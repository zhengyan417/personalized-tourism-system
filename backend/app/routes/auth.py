from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.database import get_db
from app.services import auth_service


auth_bp = Blueprint('auth', __name__)


@auth_bp.after_request
def _cors_fix(resp):
    try:
        resp.headers.setdefault('Access-Control-Allow-Origin', '*')
        resp.headers.setdefault('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        resp.headers.setdefault('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    except Exception:
        pass
    return resp


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

    return jsonify({'status': 'success', 'message': '登录成功', 'data': {'id': user_id, 'username': uname, 'email': email}})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'status': 'success', 'message': '已退出登录'})


@auth_bp.route('/me', methods=['GET'])
def me():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    # 获取完整用户信息（包括个人资料）
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT user_id, username, email, age, occupation, bio, avatar, created_at, updated_at 
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
        'created_at': str(row['created_at']) if row['created_at'] else None,
        'updated_at': str(row['updated_at']) if row['updated_at'] else None
    }
    
    return jsonify({'status': 'success', 'data': user_data})


@auth_bp.route('/profile', methods=['GET', 'PUT'])
def profile():
    """获取或更新用户资料"""
    uid = session.get('user_id')
    if not uid:
        return jsonify({'status': 'error', 'message': '未登录'}), 401
    
    conn = get_db()
    
    if request.method == 'GET':
        # 获取用户资料
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, username, email, age, occupation, bio, avatar, created_at, updated_at 
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
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'updated_at': str(row['updated_at']) if row['updated_at'] else None
        }
        
        return jsonify({'status': 'success', 'data': user_data})
    
    elif request.method == 'PUT':
        # 更新用户资料
        data = request.get_json(silent=True) or {}
        
        # 允许更新的字段
        age = data.get('age')
        occupation = (data.get('occupation') or '').strip() or None
        bio = (data.get('bio') or '').strip() or None
        avatar = (data.get('avatar') or '').strip() or None
        email = (data.get('email') or '').strip() or None
        
        # 验证年龄
        if age is not None:
            try:
                age = int(age)
                if age < 0 or age > 150:
                    return jsonify({'status': 'error', 'message': '年龄必须在0-150之间'}), 400
            except (ValueError, TypeError):
                return jsonify({'status': 'error', 'message': '年龄格式错误'}), 400
        
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users 
                SET age=%s, occupation=%s, bio=%s, avatar=%s, email=%s
                WHERE user_id=%s
            """, (age, occupation, bio, avatar, email, uid))
            conn.commit()
        
        return jsonify({'status': 'success', 'message': '资料更新成功'})
