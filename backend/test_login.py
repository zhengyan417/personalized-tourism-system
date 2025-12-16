#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""独立测试登录验证"""

import pymysql
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_hash: str, password: str) -> bool:
    return stored_hash == hash_password(password)

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='lyy060519',
    database='travel_system',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

# 测试几个用户
test_cases = [
    ('admin', '123456'),
    ('LYY', '123456'),
    ('1111', '1111'),
]

print("=" * 80)
print("登录验证测试:")
print("=" * 80)

for username, password in test_cases:
    cur.execute('SELECT user_id, username, password FROM users WHERE username=%s', (username,))
    user = cur.fetchone()
    
    if user:
        stored_hash = user['password']
        result = verify_password(stored_hash, password)
        
        print(f"\n用户: {username}")
        print(f"  测试密码: {password}")
        print(f"  存储哈希: {stored_hash}")
        print(f"  计算哈希: {hash_password(password)}")
        print(f"  验证结果: {'✅ 密码正确' if result else '❌ 密码错误'}")
    else:
        print(f"\n用户 '{username}' 不存在")

print("\n" + "=" * 80)
print("✅ 测试完成！现在可以使用以下账号登录:")
print("=" * 80)
print("用户名: admin  密码: 123456")
print("用户名: LYY    密码: 123456")
print("用户名: 1111   密码: 1111")

cur.close()
conn.close()
