"""道路导航服务：调用 OSRM 公共路由接口获取真实道路路径。

注意：
- 默认使用 OSRM 官方 demo 服务器 (router.project-osrm.org)，不保证高可用/速度。
- 若请求失败或超时，自动降级为两点直线 polyline，仍返回距离估算。
- 可扩展：部署自有 OSRM/GraphHopper/Valhalla 服务，或接入高德/百度官方 Web API。

API 参考：
GET https://router.project-osrm.org/route/v1/{profile}/{lon},{lat};{lon},{lat}?overview=full&geometries=geojson

返回字段：
    road_path: [[lat, lon], ...]  # 真实道路折线
    distance_km: float            # 总距离 km
    duration_min: float           # 预计耗时 分钟
    profile: str                  # 使用的出行模式
    degraded: bool                # 是否为降级（true 表示没有真实道路，仅直线）
    waypoints_used: int           # 使用的中间点数量
    steps_detail: [ {index, instruction, distance_km, duration_min, from:[lat,lon], to:[lat,lon]} ] # 分步骤导航
"""
from __future__ import annotations

import os
from math import radians, sin, cos, atan2, sqrt
from typing import Dict, List, Optional, Tuple

import requests

try:
    from flask import current_app
except ImportError:  # pragma: no cover
    current_app = None  # type: ignore


OSRM_BASE_DEFAULT = "https://router.project-osrm.org"
OSRM_DEFAULT_TIMEOUT = 8  # 秒

AMAP_BASE_URL = "https://restapi.amap.com"
AMAP_TIMEOUT = 6

AMAP_ENDPOINTS = {
    "driving": "/v5/direction/driving",
    "walking": "/v5/direction/walking",
    "cycling": "/v5/direction/bicycling",
}


def _get_setting(name: str, default=None):
    """从 Flask 配置或环境变量读取设置。"""
    if current_app is not None:
        try:
            value = current_app.config.get(name)
            if value is not None:
                return value
        except RuntimeError:
            # 应用上下文未准备好，退回环境变量
            pass
    return os.getenv(name, default)



def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(d_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def _parse_amap_polyline(polyline: str) -> List[List[float]]:
    points: List[List[float]] = []
    if not polyline:
        return points
    for item in polyline.split(';'):
        item = item.strip()
        if not item or ',' not in item:
            continue
        lon_str, lat_str = item.split(',', 1)
        try:
            lon = float(lon_str)
            lat = float(lat_str)
        except ValueError:
            continue
        points.append([lat, lon])
    return points


def _extend_path(base: List[List[float]], fragment: List[List[float]]):
    if not fragment:
        return
    if not base:
        base.extend(fragment)
    else:
        if base[-1] == fragment[0]:
            base.extend(fragment[1:])
        else:
            base.extend(fragment)


def fetch_osrm_route(
    start: Tuple[float, float],
    end: Tuple[float, float],
    waypoints: Optional[List[Tuple[float, float]]] = None,
    profile: str = "driving",
) -> Dict:
    """调用 OSRM 获取道路路线；失败时降级为直线。"""
    waypoints = waypoints or []
    latlon_all = [start] + waypoints + [end]

    # 构造坐标串："lon,lat;lon,lat;..." OSRM 要求经度在前
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in latlon_all)
    osrm_base = _get_setting('OSRM_BASE_URL', OSRM_BASE_DEFAULT)
    url = f"{osrm_base}/route/v1/{profile}/{coord_str}"
    timeout = float(_get_setting('OSRM_TIMEOUT', OSRM_DEFAULT_TIMEOUT))
    params = {
        "overview": "full",          # 完整几何（更精细）
        "geometries": "geojson",     # 直接使用 geojson 坐标
        "alternatives": "false",     # 不需要多条候选
        "steps": "true",             # 返回每段步骤，便于后续细化/提示
        "annotations": "distance,duration,speed"  # 获取距离/耗时/速度注解
    }

    try:
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"OSRM status {resp.status_code}")
        data = resp.json()
        routes = data.get("routes") or []
        if not routes:
            raise RuntimeError("OSRM 返回空 routes")
        best = routes[0]
        geometry = best.get("geometry", {})
        coords = geometry.get("coordinates") or []  # [[lon,lat],...]
        # 转为 [[lat, lon], ...]
        road_path = [[lat, lon] for lon, lat in coords]
        distance_km = (best.get("distance", 0.0) or 0.0) / 1000.0
        duration_min = (best.get("duration", 0.0) or 0.0) / 60.0
        steps_raw = best.get("legs", [])
        steps_detail = []
        idx_counter = 0
        def _zh_type(t: str) -> str:
            mapping = {
                'depart': '出发', 'arrive': '到达', 'turn': '转向', 'merge': '并入', 'ramp': '驶入匝道',
                'fork': '岔路', 'roundabout': '环岛', 'end of road': '道路结束', 'continue': '继续直行',
                'new name': '进入', 'exit roundabout': '离开环岛', 'exit rotary': '离开环岛'
            }
            return mapping.get(t, t or '')
        def _zh_modifier(m: str) -> str:
            mapping = {
                'left': '左转', 'right': '右转', 'slight left': '稍向左', 'slight right': '稍向右',
                'straight': '直行', 'uturn': '掉头'
            }
            return mapping.get(m, m or '')
        for leg in steps_raw or []:
            for st in leg.get('steps', []):
                maneuver = st.get('maneuver', {}) or {}
                m_type = _zh_type(maneuver.get('type', ''))
                m_mod = _zh_modifier(maneuver.get('modifier', ''))
                name = st.get('name') or ''
                dist_m = st.get('distance', 0.0)
                dur_s = st.get('duration', 0.0)
                from_lon, from_lat = maneuver.get('location', [None, None])
                locs = st.get('intersections', [])
                to_lat = to_lon = None
                if locs:
                    last_loc = locs[-1].get('location') or []
                    if len(last_loc) == 2:
                        to_lon, to_lat = last_loc
                # 指令拼接
                parts = [p for p in [m_type, m_mod, name] if p]
                instruction = '，'.join(parts) if parts else '前进'
                steps_detail.append({
                    'index': idx_counter,
                    'instruction': instruction,
                    'distance_km': round(dist_m/1000.0, 3),
                    'duration_min': round(dur_s/60.0, 2),
                    'from': [from_lat, from_lon],
                    'to': [to_lat, to_lon]
                })
                idx_counter += 1
        return {
            "road_path": road_path,
            "distance_km": round(distance_km, 3),
            "duration_min": round(duration_min, 2),
            "profile": profile,
            "provider": "osrm",
            "degraded": False,
            "waypoints_used": len(waypoints),
            "steps": idx_counter,
            "steps_detail": steps_detail,
            "message": "OK"
        }
    except Exception as e:
        # 降级：使用起终点直线，估算距离
        dist = _haversine(start[0], start[1], end[0], end[1])
        return {
            "road_path": [list(start), list(end)],
            "distance_km": round(dist, 3),
            "duration_min": None,
            "profile": profile,
            "provider": "osrm",
            "degraded": True,
            "waypoints_used": len(waypoints),
            "steps": 0,
            "steps_detail": [],
            "message": f"degraded: {e}"[:180]
        }


def fetch_amap_route(
    start: Tuple[float, float],
    end: Tuple[float, float],
    waypoints: Optional[List[Tuple[float, float]]] = None,
    profile: str = "driving",
) -> Dict:
    key = _get_setting('AMAP_API_KEY')
    if not key:
        raise RuntimeError('AMAP_API_KEY 未配置')

    waypoints = waypoints or []
    profile = profile or 'driving'
    endpoint = AMAP_ENDPOINTS.get(profile, AMAP_ENDPOINTS['driving'])
    url = f"{AMAP_BASE_URL}{endpoint}"

    params = {
        'key': key,
        'origin': f"{start[1]},{start[0]}",
        'destination': f"{end[1]},{end[0]}",
    }

    if profile == 'driving':
        params['extensions'] = 'all'
        params.setdefault('strategy', '0')

    if waypoints:
        wp = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
        params['waypoints'] = wp

    timeout = float(_get_setting('AMAP_TIMEOUT', AMAP_TIMEOUT))
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get('status') != '1':
        raise RuntimeError(f"AMap error: {data.get('info')} ({data.get('infocode')})")

    route = data.get('route') or {}
    paths = route.get('paths') or []
    if not paths:
        raise RuntimeError('AMap 未返回路径数据')

    best = paths[0]
    try:
        distance_km = float(best.get('distance', 0.0)) / 1000.0
    except (TypeError, ValueError):
        distance_km = 0.0
    try:
        duration_min = float(best.get('duration', 0.0)) / 60.0
    except (TypeError, ValueError):
        duration_min = None

    steps = best.get('steps') or []
    road_path: List[List[float]] = []
    steps_detail = []

    for idx, step in enumerate(steps):
        pts = _parse_amap_polyline(step.get('polyline', ''))
        _extend_path(road_path, pts)
        try:
            step_dist = float(step.get('distance', 0.0)) / 1000.0
        except (TypeError, ValueError):
            step_dist = 0.0
        try:
            step_dur = float(step.get('duration', 0.0)) / 60.0
        except (TypeError, ValueError):
            step_dur = None

        instruction_parts = [step.get('instruction') or '', step.get('road') or '']
        instruction = ' '.join(p for p in instruction_parts if p).strip() or '前进'
        steps_detail.append({
            'index': idx,
            'instruction': instruction,
            'distance_km': round(step_dist, 3),
            'duration_min': round(step_dur, 2) if step_dur is not None else None,
            'from': pts[0] if pts else [None, None],
            'to': pts[-1] if pts else [None, None],
        })

    if not road_path:
        path_polyline = best.get('polyline')
        poly_points = _parse_amap_polyline(path_polyline or '')
        if poly_points:
            road_path = poly_points
    if not road_path:
        road_path = [list(start), list(end)]

    return {
        'road_path': road_path,
        'distance_km': round(distance_km, 3),
        'duration_min': round(duration_min, 2) if duration_min is not None else None,
        'profile': profile,
        'degraded': False,
        'provider': 'amap',
        'waypoints_used': len(waypoints),
        'steps': len(steps_detail),
        'steps_detail': steps_detail,
        'message': 'OK'
    }

__all__ = ["fetch_osrm_route", "fetch_amap_route"]
