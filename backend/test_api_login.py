#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接测试 Flask API 登录接口"""

import requests
import json

# 测试用户
test_users = [
    {'username': 'admin', 'password': '123456'},
    {'username': 'LYY', 'password': '123456'},
    {'username': '1111', 'password': '1111'},
]

API_URL = 'http://localhost:5000/api/auth/login'

print("=" * 80)
print("测试实际的 Flask API 登录")
print("=" * 80)

for user_data in test_users:
    print(f"\n尝试登录: {user_data['username']} / {user_data['password']}")
    
    try:
        response = requests.post(
            API_URL,
            json=user_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")
        
        if response.status_code == 200:
            print(f"  ✅ 登录成功！")
        else:
            print(f"  ❌ 登录失败")
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ 无法连接到后端服务器（{API_URL}）")
        print(f"  请确保后端正在运行: python app.py")
        break
    except Exception as e:
        print(f"  ❌ 错误: {e}")
