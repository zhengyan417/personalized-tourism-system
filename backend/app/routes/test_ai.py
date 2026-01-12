# test_ai_local.py
import requests
import json

# 要测试的本地 Flask 接口地址
LOCAL_AI_CHAT_URL = "http://localhost:5000/api/ai/chat"

# 构造请求体（与你的 curl 一致）
payload = {
    "query": "我是大学生,帮我推荐一些旅游景点",
    "user_id": "123123",
    "user_profile": {}  # 可选，这里留空
}

print("正在向本地 Flask 服务发送请求...")
print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")

try:
    # 发送 POST 请求（stream=True 以支持 SSE）
    response = requests.post(
        LOCAL_AI_CHAT_URL,
        json=payload,
        stream=True,
        timeout=30
    )

    print(f"响应状态码: {response.status_code}")
    print("开始接收流式响应（SSE）:\n")

    # 逐行读取流式响应
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print(decoded_line)

            # 可选：检测是否结束
            if decoded_line.strip() == "data: [DONE]":
                print("\n[INFO] 收到结束信号")
                break

except requests.exceptions.Timeout:
    print("❌ 请求超时")
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到本地服务，请确保 Flask 正在运行")
except Exception as e:
    print(f"❌ 发生错误: {e}")