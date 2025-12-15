#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查日记表中的用户名显示问题"""

import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4'
}

def check_diaries():
    """检查日记表和用户关联"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询日记和用户的关联情况
        sql = """
        SELECT 
            d.diary_id,
            d.user_id,
            d.title,
            d.create_time,
            u.username,
            u.user_id as joined_user_id
        FROM diaries d
        LEFT JOIN users u ON d.user_id = u.user_id
        ORDER BY d.create_time DESC
        LIMIT 20
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        print("=" * 80)
        print("日记数据和用户关联检查:")
        print("=" * 80)
        
        if not results:
            print("数据库中没有日记记录")
        else:
            for row in results:
                print(f"\n日记ID: {row['diary_id']}")
                print(f"  用户ID (diary.user_id): {row['user_id']}")
                print(f"  用户ID (users.user_id): {row['joined_user_id']}")
                print(f"  用户名: {row['username']}")
                print(f"  标题: {row['title']}")
                print(f"  创建时间: {row['create_time']}")
        
        # 统计不同用户的日记数量
        print("\n" + "=" * 80)
        print("按用户统计日记数量:")
        print("=" * 80)
        
        stats_sql = """
        SELECT 
            d.user_id,
            u.username,
            COUNT(*) as diary_count
        FROM diaries d
        LEFT JOIN users u ON d.user_id = u.user_id
        GROUP BY d.user_id, u.username
        ORDER BY diary_count DESC
        """
        
        cursor.execute(stats_sql)
        stats = cursor.fetchall()
        
        for stat in stats:
            print(f"用户ID: {stat['user_id']}, 用户名: {stat['username']}, 日记数: {stat['diary_count']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_diaries()
