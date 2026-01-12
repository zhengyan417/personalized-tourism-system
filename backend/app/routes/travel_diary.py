# 文件路径：backend/app/routes/travel_diary.py
# 模块功能：旅游日记 CRUD + 内容压缩 + 地图位置

from datetime import datetime
from decimal import Decimal
from functools import wraps

from flask import Blueprint, request, jsonify, session

from app.utils.database import get_db

import base64
import zlib


diary_bp = Blueprint('diary', __name__)

_LOCATION_CACHE = {"checked": False, "available": False}
_SNIPPET_LEN = 160


def login_required(f):
    """装饰器：验证用户是否已登录"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


def compress_content(text):
    if text is None:
        return None
    payload = (text if isinstance(text, str) else str(text)).encode('utf-8')
    compressed = zlib.compress(payload)
    return base64.b64encode(compressed).decode('utf-8')


def decompress_content(encoded):
    if encoded in (None, "", b""):
        return ""

    def _ensure_bytes(val):
        if isinstance(val, (bytes, bytearray)):
            return bytes(val)
        return str(val).encode('utf-8', errors='ignore')

    payload = _ensure_bytes(encoded)

    # 1) 假定为 base64(zlib)（当前实现、新数据）
    try:
        decoded = base64.b64decode(payload, validate=True)
        return zlib.decompress(decoded).decode('utf-8')
    except Exception:
        pass

    # 2) 假定为纯 zlib 压缩（历史直接写入 BLOB）
    try:
        return zlib.decompress(payload).decode('utf-8')
    except Exception:
        pass

    # 3) 作为明文返回（兼容旧数据或测试记录）
    try:
        return payload.decode('utf-8')
    except Exception:
        return "[内容解压失败]"


def _coerce_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_user_id(raw):
    try:
        value = int(raw)
        return value if value > 0 else None
    except (TypeError, ValueError):
        return None


def _format_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M')
    return str(value)


def _build_snippet(text):
    if not text:
        return ""
    if len(text) <= _SNIPPET_LEN:
        return text
    return text[:_SNIPPET_LEN] + "…"


def _has_location_columns():
    global _LOCATION_CACHE
    if _LOCATION_CACHE["checked"]:
        return _LOCATION_CACHE["available"]
    db = get_db()
    if not db:
        return False
    try:
        with db.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM diaries LIKE 'latitude'")
            has_lat = cursor.fetchone() is not None
            cursor.execute("SHOW COLUMNS FROM diaries LIKE 'longitude'")
            has_lon = cursor.fetchone() is not None
        _LOCATION_CACHE = {"checked": True, "available": bool(has_lat and has_lon)}
    except Exception:
        _LOCATION_CACHE = {"checked": True, "available": False}
    return _LOCATION_CACHE["available"]


def _build_select_sql(include_location):
    fields = [
        "d.diary_id",
        "d.user_id",
        "d.attraction_id",
        "d.title",
        "d.content",
        "d.create_time"
    ]
    if include_location:
        fields.extend(["d.latitude", "d.longitude"])
    fields.extend([
        "a.name AS attraction_name",
        "a.latitude AS attr_latitude",
        "a.longitude AS attr_longitude",
        "u.username AS username"  # 添加用户名
    ])
    select = f"SELECT {', '.join(fields)} FROM diaries d LEFT JOIN attractions a ON d.attraction_id = a.attraction_id LEFT JOIN users u ON d.user_id = u.user_id"
    return select


def _row_to_diary(row):
    if not row:
        return None
    content = decompress_content(row.get('content'))
    snippet = _build_snippet(content)
    lat = _coerce_float(row.get('latitude'))
    lon = _coerce_float(row.get('longitude'))
    if lat is None:
        lat = _coerce_float(row.get('attr_latitude'))
    if lon is None:
        lon = _coerce_float(row.get('attr_longitude'))
    return {
        "id": row.get('diary_id'),
        "diary_id": row.get('diary_id'),
        "user_id": row.get('user_id'),
        "username": row.get('username'),  # 添加用户名
        "user_avatar": row.get('user_avatar'),  # 添加用户头像
        "attraction_id": row.get('attraction_id'),
        "attraction_name": row.get('attraction_name'),
        "title": row.get('title') or "",
        "content": content,
        "snippet": snippet,
        "date": _format_timestamp(row.get('create_time')),
        "latitude": lat,
        "longitude": lon
    }


def _fetch_diary(diary_id):
    db = get_db()
    if not db:
        return None
    include_location = _has_location_columns()
    sql = _build_select_sql(include_location) + " WHERE d.diary_id=%s LIMIT 1"
    with db.cursor() as cursor:
        cursor.execute(sql, (diary_id,))
        row = cursor.fetchone()
    return _row_to_diary(row)


def _ensure_user_exists(user_id):
    if not user_id:
        return False
    db = get_db()
    if not db:
        return False
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE user_id=%s LIMIT 1", (user_id,))
            if cursor.fetchone():
                return True
            cursor.execute(
                "INSERT INTO users (user_id, username, email, password) VALUES (%s, %s, %s, %s)",
                (user_id, f"游客{user_id}", None, 'placeholder')
            )
        db.commit()
        return True
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        # 若并发导致重复插入，认为成功
        return True


def _success(payload, **extra):
    base = {"success": True, "data": payload}
    base.update(extra)
    return jsonify(base)


def _error(message, status=400):
    return jsonify({"success": False, "message": message}), status


@diary_bp.route('', methods=['POST'])
@diary_bp.route('/', methods=['POST'])
@diary_bp.route('/create', methods=['POST'])
@login_required
def create_diary():
    """创建旅行日记（需要登录）"""
    # 从 session 获取当前登录用户 ID
    user_id = session.get('user_id')
    
    data = request.get_json(silent=True) or {}
    content = data.get('content')
    if not content:
        return _error('content 不能为空')

    attraction_id = data.get('attraction_id')
    title = data.get('title') or '未命名日记'
    latitude = data.get('latitude') if 'latitude' in data else None
    longitude = data.get('longitude') if 'longitude' in data else None
    lat_val = _coerce_float(latitude)
    lon_val = _coerce_float(longitude)

    db = get_db()
    if not db:
        return _error('数据库未初始化，请稍后重试', 500)
    include_location = _has_location_columns()
    
    columns = ['user_id', 'attraction_id', 'title', 'content']
    values = [user_id, attraction_id, title, compress_content(content)]
    placeholders = ['%s'] * len(columns)
    if include_location:
        columns.extend(['latitude', 'longitude'])
        values.extend([lat_val, lon_val])
        placeholders.extend(['%s', '%s'])

    sql = f"INSERT INTO diaries ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    try:
        with db.cursor() as cursor:
            cursor.execute(sql, values)
            db.commit()
            new_id = cursor.lastrowid
    except Exception as e:
        return _error(f'创建失败: {e}', 500)

    diary = _fetch_diary(new_id)
    return _success(diary)


@diary_bp.route('', methods=['GET'])
@diary_bp.route('/', methods=['GET'])
def list_diaries():
    """获取日记列表
    - 如果提供 user_id 参数，则获取指定用户的日记（公开查看）
    - 如果没有 user_id 参数但已登录，则获取当前用户的日记
    """
    # 优先使用 URL 参数的 user_id（用于查看其他用户的日记）
    user_id = request.args.get('user_id', type=int)
    
    # 如果没有提供 user_id，尝试从 session 获取当前登录用户
    if not user_id:
        user_id = session.get('user_id')
    
    if not user_id:
        return _error('请提供 user_id 参数或先登录')

    db = get_db()
    if not db:
        return _error('数据库未初始化，请稍后重试', 500)
    include_location = _has_location_columns()
    sql = _build_select_sql(include_location) + ' WHERE d.user_id=%s ORDER BY d.create_time DESC'
    with db.cursor() as cursor:
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()

    diaries = [_row_to_diary(r) for r in rows]
    return _success(diaries, count=len(diaries))


@diary_bp.route('/public', methods=['GET'])
def list_public_diaries():
    """获取所有公开的日记(社区浏览用)"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    offset = (page - 1) * limit

    db = get_db()
    if not db:
        return _error('数据库未初始化，请稍后重试', 500)
    
    include_location = _has_location_columns()
    
    # 构建查询SQL，包含用户头像
    select_fields = [
        "d.diary_id",
        "d.user_id",
        "d.attraction_id",
        "d.title",
        "d.content",
        "d.create_time"
    ]
    if include_location:
        select_fields.extend(["d.latitude", "d.longitude"])
    select_fields.extend([
        "a.name AS attraction_name",
        "a.latitude AS attr_latitude",
        "a.longitude AS attr_longitude",
        "u.username AS username",
        "u.avatar AS user_avatar"  # 添加用户头像
    ])
    
    sql = f"""
        SELECT {', '.join(select_fields)}
        FROM diaries d 
        LEFT JOIN attractions a ON d.attraction_id = a.attraction_id 
        LEFT JOIN users u ON d.user_id = u.user_id
        ORDER BY d.create_time DESC
        LIMIT %s OFFSET %s
    """
    
    with db.cursor() as cursor:
        cursor.execute(sql, (limit, offset))
        rows = cursor.fetchall()
        
        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM diaries")
        total_row = cursor.fetchone()
        total = total_row['total'] if total_row else 0

    diaries = [_row_to_diary(r) for r in rows]
    return _success(diaries, count=len(diaries), total=total, page=page, limit=limit)


@diary_bp.route('/<int:diary_id>', methods=['GET'])
def get_diary(diary_id):
    diary = _fetch_diary(diary_id)
    if not diary:
        return _error('日记不存在', 404)
    return _success(diary)


@diary_bp.route('/<int:diary_id>', methods=['PUT', 'PATCH'])
@login_required
def update_diary(diary_id):
    """更新日记（需要登录，且只能更新自己的日记）"""
    current_user_id = session.get('user_id')
    
    # 先检查日记是否存在以及是否属于当前用户
    diary = _fetch_diary(diary_id)
    if not diary:
        return _error('日记不存在', 404)
    
    if diary['user_id'] != current_user_id:
        return _error('无权修改他人的日记', 403)
    
    data = request.get_json(silent=True) or {}
    fields = []
    values = []

    if 'title' in data:
        fields.append('title=%s')
        values.append(data.get('title'))
    if 'content' in data:
        fields.append('content=%s')
        values.append(compress_content(data.get('content')))
    if 'attraction_id' in data:
        fields.append('attraction_id=%s')
        values.append(data.get('attraction_id'))

    include_location = _has_location_columns()
    if include_location:
        if 'latitude' in data:
            fields.append('latitude=%s')
            values.append(_coerce_float(data.get('latitude')))
        if 'longitude' in data:
            fields.append('longitude=%s')
            values.append(_coerce_float(data.get('longitude')))

    if not fields:
        return _error('未提供需要更新的字段')

    values.append(diary_id)
    db = get_db()
    if not db:
        return _error('数据库未初始化，请稍后重试', 500)
    with db.cursor() as cursor:
        cursor.execute(f"UPDATE diaries SET {', '.join(fields)} WHERE diary_id=%s", values)
        db.commit()

    diary = _fetch_diary(diary_id)
    return _success(diary)


@diary_bp.route('/<int:diary_id>', methods=['DELETE'])
@login_required
def delete_diary(diary_id):
    """删除日记（需要登录，且只能删除自己的日记）"""
    current_user_id = session.get('user_id')
    
    # 先检查日记是否存在以及是否属于当前用户
    diary = _fetch_diary(diary_id)
    if not diary:
        return _error('日记不存在', 404)
    
    if diary['user_id'] != current_user_id:
        return _error('无权删除他人的日记', 403)
    
    db = get_db()
    if not db:
        return _error('数据库未初始化，请稍后重试', 500)
    with db.cursor() as cursor:
        cursor.execute('DELETE FROM diaries WHERE diary_id=%s', (diary_id,))
        db.commit()
    return jsonify({"success": True, "message": "日记已删除"})
