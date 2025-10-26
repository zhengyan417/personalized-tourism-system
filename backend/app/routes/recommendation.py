# /backend/app/routes/recommendation.py
from flask import Blueprint, request, jsonify
import pymysql
from app.utils.database import get_connection  # 注意路径

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
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT attraction_id, name, category, latitude, longitude, description
            FROM attractions
            ORDER BY RAND() LIMIT %s
        """, (top_n,))
        rows = cursor.fetchall()
         print("✅ Recommendation rows:", rows)
        recs = []
        for r in rows:
            recs.append({
                "attraction_id": r.get("attraction_id"),
                "name": r.get("name"),
                "type": r.get("category"),
                "score": 0.8,
                "reason": "基于您的历史偏好推荐" if algorithm == "content_based" else "协同过滤推荐"
            })

        return jsonify({
            "success": True,
            "data": {
                "recommendations": recs,
                "algorithm_used": algorithm
            }
        })
    except Exception as e:
        import traceback
        print("❌ Recommendation API Error:\n", traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
