#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为用户表添加个人资料字段"""

import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='lyy060519',
    database='travel_system'
)

cur = conn.cursor()

print("正在添加用户资料字段...")

try:
    # 检查字段是否已存在
    cur.execute("SHOW COLUMNS FROM users LIKE 'age'")
    if cur.fetchone():
        print("⚠️  字段已存在，跳过添加")
    else:
        cur.execute('ALTER TABLE users ADD COLUMN age INT COMMENT "年龄"')
        cur.execute('ALTER TABLE users ADD COLUMN occupation VARCHAR(100) COMMENT "职业"')
        cur.execute('ALTER TABLE users ADD COLUMN bio TEXT COMMENT "个人简介"')
        cur.execute('ALTER TABLE users ADD COLUMN avatar VARCHAR(255) COMMENT "头像URL"')
        cur.execute('ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT "更新时间"')
        conn.commit()
        print("✅ 用户表字段添加成功")
        
    # 显示更新后的表结构
    cur.execute("DESCRIBE users")
    rows = cur.fetchall()
    print("\n更新后的用户表结构:")
    for row in rows:
        print(f"  {row[0]:20s} {row[1]:30s} NULL={row[2]}")
        
except pymysql.Error as e:
    print(f"❌ 错误: {e}")
    conn.rollback()

cur.close()
conn.close()
