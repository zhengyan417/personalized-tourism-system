#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复明文密码用户"""

import pymysql
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def fix_plaintext_passwords():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 查找所有明文密码（不是以 pbkdf2: 或 scrypt: 开头的）
    cur.execute("SELECT user_id, username, password FROM users WHERE password NOT LIKE 'pbkdf2:%' AND password NOT LIKE 'scrypt:%'")
    rows = cur.fetchall()
    
    if not rows:
        print("✅ 所有用户密码都已正确哈希！")
        return
    
    print(f"发现 {len(rows)} 个用户使用明文密码，正在修复...\n")
    
    for r in rows:
        user_id = r['user_id']
        username = r['username']
        plaintext = r['password']
        
        # 生成哈希密码
        hashed = generate_password_hash(plaintext)
        
        # 更新数据库
        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (hashed, user_id))
        
        print(f"✅ 用户 '{username}' (ID={user_id})")
        print(f"   原密码（明文）: {plaintext}")
        print(f"   新密码（哈希）: {hashed[:60]}...")
        print()
    
    conn.commit()
    print(f"✅ 已修复 {len(rows)} 个用户的密码！")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    fix_plaintext_passwords()
