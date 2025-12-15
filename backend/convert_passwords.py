#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将所有密码转换为简单的 SHA256 哈希"""

import pymysql
import hashlib

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def hash_password(password: str) -> str:
    """使用 SHA256 哈希"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def convert_all_passwords():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 查询所有用户
    cur.execute("SELECT user_id, username, password FROM users")
    rows = cur.fetchall()
    
    print(f"找到 {len(rows)} 个用户，正在转换密码...\n")
    
    # 已知的用户密码映射（根据之前的数据）
    known_passwords = {
        'admin': '123456',
        'LYY': '123456',  # 假设默认密码
        'LLL': '123456',
        'LLLLLL': '123456',
        'OOO': '123456',
        '1111': '1111'
    }
    
    for r in rows:
        user_id = r['user_id']
        username = r['username']
        old_password = r['password']
        
        # 如果已经是 64 字符的十六进制（SHA256），跳过
        if len(old_password) == 64 and all(c in '0123456789abcdef' for c in old_password.lower()):
            print(f"⏭️  用户 '{username}' 已经是简单哈希格式，跳过")
            continue
        
        # 尝试使用已知密码
        if username in known_passwords:
            plaintext = known_passwords[username]
        else:
            # 如果是明文（长度小于20），直接使用
            if len(old_password) < 20:
                plaintext = old_password
            else:
                print(f"⚠️  用户 '{username}' 无法确定原密码，设置默认密码 '123456'")
                plaintext = '123456'
        
        # 生成新哈希
        new_hash = hash_password(plaintext)
        
        # 更新数据库
        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_hash, user_id))
        
        print(f"✅ 用户 '{username}' (ID={user_id})")
        print(f"   原密码: {plaintext}")
        print(f"   新哈希: {new_hash}")
        print()
    
    conn.commit()
    print(f"\n✅ 密码转换完成！所有用户现在使用简单的 SHA256 哈希")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    convert_all_passwords()
