from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.database import get_db
from app.services import auth_service


auth_bp = Blueprint('auth', __name__)


# CORS 由全局 CORS(app) 统一处理，支持 credentials
# @auth_bp.after_request
# def _cors_fix(resp):
#     # 不再手动设置 CORS 头，避免与全局配置冲突
#     return resp


def _find_user_by_username(conn, username: str):
    # 保持兼容旧实现，但优先使用服务层
    row = auth_service.get_user_by_username(username)
    if row:
        return row
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, username, password, email FROM users WHERE username=%s LIMIT 1", (username,))
        return cur.fetchone()


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    email = (data.get('email') or '').strip() or None

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'username 和 password 必填'}), 400

    conn = get_db()
    # 查重
    if _find_user_by_username(conn, username):
        return jsonify({'status': 'error', 'message': '用户名已存在'}), 409

    # 使用服务层创建用户
    auth_service.create_user(username, password, email)

    return jsonify({'status': 'success', 'message': '注册成功'})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'username 和 password 必填'}), 400

    conn = get_db()
    row = _find_user_by_username(conn, username)
    if not row:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404

    user_id, uname, pwd_hash, email = row
    if not auth_service.verify_password(pwd_hash, password):
        return jsonify({'status': 'error', 'message': '密码错误'}), 401

    # 设置会话（服务器端 session cookie）
    session['user_id'] = int(user_id)
    session['username'] = uname
    
    # 获取完整用户资料（包括个人信息和旅游偏好）
    with conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, username, email, age, occupation, bio, avatar,
                   travel_persona, favorite_cities,
                   created_at, updated_at
            FROM users WHERE user_id=%s
        """, (user_id,))
        profile_row = cur.fetchone()
    
    user_data = {
        'id': profile_row['user_id'],
        'username': profile_row['username'],
        'email': profile_row['email'],
        'age': profile_row.get('age'),
        'occupation': profile_row.get('occupation'),
        'bio': profile_row.get('bio'),
        'avatar': profile_row.get('avatar'),
        'travel_persona': profile_row.get('travel_persona'),
        'favorite_cities': profile_row.get('favorite_cities'),
        'created_at': str(profile_row['created_at']) if profile_row.get('created_at') else None,
        'updated_at': str(profile_row['updated_at']) if profile_row.get('updated_at') else None
    }

    return jsonify({'status': 'success', 'message': '登录成功', 'data': user_data})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': '已退出登录'})


@auth_bp.route('/me', methods=['GET'])
def me():
    """获取当前登录用户的基本信息"""
    uid = session.get('user_id')
    if not uid:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 获取完整用户信息（包括个人资料）
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, username, email, age, occupation, bio, avatar,
                   travel_persona, favorite_cities,
                   created_at, updated_at
            FROM users WHERE user_id=%s
        """, (uid,))
        row = cur.fetchone()
        
    if not row:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    
    user_data = {
        'id': row['user_id'],
        'username': row['username'],
        'email': row['email'],
        'age': row.get('age'),
        'occupation': row.get('occupation'),
        'bio': row.get('bio'),
        'avatar': row.get('avatar'),
        'travel_persona': row.get('travel_persona'),
        'favorite_cities': row.get('favorite_cities'),
        'created_at': str(row['created_at']) if row.get('created_at') else None,
        'updated_at': str(row['updated_at']) if row.get('updated_at') else None
    }
    
    # 获取用户日记统计
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) as diary_count FROM diaries WHERE user_id=%s", (uid,))
        stats = cur.fetchone()
        user_data['diary_count'] = stats['diary_count'] if stats else 0
    
    return jsonify({'status': 'success', 'data': user_data})


@auth_bp.route('/profile', methods=['GET', 'PUT'])
def profile():
    """获取或更新用户资料"""
    uid = session.get('user_id')
    if not uid:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    conn = get_db()
    
    if request.method == 'GET':
        # 获取用户资料（包括扩展字段）
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, username, email, age, occupation, bio, avatar,
                       travel_persona, favorite_cities,
                       created_at, updated_at
                FROM users WHERE user_id=%s
            """, (uid,))
            row = cur.fetchone()
            
        if not row:
            return jsonify({'status': 'error', 'message': '用户不存在'}), 404
        
        user_data = {
            'id': row['user_id'],
            'username': row['username'],
            'email': row['email'],
            'age': row['age'],
            'occupation': row['occupation'],
            'bio': row['bio'],
            'avatar': row['avatar'],
            'travel_persona': row.get('travel_persona'),
            'favorite_cities': row.get('favorite_cities'),
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'updated_at': str(row['updated_at']) if row['updated_at'] else None
        }
        
        return jsonify({'status': 'success', 'data': user_data})
    
    elif request.method == 'PUT':
        # 更新用户资料
        data = request.get_json(silent=True) or {}
        
        # 获取更新字段
        email = (data.get('email') or '').strip() or None
        age = data.get('age')
        occupation = (data.get('occupation') or '').strip() or None
        bio = (data.get('bio') or '').strip() or None
        avatar = (data.get('avatar') or '').strip() or None
        travel_persona = (data.get('travel_persona') or '').strip() or None
        favorite_cities = (data.get('favorite_cities') or '').strip() or None
        
        # 验证邮箱格式
        if email and '@' not in email:
            return jsonify({'status': 'error', 'message': '邮箱格式错误'}), 400
        
        # 验证年龄
        if age is not None:
            try:
                age = int(age)
                if age < 0 or age > 150:
                    return jsonify({'status': 'error', 'message': '年龄必须在0-150之间'}), 400
            except (ValueError, TypeError):
                return jsonify({'status': 'error', 'message': '年龄格式错误'}), 400
        
        # 构建更新语句（只更新提供的字段）
        update_fields = []
        params = []
        
        if email is not None:
            update_fields.append('email=%s')
            params.append(email)
        if age is not None:
            update_fields.append('age=%s')
            params.append(age)
        if occupation is not None:
            update_fields.append('occupation=%s')
            params.append(occupation)
        if bio is not None:
            update_fields.append('bio=%s')
            params.append(bio)
        if avatar is not None:
            update_fields.append('avatar=%s')
            params.append(avatar)
        if travel_persona is not None:
            update_fields.append('travel_persona=%s')
            params.append(travel_persona)
        if favorite_cities is not None:
            update_fields.append('favorite_cities=%s')
            params.append(favorite_cities)
        
        if update_fields:
            params.append(uid)
            sql = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id=%s"
            
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
        
        return jsonify({'status': 'success', 'message': '资料更新成功'})
