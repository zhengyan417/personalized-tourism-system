"""
通用工具：数据去重等。

当前主要提供对查询结果（list[dict]）的去重功能，
支持优先使用主键/唯一键（如 attraction_id 或 id），
否则回退到 name + (latitude, longitude) 的组合键；
若仍无法构造键，则使用条目内容散列作为兜底。
"""

from __future__ import annotations

from typing import Iterable, List, Dict, Sequence, Tuple, Optional, Any


def _norm_str(v: Any) -> str:
	if v is None:
		return ""
	s = str(v)
	return s.strip().casefold()


def _round_num(v: Any, digits: int = 6) -> Optional[float]:
	try:
		return round(float(v), digits)
	except (TypeError, ValueError):
		return None


def deduplicate_records(
	rows: Iterable[Dict[str, Any]],
	keys: Sequence[str] = ("attraction_id", "id"),
	*,
	use_name_and_coords_fallback: bool = True,
	lat_key: str = "latitude",
	lon_key: str = "longitude",
	coord_precision: int = 6,
) -> List[Dict[str, Any]]:
	"""
	对 list[dict] 进行去重。

	规则顺序：
	1) 优先按 keys 中第一个存在于记录的键作为唯一键（例如 attraction_id 或 id）。
	2) 若没有上述键且启用回退，则按 (name, round(latitude, p), round(longitude, p)) 去重。
	3) 若仍无法构造键，则对条目内容进行不可逆摘要（转为冻结键值对元组），用于兜底去重。

	返回：保持首次出现顺序的去重列表。
	"""
	seen: set = set()
	out: List[Dict[str, Any]] = []

	for r in rows:
		if not isinstance(r, dict):
			# 非字典条目，直接跳过或也可加入；这里保守：跳过
			continue

		dedup_key: Optional[Tuple[Any, ...]] = None

		# 1) 主键/唯一键
		for k in keys:
			if k in r and r[k] is not None:
				dedup_key = (k, r[k])
				break

		# 2) name + 坐标 回退
		if dedup_key is None and use_name_and_coords_fallback:
			name = _norm_str(r.get("name")) or _norm_str(r.get("title"))
			lat = _round_num(r.get(lat_key), coord_precision)
			lon = _round_num(r.get(lon_key), coord_precision)
			if name and lat is not None and lon is not None:
				dedup_key = ("name@coord", name, lat, lon)

		# 3) 全量摘要兜底（稳定但可能较长）
		if dedup_key is None:
			try:
				dedup_key = tuple(sorted(r.items()))  # type: ignore[arg-type]
			except Exception:
				dedup_key = (id(r),)

		if dedup_key in seen:
			continue
		seen.add(dedup_key)
		out.append(r)

	return out


def deduplicate_by_description(
	rows: Iterable[Dict[str, Any]],
	description_key: str = "description",
	*,
	ignore_empty: bool = True,
) -> List[Dict[str, Any]]:
	"""
	基于描述字段去重：相同 description 视为同一地点的重复记录。

	- 默认忽略空/缺失描述（不据此合并，避免把大量空描述合并为一条）。
	- 保持首次出现顺序。
	"""
	seen: set = set()
	out: List[Dict[str, Any]] = []

	for r in rows:
		if not isinstance(r, dict):
			continue
		desc_raw = r.get(description_key)
		desc_norm = _norm_str(desc_raw)
		use_desc = bool(desc_norm)
		if not use_desc and ignore_empty:
			# 不使用空描述作为去重键，直接按原样追加（后续可能被其他规则再去重）
			out.append(r)
			continue

		if desc_norm in seen:
			continue
		seen.add(desc_norm)
		out.append(r)

	return out

