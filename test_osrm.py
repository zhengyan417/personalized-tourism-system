#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试OSRM路线规划服务可用性"""

import requests
import json

def test_osrm():
    """测试OSRM服务"""
    # 测试坐标：北京天安门 -> 故宫
    coords = "116.397428,39.90923;116.403414,39.918058"
    url = f"https://router.project-osrm.org/route/v1/driving/{coords}"
    
    print("=" * 80)
    print("测试OSRM路线规划服务")
    print("=" * 80)
    print(f"请求URL: {url}")
    print()
    
    try:
        response = requests.get(url, params={
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'true'
        }, timeout=15)
        
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            
            if 'routes' in data and len(data['routes']) > 0:
                route = data['routes'][0]
                print("\n路线信息:")
                print(f"  距离: {route.get('distance', 0) / 1000:.2f} km")
                print(f"  预计时间: {route.get('duration', 0) / 60:.2f} 分钟")
                print("\n✅ OSRM服务正常工作")
            else:
                print("\n❌ 响应中没有路线数据")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时 - OSRM服务可能无法访问")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 无法连接到OSRM服务器")
    except Exception as e:
        print(f"❌ 发生错误: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_osrm()
