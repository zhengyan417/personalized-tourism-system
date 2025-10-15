# /backend/app/routes/travel_diary.py
from flask import Blueprint, request, jsonify
from backend.app.utils.database import get_db

diary_bp = Blueprint('diaries', __name__)

@diary_bp.route('', methods=['GET'])
def list_diaries():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT diary_id, title, create_time FROM diaries WHERE user_id=%s", (user_id,))
    data = cursor.fetchall()
    return jsonify({"status": "success", "count": len(data), "data": data})
