import requests

BASE_URL = "http://127.0.0.1:5000"

def show(title: str, resp: requests.Response):
	try:
		print(title, resp.status_code, resp.json())
	except Exception:
		print(title, resp.status_code, resp.text[:300])

if __name__ == "__main__":
	# 测试场所查询
	res = requests.get(f"{BASE_URL}/api/places/nearby", params={"lat": 39.9, "lon": 116.4, "radius": 20})
	show("🔍 场所查询结果：", res)

	# 测试创建日记
	payload = {"user_id": 1, "attraction_id": 1, "title": "颐和园之旅", "content": "今天天气真好"}
	res = requests.post(f"{BASE_URL}/api/diaries", json=payload)
	show("📝 创建日记结果：", res)

	# 测试查询日记
	res = requests.get(f"{BASE_URL}/api/diaries", params={"user_id": 1})
	show("📚 用户日记列表：", res)

	# 测试最短路径（假设景点 ID 1 -> 5 存在，可根据实际调整）
	res = requests.get(f"{BASE_URL}/api/routes/shortest", params={"start_id": 1, "end_id": 5, "max_distance_km": 80})
	show("🧭 最短路径：", res)
