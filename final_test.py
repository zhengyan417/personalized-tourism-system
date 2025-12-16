import requests
import time

print("等待后端重载...")
time.sleep(3)

url = 'http://localhost:5000/api/auth/login'
test_users = [
    {'username': 'admin', 'password': '123456'},
    {'username': 'LYY', 'password': '123456'},
    {'username': '1111', 'password': '1111'},
]

print("\n" + "=" * 80)
print("测试登录 API")
print("=" * 80)

for user_data in test_users:
    print(f"\n登录: {user_data['username']} / {user_data['password']}")
    try:
        response = requests.post(url, json=user_data, headers={'Content-Type': 'application/json'}, timeout=5)
        print(f"  状态码: {response.status_code}")
        result = response.json()
        print(f"  响应: {result}")
        if response.status_code == 200:
            print(f"  ✅ 登录成功！")
        else:
            print(f"  ❌ 登录失败: {result.get('message')}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        break
