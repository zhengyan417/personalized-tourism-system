# 文件路径：backend/app/routes/travel_diary.py
# 模块功能：旅游日记 CRUD + 内容压缩
# 模块负责人：C 同学

from flask import Blueprint, request, jsonify
from app.utils.database import get_db
import zlib  # 压缩与解压
import base64

diary_bp = Blueprint('diary', __name__)

# ==========================================
# 辅助函数：压缩 / 解压内容
# ==========================================
def compress_content(text):
    if not text:
        return None
    compressed = zlib.compress(text.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')  # 以文本形式存储

def decompress_content(encoded):
    if not encoded:
        return ""
    try:
        compressed = base64.b64decode(encoded.encode('utf-8'))
        return zlib.decompress(compressed).decode('utf-8')
    except Exception:
        return "[内容解压失败]"


# ==========================================
# 1️⃣ 创建日记
# ==========================================
@diary_bp.route('/create', methods=['POST'])
def create_diary():
    data = request.get_json()
    user_id = data.get('user_id')
    attraction_id = data.get('attraction_id')
    title = data.get('title')
    content = data.get('content')

    if not user_id or not content:
        return jsonify({"status": "error", "message": "user_id 和 content 不能为空"}), 400

    compressed = compress_content(content)
    db = get_db()
    with db.cursor() as cursor:
        sql = """
            INSERT INTO diaries (user_id, attraction_id, title, content)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, attraction_id, title, compressed))
        db.commit()

    return jsonify({"status": "success", "message": "日记创建成功"})


# ==========================================
# 2️⃣ 获取某用户的全部日记
# ==========================================
@diary_bp.route('/', methods=['GET'])
def list_diaries():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "缺少 user_id 参数"}), 400

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT diary_id, attraction_id, title, content, create_time FROM diaries WHERE user_id=%s ORDER BY create_time DESC",
            (user_id,)
        )
        diaries = cursor.fetchall()

    for d in diaries:
        d["content"] = decompress_content(d["content"])

    return jsonify({"status": "success", "count": len(diaries), "data": diaries})


# ==========================================
# 3️⃣ 查看单篇日记
# ==========================================
@diary_bp.route('/<int:diary_id>', methods=['GET'])
def get_diary(diary_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT diary_id, user_id, attraction_id, title, content, create_time FROM diaries WHERE diary_id=%s",
            (diary_id,)
        )
        diary = cursor.fetchone()
    if not diary:
        return jsonify({"status": "error", "message": "日记不存在"}), 404

    diary["content"] = decompress_content(diary["content"])
    return jsonify({"status": "success", "data": diary})


# ==========================================
# 4️⃣ 更新日记
# ==========================================
@diary_bp.route('/<int:diary_id>', methods=['PUT'])
def update_diary(diary_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    db = get_db()
    with db.cursor() as cursor:
        sql = "UPDATE diaries SET title=%s, content=%s WHERE diary_id=%s"
        cursor.execute(sql, (title, compress_content(content), diary_id))
        db.commit()

    return jsonify({"status": "success", "message": "日记更新成功"})


# ==========================================
# 5️⃣ 删除日记
# ==========================================
@diary_bp.route('/<int:diary_id>', methods=['DELETE'])
def delete_diary(diary_id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM diaries WHERE diary_id=%s", (diary_id,))
        db.commit()
    return jsonify({"status": "success", "message": "日记已删除"})
