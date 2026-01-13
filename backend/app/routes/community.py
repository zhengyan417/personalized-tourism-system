# /backend/app/routes/community.py
from flask import Blueprint, request, jsonify, session
from app.utils.database import get_db
import zlib
import base64
import traceback

community_bp = Blueprint("community", __name__)


def safe_decode(value):
    """安全地将 bytes 转换为 str"""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if not isinstance(value, str):
        return str(value)
    return value


# ========== 公开日记列表 ==========
@community_bp.route("/api/community/diaries", methods=["GET"])
def get_public_diaries():
    """获取所有公开的日记列表，支持分页"""
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit

    conn = get_db()
    cursor = conn.cursor()

    try:
        # 获取公开日记，按创建时间倒序，包含用户信息
        query = """
            SELECT 
                d.diary_id,
                d.user_id,
                d.title,
                d.content,
                d.latitude,
                d.longitude,
                d.created_at,
                d.like_count,
                d.comment_count,
                d.view_count,
                u.username,
                u.nickname,
                u.avatar_url
            FROM diaries d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.is_public = 1
            ORDER BY d.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, offset))
        diaries = cursor.fetchall()

        # 解压内容并格式化返回
        result = []
        for diary in diaries:
            try:
                # 解压日记内容：先 base64 解码，再 zlib 解压
                content_bytes = diary["content"]
                if isinstance(content_bytes, bytes):
                    # 先 base64 解码
                    decoded = base64.b64decode(content_bytes)
                    # 再 zlib 解压
                    decompressed = zlib.decompress(decoded).decode("utf-8")
                else:
                    decompressed = str(content_bytes)
            except Exception as e:
                print(
                    f"[Community] 解压内容失败: {e}, content type: {type(diary['content'])}"
                )
                decompressed = str(diary["content"])

            result.append(
                {
                    "diary_id": diary["diary_id"],
                    "user_id": diary["user_id"],
                    "username": safe_decode(diary["username"]),
                    "nickname": safe_decode(diary["nickname"])
                    or safe_decode(diary["username"]),
                    "avatar_url": safe_decode(diary["avatar_url"]),
                    "title": safe_decode(diary["title"]),
                    "content": decompressed,
                    "latitude": float(diary["latitude"]) if diary["latitude"] else None,
                    "longitude": (
                        float(diary["longitude"]) if diary["longitude"] else None
                    ),
                    "created_at": diary["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "date": diary["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "like_count": diary["like_count"],
                    "comment_count": diary["comment_count"],
                    "view_count": diary["view_count"],
                }
            )

        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM diaries WHERE is_public = 1")
        total = cursor.fetchone()["total"]

        return jsonify(
            {
                "success": True,
                "diaries": result,
                "pagination": {"page": page, "limit": limit, "total": total},
            }
        )

    except Exception as e:
        print(f"[Community Error] {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "message": str(e)}), 500


# ========== 点赞/取消点赞 ==========
@community_bp.route("/api/community/diaries/<int:diary_id>/like", methods=["POST"])
def toggle_like(diary_id):
    """点赞或取消点赞"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()

    try:
        # 检查是否已点赞
        cursor.execute(
            "SELECT like_id FROM diary_likes WHERE diary_id = %s AND user_id = %s",
            (diary_id, user_id),
        )
        existing_like = cursor.fetchone()

        if existing_like:
            # 已点赞，取消点赞
            cursor.execute(
                "DELETE FROM diary_likes WHERE diary_id = %s AND user_id = %s",
                (diary_id, user_id),
            )
            action = "unliked"
        else:
            # 未点赞，添加点赞
            cursor.execute(
                "INSERT INTO diary_likes (diary_id, user_id) VALUES (%s, %s)",
                (diary_id, user_id),
            )
            action = "liked"

        conn.commit()

        # 获取最新点赞数
        cursor.execute(
            "SELECT like_count FROM diaries WHERE diary_id = %s", (diary_id,)
        )
        result = cursor.fetchone()
        like_count = result["like_count"] if result else 0

        return jsonify({"success": True, "action": action, "like_count": like_count})

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ========== 获取评论列表 ==========
@community_bp.route("/api/community/diaries/<int:diary_id>/comments", methods=["GET"])
def get_comments(diary_id):
    """获取日记的所有评论"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        query = """
            SELECT 
                c.comment_id,
                c.diary_id,
                c.user_id,
                c.content,
                c.parent_id,
                c.created_at,
                u.username,
                u.nickname,
                u.avatar_url
            FROM diary_comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.diary_id = %s
            ORDER BY c.created_at ASC
        """
        cursor.execute(query, (diary_id,))
        comments = cursor.fetchall()

        result = []
        for comment in comments:
            result.append(
                {
                    "comment_id": comment["comment_id"],
                    "diary_id": comment["diary_id"],
                    "user_id": comment["user_id"],
                    "username": safe_decode(comment["username"]),
                    "nickname": safe_decode(comment["nickname"])
                    or safe_decode(comment["username"]),
                    "avatar_url": safe_decode(comment["avatar_url"]),
                    "content": safe_decode(comment["content"]),
                    "parent_id": comment["parent_id"],
                    "created_at": comment["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "date": comment["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        return jsonify({"success": True, "comments": result})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ========== 添加评论 ==========
@community_bp.route("/api/community/diaries/<int:diary_id>/comments", methods=["POST"])
def add_comment(diary_id):
    """为日记添加评论"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "请先登录"}), 401

    user_id = session["user_id"]
    data = request.json
    content = data.get("content", "").strip()
    parent_id = data.get("parent_id")

    if not content:
        return jsonify({"success": False, "message": "评论内容不能为空"}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # 插入评论
        cursor.execute(
            "INSERT INTO diary_comments (diary_id, user_id, content, parent_id) VALUES (%s, %s, %s, %s)",
            (diary_id, user_id, content, parent_id),
        )
        conn.commit()

        comment_id = cursor.lastrowid
        return jsonify({"success": True, "comment_id": comment_id})

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ========== 增加浏览量 ==========
@community_bp.route("/api/community/diaries/<int:diary_id>/view", methods=["POST"])
def increment_view(diary_id):
    """增加日记浏览量"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # 更新浏览量
        cursor.execute(
            "UPDATE diaries SET view_count = view_count + 1 WHERE diary_id = %s",
            (diary_id,),
        )
        conn.commit()

        # 获取更新后的浏览量
        cursor.execute(
            "SELECT view_count FROM diaries WHERE diary_id = %s", (diary_id,)
        )
        result = cursor.fetchone()

        if result:
            return jsonify({"success": True, "view_count": result["view_count"]})
        else:
            return jsonify({"success": False, "message": "日记不存在"}), 404

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
