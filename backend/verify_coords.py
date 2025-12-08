#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证修正后的坐标数据"""

import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lyy060519',
    'database': 'travel_system',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def verify_attractions():
    """验证景点坐标"""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 检查几个关键修正过的景点
    test_names = ['天坛', '圆明园', '八达岭长城', '首都机场', '大兴机场', '北京丰台站']
    
    print("=" * 60)
    print("景点坐标验证:")
    print("=" * 60)
    
    for name in test_names:
        cur.execute('SELECT name, latitude, longitude FROM attractions WHERE name = %s', (name,))
        row = cur.fetchone()
        if row:
            print(f"{row['name']:15s} : {row['latitude']:.4f}, {row['longitude']:.4f}")
        else:
            print(f"{name:15s} : 未找到")
    
    cur.close()
    conn.close()

def verify_facilities():
    """验证设施坐标"""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    test_names = ['北京首都国际机场', '北京西站', '清华大学', '北京大学', '中国尊']
    
    print("\n" + "=" * 60)
    print("设施坐标验证:")
    print("=" * 60)
    
    for name in test_names:
        cur.execute('SELECT name, latitude, longitude FROM facilities WHERE name = %s', (name,))
        row = cur.fetchone()
        if row:
            print(f"{row['name']:20s} : {row['latitude']:.4f}, {row['longitude']:.4f}")
        else:
            print(f"{name:20s} : 未找到")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    verify_attractions()
    verify_facilities()
    print("\n✅ 数据验证完成！")
