"""
Bridge between Flask routes and C++ core (pybind11) recommendation module.

This module tries to import the compiled extension `recommendation_core` and
provides simple helpers to:
- rank personalized recommendations (content-based default)
- rank hot lists by popularity/rating/visitor_count

If the native module isn't available, it falls back to pure-Python sorting so
API endpoints still work.
"""
from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional

try:
	import recommendation_core as rc  # type: ignore
	HAS_NATIVE = True
except Exception:  # pragma: no cover - safe fallback
	rc = None  # type: ignore
	HAS_NATIVE = False


# -----------------------------
# Internal: conversions
# -----------------------------
def _row_to_rc_item(row: Dict):
	"""Convert DB row (dict) to rc.RecommendationItem.

	Expected row keys: attraction_id (or id), name, category, popularity,
	avg_rating, rating_count, visitor_count, image_url, score (optional).
	"""
	item = rc.RecommendationItem() if HAS_NATIVE else None  # type: ignore
	if HAS_NATIVE:
		item.attraction_id = row.get("attraction_id") or row.get("id")
		item.name = row.get("name") or ""
		item.type = row.get("category") or row.get("type") or ""
		# score is optional; comparators may use different fields
		item.score = float(row.get("score") or 0.0)
		item.popularity = _to_float(row.get("popularity"))
		# rating in API maps to avg_rating in DB
		item.rating = _to_float(row.get("avg_rating") or row.get("rating"))
	return item


def _to_float(v) -> float:
	try:
		return float(v) if v is not None else 0.0
	except Exception:
		return 0.0


# -----------------------------
# Public helpers (native-first)
# -----------------------------
def rank_personalized(
	rows: Iterable[Dict],
	top_n: int = 10,
	algorithm: str = "heap",  # heap | quick
	score_fn: Optional[Callable[[Dict], float]] = None,
) -> List[Dict]:
	"""Rank items for personalized recommendation using native sorter.

	- algorithm: 'heap' uses heap_sort_top_n, 'quick' uses quick_select_top_n
	- score_fn: optional Python function to compute row['score'] before sort

	Returns list of original dict rows (with 'score' added when available),
	sorted in descending order.
	"""
	rows_list = list(rows)

	# Compute score if requested (e.g., content-based pre-score)
	if score_fn is not None:
		for r in rows_list:
			try:
				r["score"] = float(score_fn(r))
			except Exception:
				r["score"] = 0.0
	else:
		# default heuristic: weighted rating+popularity
		for r in rows_list:
			rating = _to_float(r.get("avg_rating") or r.get("rating"))
			popularity = _to_float(r.get("popularity"))
			r["score"] = 0.6 * rating + 0.4 * popularity

	if not HAS_NATIVE:
		# Python fallback: sort by score desc
		rows_list.sort(key=lambda x: x.get("score") or 0.0, reverse=True)
		return rows_list[: max(0, top_n)]

	items = [_row_to_rc_item(r) for r in rows_list]

	comparator = rc.content_based_comparator  # type: ignore[attr-defined]
	if algorithm == "quick":
		ranked = rc.quick_select_top_n(items, int(top_n), comparator)  # type: ignore[attr-defined]
	else:
		ranked = rc.heap_sort_top_n(items, int(top_n), comparator)  # type: ignore[attr-defined]

	# Build id set for fast lookup
	id_set = {it.attraction_id for it in ranked}
	# Keep original dicts with same order as ranked
	ranked_map = {it.attraction_id: it for it in ranked}

	# Create a mapping from id->row and update with back-propagated score
	row_map = { (r.get("attraction_id") or r.get("id")): r for r in rows_list }

	out: List[Dict] = []
	for aid in [it.attraction_id for it in ranked]:
		r = dict(row_map.get(aid) or {})
		# ensure fields present
		r.setdefault("rating", r.get("avg_rating"))
		# ensure score reflects C++ item.score if set
		try:
			r["score"] = float(getattr(ranked_map[aid], "score", r.get("score", 0.0)))
		except Exception:
			pass
		out.append(r)
	return out


def rank_hot(
	rows: Iterable[Dict],
	top_n: int = 10,
	sort_by: str = "popularity",  # popularity | rating | visitor_count
	algorithm: str = "heap",      # heap | quick
) -> List[Dict]:
	"""Rank hot items using native comparators when available.

	- popularity -> rc.popularity_comparator
	- rating -> rc.rating_comparator
	- visitor_count -> Python comparator bridged to native sorter
	"""
	rows_list = list(rows)

	if not rows_list:
		return []

	if not HAS_NATIVE:
		key_map = {
			"popularity": lambda r: _to_float(r.get("popularity")),
			"rating": lambda r: _to_float(r.get("avg_rating") or r.get("rating")),
			"visitor_count": lambda r: float(r.get("visitor_count") or 0.0),
		}
		key = key_map.get(sort_by, key_map["popularity"]) 
		rows_list.sort(key=key, reverse=True)
		return rows_list[: max(0, top_n)]

	# Native path
	items = [_row_to_rc_item(r) for r in rows_list]

	# Choose comparator: use native when exists, else Python comparator
	if sort_by == "rating":
		comparator = rc.rating_comparator  # type: ignore[attr-defined]
	elif sort_by == "popularity":
		comparator = rc.popularity_comparator  # type: ignore[attr-defined]
	else:
		# Bridge a Python comparator for visitor_count using score channel
		def py_cmp(a, b):  # type: ignore[no-redef]
			# Desc order by score
			return (getattr(a, "score", 0.0) or 0.0) > (getattr(b, "score", 0.0) or 0.0)

		# We don't have visitor_count field in RecommendationItem; encode into score
		for r in rows_list:
			r["score"] = float(r.get("visitor_count") or 0.0)
		items = [_row_to_rc_item(r) for r in rows_list]
		comparator = py_cmp

	if algorithm == "quick":
		ranked = rc.quick_select_top_n(items, int(top_n), comparator)  # type: ignore[attr-defined]
	else:
		ranked = rc.heap_sort_top_n(items, int(top_n), comparator)  # type: ignore[attr-defined]

	# Map back to dicts preserving ranked order
	row_map = { (r.get("attraction_id") or r.get("id")): r for r in rows_list }
	out: List[Dict] = []
	for it in ranked:
		rid = getattr(it, "attraction_id", None)
		r = dict(row_map.get(rid) or {})
		r.setdefault("rating", r.get("avg_rating"))
		out.append(r)
	return out


def has_native() -> bool:
	"""Whether native module is available."""
	return HAS_NATIVE

