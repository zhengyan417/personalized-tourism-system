#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接测试auth_service模块"""

import sys
sys.path.insert(0, 'c:/code/travel/backend')

from app.services import auth_service
import pymysql

# 连接数据库查看实际存储的密码
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='lyy060519',
    database='travel_system',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()
cur.execute("SELECT user_id, username, password FROM users WHERE username='admin'")
user = cur.fetchone()

print("=" * 80)
print("直接测试 auth_service.verify_password()")
print("=" * 80)

if user:
    print(f"\n数据库中的用户:")
    print(f"  ID: {user['user_id']}")
    print(f"  用户名: {user['username']}")
    print(f"  存储密码: {user['password']}")
    
    # 测试密码验证
    test_password = '123456'
    print(f"\n测试密码: {test_password}")
    
    result = auth_service.verify_password(user['password'], test_password)
    print(f"verify_password() 返回: {result}")
    
    # 手动计算哈希
    import hashlib
    computed_hash = hashlib.sha256(test_password.encode('utf-8')).hexdigest()
    print(f"\n手动计算的 SHA256: {computed_hash}")
    print(f"存储的密码:        {user['password']}")
    print(f"两者相等: {computed_hash == user['password']}")

cur.close()
conn.close()
