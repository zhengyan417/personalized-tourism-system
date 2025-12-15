#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""执行数据库迁移 - 添加用户资料扩展字段"""

import pymysql
from config import Config

def main():
    # 连接数据库
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 要执行的SQL语句
    migrations = [
        'ALTER TABLE users ADD COLUMN age INT NULL COMMENT "年龄" AFTER email',
        'ALTER TABLE users ADD COLUMN occupation VARCHAR(100) NULL COMMENT "职业" AFTER age',
        'ALTER TABLE users ADD COLUMN bio TEXT NULL COMMENT "个人简介" AFTER occupation',
        'ALTER TABLE users ADD COLUMN avatar VARCHAR(500) NULL COMMENT "头像URL" AFTER bio',
        'ALTER TABLE users ADD COLUMN updated_at DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT "最后更新时间" AFTER created_at'
    ]
    
    print("开始执行数据库迁移...")
    
    # 逐个执行SQL
    for i, sql in enumerate(migrations, 1):
        try:
            print(f"{i}. 执行: {sql[:50]}...")
            cursor.execute(sql)
            conn.commit()
            print(f"   ✅ 成功")
        except Exception as e:
            # 如果字段已存在则跳过
            if "Duplicate column name" in str(e):
                print(f"   ⚠️  字段已存在，跳过")
            else:
                print(f"   ❌ 失败: {e}")
                raise
    
    # 查看最终表结构
    print("\n最终表结构：")
    cursor.execute('DESCRIBE users')
    rows = cursor.fetchall()
    print(f"{'字段名':<20} {'类型':<30} {'NULL':<8} {'键':<8} {'默认值':<15}")
    print("=" * 85)
    for row in rows:
        print(f"{row[0]:<20} {row[1]:<30} {row[2]:<8} {row[3]:<8} {str(row[4] or ''):<15}")
    
    cursor.close()
    conn.close()
    print("\n✅ 数据库迁移完成！")

if __name__ == '__main__':
    main()
