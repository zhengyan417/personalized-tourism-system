import requests
import time

time.sleep(2)  # 等待服务器完全启动

url = 'http://localhost:5000/api/auth/login'
data = {'username': 'admin', 'password': '123456'}

print("发送登录请求...")
response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
