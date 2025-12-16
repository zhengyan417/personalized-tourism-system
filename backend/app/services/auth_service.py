from typing import Optional, Tuple
import hashlib
from app.utils.database import get_db


def _hash_password(password: str) -> str:
    """使用简单的 SHA256 哈希密码"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_user_by_username(username: str) -> Optional[Tuple[int, str, str, Optional[str]]]:
    """返回 (user_id, username, password, email) 或 None"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, username, password, email FROM users WHERE username=%s LIMIT 1", (username,))
        row = cur.fetchone()
        if row:
            # DictCursor 返回 dict，需要转换为 tuple
            return (row['user_id'], row['username'], row['password'], row['email'])
        return None


def create_user(username: str, password: str, email: Optional[str] = None) -> int:
    """创建用户并返回用户ID"""
    conn = get_db()
    pwd_hash = _hash_password(password)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, pwd_hash, email)
        )
        conn.commit()
        return cur.lastrowid


def verify_password(pwd_hash: str, password: str) -> bool:
    """验证密码"""
    return pwd_hash == _hash_password(password)
