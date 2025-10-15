import requests

BASE_URL = "http://127.0.0.1:5000"

# 测试场所查询
res = requests.get(f"{BASE_URL}/api/places/nearby", params={"lat": 39.9, "lon": 116.4, "radius": 20})
print("🔍 场所查询结果：", res.json())

# 测试创建日记
payload = {"user_id": 1, "attraction_id": 1, "title": "颐和园之旅", "content": "今天天气真好"}
res = requests.post(f"{BASE_URL}/api/diaries/create", json=payload)
print("📝 创建日记结果：", res.json())

# 测试查询日记
res = requests.get(f"{BASE_URL}/api/diaries", params={"user_id": 1})
print("📚 用户日记列表：", res.json())
