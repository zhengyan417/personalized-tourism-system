"""路线规划服务：构建景点图与最短路径搜索

功能概述：
1. 从 attractions 表加载 (attraction_id, latitude, longitude, popularity, avg_rating 等)
2. 基于地理距离构建稀疏图：仅连接距离 <= max_distance_km 的点，降低 O(n^2) 复杂度
3. 使用 Dijkstra 算法计算 start -> end 的最短路径
4. 预留扩展：权重可加入拥挤度、评分、用户偏好等因子

权重设计（当前版本）：
	weight = haversine_distance_km
后续可以扩展：
	weight = distance * (1 + congestion_factor) - attraction_bonus

接口：
	build_graph(max_distance_km=50) -> adjacency(dict[int, list[tuple[int, float]]])
	shortest_path(start_id:int, end_id:int, max_distance_km=50) -> {path: [...], distance_km: float}

错误与边界：
	- 若 start/end 不存在或缺少坐标 -> ValueError
	- 若无路径 -> 返回 path=[], distance_km=None, message 提示
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional
from math import radians, sin, cos, atan2, sqrt
from app.utils.database import get_db

# ----------------------------------
# 基础：地理距离（Haversine）
# ----------------------------------
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	R = 6371.0  # 地球半径 km
	d_lat = radians(lat2 - lat1)
	d_lon = radians(lon2 - lon1)
	a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))
	return R * c


def _load_attractions() -> List[Dict]:
	"""从数据库加载景点基础数据。兼容 attraction_id / id 主键命名。"""
	db = get_db()
	with db.cursor() as cursor:
		try:
			cursor.execute(
				"""
				SELECT attraction_id, name, latitude, longitude, popularity, avg_rating, rating_count
				FROM attractions WHERE latitude IS NOT NULL AND longitude IS NOT NULL
				"""
			)
		except Exception:
			cursor.execute(
				"""
				SELECT id AS attraction_id, name, latitude, longitude, popularity, avg_rating, rating_count
				FROM attractions WHERE latitude IS NOT NULL AND longitude IS NOT NULL
				"""
			)
		rows = cursor.fetchall()
	return rows


def build_graph(max_distance_km: float = 50.0) -> Dict[int, List[Tuple[int, float]]]:
	"""构建邻接表：{attraction_id: [(neighbor_id, weight), ...]}.

	为控制复杂度：仅在两点距离 <= max_distance_km 时添加边（无向图双向添加）。
	"""
	rows = _load_attractions()
	points = [(r["attraction_id"], r["latitude"], r["longitude"]) for r in rows]
	adj: Dict[int, List[Tuple[int, float]]] = {pid: [] for pid, _, _ in points}

	# 朴素 O(n^2) 构建；若后续点位很多，可优化为网格/球面分桶或KD树。
	n = len(points)
	for i in range(n):
		id1, lat1, lon1 = points[i]
		for j in range(i + 1, n):
			id2, lat2, lon2 = points[j]
			dist = haversine(lat1, lon1, lat2, lon2)
			if dist <= max_distance_km:
				# 无向图：双向添加
				adj[id1].append((id2, dist))
				adj[id2].append((id1, dist))
	return adj


def _dijkstra(adj: Dict[int, List[Tuple[int, float]]], start: int, end: int) -> Tuple[List[int], Optional[float]]:
	"""标准 Dijkstra（使用简单线性最小堆，节点不多时可接受）。"""
	import heapq
	dist: Dict[int, float] = {start: 0.0}
	prev: Dict[int, Optional[int]] = {start: None}
	visited = set()
	pq: List[Tuple[float, int]] = [(0.0, start)]

	while pq:
		d, u = heapq.heappop(pq)
		if u in visited:
			continue
		visited.add(u)
		if u == end:
			break
		for v, w in adj.get(u, []):
			nd = d + w
			if nd < dist.get(v, float('inf')):
				dist[v] = nd
				prev[v] = u
				heapq.heappush(pq, (nd, v))

	if end not in dist:
		return [], None

	# 回溯路径
	path = []
	cur: Optional[int] = end
	while cur is not None:
		path.append(cur)
		cur = prev.get(cur)
	path.reverse()
	return path, dist[end]


def shortest_path(start_id: int, end_id: int, max_distance_km: float = 50.0) -> Dict:
	"""对外接口：计算最短路径并返回结构化结果。"""
	rows = _load_attractions()
	id_set = {r["attraction_id"] for r in rows}
	if start_id not in id_set or end_id not in id_set:
		raise ValueError("start_id 或 end_id 不存在于景点数据中")

	adj = build_graph(max_distance_km=max_distance_km)
	path, dist_val = _dijkstra(adj, start_id, end_id)
	return {
		"path": path,
		"distance_km": round(dist_val, 3) if dist_val is not None else None,
		"nodes": len(path),
		"edge_threshold_km": max_distance_km,
		"found": bool(path),
	}


__all__ = [
	"haversine",
	"build_graph",
	"shortest_path",
	"optimize_multi_point",
    "audit_coordinates",
]

# -------------------------------------------------------------
# 多点优化路径（固定起点，其余点任意顺序）
# 场景：景点串游，起点固定，其余游览点给出推荐访问顺序（不要求回到起点）。
# 策略：
#   - 点数 m <= 10 ：使用全排列暴力搜索最优。
#   - 点数 m > 10 ：使用最近邻 + 2-opt 局部优化（近似）。
# 距离度量：直接使用 Haversine（可扩展为最短路或加权）。
# -------------------------------------------------------------
from itertools import permutations

def _pairwise_distance_matrix(ids: List[int], coord_map: Dict[int, Tuple[float,float]]) -> Dict[Tuple[int,int], float]:
	dist_map: Dict[Tuple[int,int], float] = {}
	for i in range(len(ids)):
		for j in range(i+1, len(ids)):
			a, b = ids[i], ids[j]
			(lat1, lon1) = coord_map[a]
			(lat2, lon2) = coord_map[b]
			d = haversine(lat1, lon1, lat2, lon2)
			dist_map[(a,b)] = d
			dist_map[(b,a)] = d
	return dist_map

def _route_distance(order: List[int], dist_map: Dict[Tuple[int,int], float]) -> float:
	total = 0.0
	for i in range(len(order)-1):
		total += dist_map.get((order[i], order[i+1]), 0.0)
	return total

def _nearest_neighbor(start: int, candidates: List[int], dist_map: Dict[Tuple[int,int], float]) -> List[int]:
	path = [start]
	remaining = set(candidates)
	cur = start
	while remaining:
		nxt = min(remaining, key=lambda x: dist_map.get((cur,x), float('inf')))
		path.append(nxt)
		remaining.remove(nxt)
		cur = nxt
	return path

def _two_opt(path: List[int], dist_map: Dict[Tuple[int,int], float], max_iter: int = 200) -> List[int]:
	# 2-opt 改善：尝试交换两个边，若改进则接受
	improved = True
	iter_count = 0
	while improved and iter_count < max_iter:
		improved = False
		iter_count += 1
		for i in range(1, len(path)-2):
			for j in range(i+1, len(path)-1):
				if j - i == 1:
					continue
				old_d = dist_map.get((path[i-1], path[i]), 0) + dist_map.get((path[j-1], path[j]), 0)
				new_d = dist_map.get((path[i-1], path[j-1]), 0) + dist_map.get((path[i], path[j]), 0)
				if new_d < old_d - 1e-9:
					# 反转中间段
					path[i:j] = reversed(path[i:j])
					improved = True
		# 若一轮无改进则退出
	return path

def optimize_multi_point(start_id: int, point_ids: List[int]) -> Dict:
	"""给定起点和待访问点集合，输出近似最优访问顺序（不回到起点）。

	参数：
		start_id: 固定起点
		point_ids: 其余待访问点（不含 start_id；若包含将自动去除）
	返回：dict 包含 ordered_route, total_distance_km, method, segments
	"""
	rows = _load_attractions()
	coord_map = {r["attraction_id"]: (r["latitude"], r["longitude"]) for r in rows}
	if start_id not in coord_map:
		raise ValueError("start_id 不存在")
	uniq_targets = [pid for pid in point_ids if pid != start_id and pid in coord_map]
	uniq_targets = list(dict.fromkeys(uniq_targets))  # 保留顺序去重

	all_ids = [start_id] + uniq_targets
	dist_map = _pairwise_distance_matrix(all_ids, coord_map)

	m = len(uniq_targets)
	if m == 0:
		return {
			"start": start_id,
			"points_input": point_ids,
			"ordered_route": [start_id],
			"total_distance_km": 0.0,
			"method": "trivial",
			"segments": [],
			"nodes": 1
		}

	# -------------------------------------------------------------
	# 坐标审计：检测异常范围 / 重复 / 近似整度数（疑似粗略或错误）
	# -------------------------------------------------------------
	def audit_coordinates() -> Dict:
		rows = _load_attractions()
		coord_map = {}
		issues_out_of_range = []
		issues_zero = []
		issues_near_integer = []
		duplicates = {}
		for r in rows:
			aid = r["attraction_id"]
			lat = r["latitude"]
			lon = r["longitude"]
			# 范围检查（地理全球有效 + 北京地区合理范围）
			if not (-90 <= lat <= 90 and -180 <= lon <= 180):
				issues_out_of_range.append({"id": aid, "lat": lat, "lon": lon})
			elif not (39.0 <= lat <= 41.0 and 115.0 <= lon <= 117.8):  # 粗略北京范围
				# 可归类为偏离北京区间（但可能是景点扩展区域）
				pass
			# 接近 0 或明显错误
			if abs(lat) < 0.001 or abs(lon) < 0.001:
				issues_zero.append({"id": aid, "lat": lat, "lon": lon})
			# 近整数（疑似缺少小数精度或采用简化）
			if abs(lat - round(lat)) < 1e-3 and abs(lon - round(lon)) < 1e-3:
				issues_near_integer.append({"id": aid, "lat": lat, "lon": lon})
			key = (round(lat, 4), round(lon, 4))
			duplicates.setdefault(key, []).append(aid)
		dup_list = [ {"lat": k[0], "lon": k[1], "ids": v} for k,v in duplicates.items() if len(v) > 1 ]
		return {
			"total": len(rows),
			"out_of_range": issues_out_of_range,
			"near_zero": issues_zero,
			"near_integer": issues_near_integer,
			"duplicate_coord_groups": dup_list,
		}

	if m <= 10:
		# 暴力搜索最优
		best_order = None
		best_dist = float('inf')
		for perm in permutations(uniq_targets):
			order = [start_id] + list(perm)
			d = _route_distance(order, dist_map)
			if d < best_dist:
				best_dist = d
				best_order = order
		method = "brute_force"
		final_order = best_order
		total_d = best_dist
	else:
		# 近似：最近邻 + 2-opt
		nn_order = _nearest_neighbor(start_id, uniq_targets, dist_map)
		opt_order = _two_opt(nn_order, dist_map)
		method = "heuristic+2opt"
		final_order = opt_order
		total_d = _route_distance(final_order, dist_map)

	# 构造分段详情
	segments = []
	for i in range(len(final_order)-1):
		a, b = final_order[i], final_order[i+1]
		segments.append({
			"from": a,
			"to": b,
			"distance_km": round(dist_map.get((a,b), 0.0), 4)
		})

	return {
		"start": start_id,
		"points_input": point_ids,
		"ordered_route": final_order,
		"total_distance_km": round(total_d, 4),
		"method": method,
		"segments": segments,
		"nodes": len(final_order)
	}

