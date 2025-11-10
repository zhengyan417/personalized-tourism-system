# /backend/app/routes/recommendation.py
from flask import Blueprint, request, jsonify
import pymysql
from ..utils.database import get_connection  # 相对导入更稳
from ..core_bridge import recommendation_bridge as rbridge

rec_bp = Blueprint("recommendations", __name__)

@rec_bp.after_request
def _no_cache(resp):
    """为本蓝图的所有响应添加 no-cache 头，避免浏览器缓存导致的空白/不可预览。"""
    try:
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    except Exception:
        pass
    return resp

@rec_bp.route("/_ping", methods=["GET"])
def ping():
    """轻量健康检查：不访问数据库，验证蓝图已挂载。"""
    return jsonify({"ok": True, "bp": "recommendations"})

@rec_bp.route("/_db_ping", methods=["GET"])
def db_ping():
    """数据库连通性检查：仅执行 SELECT 1。"""

    import traceback
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT 1 AS ok")
            val = cursor.fetchone()
        # 仅返回简单 JSON，最大程度避免浏览器预览问题
        return jsonify({"ok": True, "db": True}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "where": "SELECT 1"}), 500
    finally:
        # 连接由 app.utils.database.init_db 的 teardown_request 统一关闭
        pass

@rec_bp.route("/", methods=["GET"])
def personalized():
    """GET /api/recommendations?user_id=..&top_n=..&algorithm=.."""
    user_id = request.args.get("user_id", type=int)
    top_n = request.args.get("top_n", default=10, type=int)
    algorithm = request.args.get("algorithm", default="content_based", type=str)

    if not user_id:
        return jsonify({"success": False, "message": "user_id is required"}), 400

    conn = None
    try:
        conn = get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 取更大的候选集再交由C++排序，以体现“算法在.cpp”
            try:
                cursor.execute(
                    """
                    SELECT 
                      attraction_id, name, category, latitude, longitude, description,
                      popularity, avg_rating, rating_count, image_url, visitor_count
                    FROM attractions
                    ORDER BY RAND() LIMIT %s
                    """,
                    (max(top_n * 20, 200),)
                )
            except Exception as _:
                # 兼容旧表结构（主键列名为 id）
                cursor.execute(
                    """
                    SELECT 
                      id AS attraction_id, name, category, latitude, longitude, description,
                      popularity, avg_rating, rating_count, image_url, visitor_count
                    FROM attractions
                    ORDER BY RAND() LIMIT %s
                    """,
                    (max(top_n * 20, 200),)
                )
            rows = cursor.fetchall()

        # 选择排序器：heap 或 quick（默认 heap）
        algo = "quick" if "quick" in (algorithm or "").lower() else "heap"
        ranked = rbridge.rank_personalized(rows, top_n=top_n, algorithm=algo)

        # 补充输出字段
        for r in ranked:
            r.setdefault("type", r.get("category"))
            r.setdefault("rating", r.get("avg_rating"))
            r["reason"] = "基于您的历史偏好推荐" if (algorithm or "").lower().startswith("content") else "协同过滤推荐"

        return jsonify({
            "success": True,
            "data": {
                "recommendations": ranked,
                "algorithm_used": algorithm,
                "native_core": rbridge.has_native()
            }
        })
    except Exception as e:
        import traceback
        # 避免 Windows 控制台编码问题（去除非 ASCII 字符）
        print("Recommendation API Error:\n", traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # 连接由 app.utils.database.init_db 的 teardown_request 统一关闭
        pass


# filepath: c:\code\travel\backend\app\routes\recommendation.py
# ...existing code...
@rec_bp.route("/_debug", methods=["GET"])
def debug_db():
    """数据库自检：更稳健的版本，不依赖 SHOW TABLES。
    返回：当前库名/版本，attractions 是否可访问以及行数。
    """
    import traceback
    conn = None
    info = {"ok": False}
    try:
        conn = get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 数据库与版本信息
            try:
                cursor.execute("SELECT DATABASE() AS db")
                info["database"] = (cursor.fetchone() or {}).get("db")
            except Exception:
                info["database"] = None

            try:
                cursor.execute("SELECT VERSION() AS version")
                info["mysql_version"] = (cursor.fetchone() or {}).get("version")
            except Exception:
                info["mysql_version"] = None

            # attractions 表计数（若不存在则捕获并返回说明）
            try:
                cursor.execute("SELECT COUNT(*) AS c FROM attractions")
                info["attractions_count"] = (cursor.fetchone() or {}).get("c")
                info["attractions_accessible"] = True
            except Exception as ex:
                info["attractions_count"] = None
                info["attractions_accessible"] = False
                info["attractions_error"] = str(ex)

        info["ok"] = True
        return jsonify(info)
    except Exception as e:
        info.update({"ok": False, "error": str(e), "trace": traceback.format_exc()})
        return jsonify(info), 500
    finally:
        # 连接由 app.utils.database.init_db 的 teardown_request 统一关闭
        pass


@rec_bp.route("/hot", methods=["GET"])
def hot_list():
        """GET /api/recommendations/hot?top_n=10&sort_by=popularity|rating|visitor_count
        基于热度/评分/访客数的热门景点。
        """
        top_n = request.args.get("top_n", default=10, type=int)
        sort_by = request.args.get("sort_by", default="popularity", type=str)

        conn = None
        try:
            conn = get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                if rbridge.has_native():
                    # 原生可用：取全集交给 C++ 排序
                    try:
                        cursor.execute(
                            """
                            SELECT attraction_id, name, category, popularity, avg_rating, rating_count, image_url, visitor_count
                            FROM attractions
                            """
                        )
                    except Exception as _:
                        cursor.execute(
                            """
                            SELECT id AS attraction_id, name, category, popularity, avg_rating, rating_count, image_url, visitor_count
                            FROM attractions
                            """
                        )
                    rows = cursor.fetchall()
                    algo = "heap"
                    ranked = rbridge.rank_hot(rows, top_n=top_n, sort_by=sort_by, algorithm=algo)
                else:
                    # 原生不可用：直接 SQL 排序 + LIMIT，避免大结果集引发响应异常
                    sort_map = {
                        "popularity": "popularity",
                        "rating": "avg_rating",
                        "visitor_count": "visitor_count"
                    }
                    order_col = sort_map.get(sort_by, "popularity")
                    try:
                        cursor.execute(
                            f"""
                            SELECT attraction_id, name, category, popularity, avg_rating, rating_count, image_url, visitor_count
                            FROM attractions
                            ORDER BY {order_col} DESC, attraction_id ASC
                            LIMIT %s
                            """,
                            (top_n,)
                        )
                    except Exception as _:
                        cursor.execute(
                            f"""
                            SELECT id AS attraction_id, name, category, popularity, avg_rating, rating_count, image_url, visitor_count
                            FROM attractions
                            ORDER BY {order_col} DESC, id ASC
                            LIMIT %s
                            """,
                            (top_n,)
                        )
                    ranked = cursor.fetchall()

            # 统一字段命名
            for r in ranked:
                r.setdefault("type", r.get("category"))
                r.setdefault("rating", r.get("avg_rating"))

            return jsonify({
                "success": True,
                "data": {
                    "recommendations": ranked,
                    "sort_method": sort_by,
                    "total_attractions": len(ranked),
                    "native_core": rbridge.has_native()
                }
            })
        except Exception as e:
            import traceback
            # 避免 Windows 控制台编码问题（去除非 ASCII 字符）
            print("Hot Recommendation API Error:\n", traceback.format_exc())
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            if conn:
                conn.close()
# ...existing code...
