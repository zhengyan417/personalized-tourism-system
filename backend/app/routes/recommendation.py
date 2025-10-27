# /backend/app/routes/recommendation.py
from flask import Blueprint, request, jsonify
import pymysql
from ..utils.database import get_connection  # 相对导入更稳

rec_bp = Blueprint("recommendations", __name__)

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
            cursor.execute("""
                SELECT id, name, category, latitude, longitude, description
                FROM attractions
                ORDER BY RAND() LIMIT %s
            """, (top_n,))
            rows = cursor.fetchall()

        recs = [{
            "attraction_id": r.get("id"),     # 映射为返回字段
            "name": r.get("name"),
            "type": r.get("category"),
            "score": 0.8,
            "reason": "基于您的历史偏好推荐" if algorithm == "content_based" else "协同过滤推荐"
        } for r in rows]

        return jsonify({"success": True, "data": {"recommendations": recs, "algorithm_used": algorithm}})
    except Exception as e:
        import traceback
        print("❌ Recommendation API Error:\n", traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


# filepath: c:\code\travel\backend\app\routes\recommendation.py
# ...existing code...
@rec_bp.route("/_debug", methods=["GET"])
def debug_db():
    """数据库自检：连接 + attractions 计数"""
    import traceback
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [list(r.values())[0] for r in cursor.fetchall()]
            count = None
            if "attractions" in tables:
                cursor.execute("SELECT COUNT(*) AS c FROM attractions;")
                count = cursor.fetchone()["c"]
        return jsonify({
            "ok": True,
            "tables": tables,
            "attractions_count": count
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()}), 500
    finally:
        if conn:
            conn.close()
# ...existing code...
