from typing import Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.database import get_db


def get_user_by_username(username: str) -> Optional[Tuple[int, str, str, Optional[str]]]:
    """返回 (user_id, username, password, email) 或 None"""
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT user_id, username, password, email FROM users WHERE username=%s LIMIT 1", (username,))
        row = cur.fetchone()
        return row


def create_user(username: str, password: str, email: Optional[str] = None) -> int:
    """创建用户并返回用户ID"""
    conn = get_db()
    pwd_hash = generate_password_hash(password)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, pwd_hash, email)
        )
        conn.commit()
        return cur.lastrowid


def verify_password(pwd_hash: str, password: str) -> bool:
    return check_password_hash(pwd_hash, password)
