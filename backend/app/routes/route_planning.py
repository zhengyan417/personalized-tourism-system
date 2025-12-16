from flask import Blueprint, request, jsonify
from app.services import route_service
from app.services import navigate_service  # 新增道路导航服务

route_bp = Blueprint("routes", __name__)

# CORS 由全局 CORS(app) 统一处理，支持 credentials
# @route_bp.after_request
# def _cors_fix(resp):
#     # 不再手动设置 CORS 头，避免与全局配置冲突
#     return resp

@route_bp.route('/_ping', methods=['GET'])
def ping_routes():
    return jsonify({'ok': True, 'bp': 'routes'})

@route_bp.route("/plan", methods=["GET", "POST"])
def plan_route():
    """简易路线规划（顺序拼接）：支持 GET/POST，仍保留作为演示。"""
    if request.method == "GET":
        start = request.args.get("start")
        end = request.args.get("end")
        wp = request.args.getlist("waypoints")
        if len(wp) == 1 and wp[0] and "," in wp[0]:
            waypoints = [w for w in wp[0].split(",") if w]
        else:
            waypoints = wp
    else:
        data = request.get_json(silent=True) or {}
        start = data.get("start") or request.form.get("start")
        end = data.get("end") or request.form.get("end")
        if isinstance(data.get("waypoints"), list):
            waypoints = data["waypoints"]
        else:
            wp_multi = request.form.getlist("waypoints")
            if wp_multi:
                waypoints = wp_multi
            else:
                s = request.form.get("waypoints", "")
                waypoints = [w for w in s.split(",") if w] if s else []

    if not start or not end:
        return jsonify({"status": "error", "message": "start 和 end 必填"}), 400

    route = [start] + waypoints + [end]
    total_distance = len(route) * 2.5  # 仍保留模拟距离
    return jsonify({
        "status": "success",
        "message": "顺序拼接路线成功 (演示)",
        "route": route,
        "distance_km": total_distance
    })


@route_bp.route("/shortest", methods=["GET"])
def shortest_route():
    """计算两个景点之间的最短路径（Dijkstra）。

    请求参数：
        start_id: 起点景点ID
        end_id: 终点景点ID
        max_distance_km: 构边距离阈值（可选，默认50）
    """
    start_id = request.args.get("start_id", type=int)
    end_id = request.args.get("end_id", type=int)
    max_dist = request.args.get("max_distance_km", default=50.0, type=float)

    if not start_id or not end_id:
        return jsonify({"status": "error", "message": "start_id 与 end_id 必填"}), 400

    try:
        result = route_service.shortest_path(start_id, end_id, max_distance_km=max_dist)
        if not result["found"]:
            return jsonify({
                "status": "error",
                "message": "未找到路径，请调大 max_distance_km 或检查坐标数据",
                "data": result
            }), 404
        return jsonify({
            "status": "success",
            "message": "最短路径计算成功",
            "data": result
        })
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@route_bp.route("/navigate", methods=["GET"])
def navigate_route():
    """真实道路导航：调用外部道路服务 (OSRM) 获取可行路线几何。

    请求参数：
        start_lat, start_lon, end_lat, end_lon
        waypoints（可选，格式："lat,lon;lat,lon" 或多次 ?waypoints=lat,lon）
        profile（可选：driving|walking|cycling，默认 driving）
    返回：道路坐标序列、距离(km)、耗时(分钟)、使用服务与降级标记。
    """
    start_lat = request.args.get("start_lat", type=float)
    start_lon = request.args.get("start_lon", type=float)
    end_lat = request.args.get("end_lat", type=float)
    end_lon = request.args.get("end_lon", type=float)
    profile = request.args.get("profile", default="driving", type=str)
    # 统一使用 OSRM 作为导航提供商；前端传入的 provider 将被忽略（保持向后兼容字段）。
    provider = request.args.get("provider", default="osrm", type=str)

    raw_wp_list = request.args.getlist("waypoints")
    waypoints = []
    for item in raw_wp_list:
        parts = [p.strip() for p in item.split(";") if p.strip()]
        for seg in parts:
            if "," in seg:
                lat_s, lon_s = seg.split(",", 1)
                try:
                    waypoints.append((float(lat_s), float(lon_s)))
                except ValueError:
                    pass

    if None in (start_lat, start_lon, end_lat, end_lon):
        return jsonify({"status": "error", "message": "start/end 坐标缺失"}), 400

    provider = (provider or "auto").lower()
    errors = {}
    data = None
    selected_provider = "osrm"

    # 统一 OSRM：直接调用 OSRM，忽略 AMap 分支与自动降级逻辑。
    try:
        data = navigate_service.fetch_osrm_route(
            start=(start_lat, start_lon),
            end=(end_lat, end_lon),
            waypoints=waypoints,
            profile=profile,
        )
    except Exception as osrm_err:
        errors['osrm'] = str(osrm_err)
        return jsonify({
            "status": "error",
            "message": f"导航服务不可用: {osrm_err}",
            "errors": errors
        }), 502

    if errors:
        data.setdefault('fallback', errors)
    data['provider'] = selected_provider

    code = 200 if data.get('road_path') else 502
    resp = jsonify({
        "status": "success" if code == 200 else "error",
        "message": data.get("message", "OK"),
        "data": data
    })
    return resp, code


@route_bp.route("/optimize", methods=["GET"])
def optimize_multi_point():
    """多点优化路径（固定起点 + 待访问点集合，不回起点）

    请求参数：
        start_id: 起点
        point_ids: 逗号分隔的景点ID列表（不含起点；若含起点将自动去除）
    返回：
        ordered_route: 顺序（含起点）
        total_distance_km: 总距离（Haversine 近似）
        method: brute_force | heuristic+2opt | trivial
        segments: 每一段的距离
    """
    start_id = request.args.get("start_id", type=int)
    raw_points = request.args.get("point_ids", default="", type=str)
    if not start_id:
        return jsonify({"status": "error", "message": "start_id 必填"}), 400
    point_ids = []
    for part in raw_points.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            pid = int(part)
            point_ids.append(pid)
        except ValueError:
            pass
    try:
        result = route_service.optimize_multi_point(start_id, point_ids)
        return jsonify({
            "status": "success",
            "message": "多点优化完成",
            "data": result
        })
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@route_bp.route('/coords_audit', methods=['GET'])
def coords_audit():
    """坐标数据审计：返回潜在异常（重复坐标、近整数等）。"""
    try:
        result = route_service.audit_coordinates()
        return jsonify({
            'status': 'success',
            'message': '坐标审计完成',
            'data': result
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500