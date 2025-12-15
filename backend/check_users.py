#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查用户表和密码验证"""

import pymysql
from werkzeug.security import check_password_hash

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def check_users():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 80)
    print("用户表数据检查:")
    print("=" * 80)
    
    cur.execute('SELECT user_id, username, password, email, created_at FROM users')
    rows = cur.fetchall()
    
    if not rows:
        print("⚠️  用户表为空！")
        return
    
    for r in rows:
        print(f"\n用户 #{r['user_id']}:")
        print(f"  用户名: {r['username']}")
        print(f"  密码哈希: {r['password'][:60]}...")
        print(f"  Email: {r['email']}")
        print(f"  创建时间: {r['created_at']}")
        print(f"  哈希长度: {len(r['password'])} 字符")
        print(f"  哈希前缀: {r['password'][:20]}")
    
    print(f"\n总共 {len(rows)} 个用户")
    
    # 测试密码验证
    print("\n" + "=" * 80)
    print("密码验证测试:")
    print("=" * 80)
    
    test_username = input("\n请输入要测试的用户名（按回车跳过）: ").strip()
    if test_username:
        cur.execute('SELECT password FROM users WHERE username=%s', (test_username,))
        user = cur.fetchone()
        if user:
            test_password = input("请输入密码: ")
            pwd_hash = user['password']
            result = check_password_hash(pwd_hash, test_password)
            print(f"\n验证结果: {'✅ 密码正确' if result else '❌ 密码错误'}")
            print(f"哈希值: {pwd_hash[:80]}...")
        else:
            print(f"❌ 用户 '{test_username}' 不存在")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    check_users()
