"""
测试AI接口连接
"""
import requests
import json

def test_ai_chat():
    url = 'http://localhost:5000/api/ai/chat'
    
    payload = {
        'query': '你好，请简单介绍一下自己',
        'user_id': 'test_user',
        'user_profile': {
            'username': '测试用户',
            'age': 25,
            'occupation': '工程师',
            'travel_persona': '喜欢自然风光和历史文化',
            'favorite_cities': '北京,成都,杭州'
        }
    }
    
    print("=" * 60)
    print("测试 AI Chat API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=30)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("\n" + "=" * 60)
        print("AI 响应内容:")
        print("=" * 60)
        
        if response.status_code == 200:
            # 逐行读取流式响应
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    print(line_str)
                    
                    # 尝试解析JSON
                    if line_str.startswith('data:'):
                        data_str = line_str[5:].strip()
                        if data_str:
                            try:
                                data = json.loads(data_str)
                                if data.get('type') == 'answer' and data.get('content'):
                                    print(f"[内容片段]: {data.get('content')}")
                            except:
                                pass
        else:
            print(f"错误: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 连接错误: 无法连接到后端服务")
        print(f"   请确保后端服务正在运行: python backend/app.py")
        print(f"   错误详情: {e}")
        
    except requests.exceptions.Timeout as e:
        print(f"\n❌ 请求超时: AI 服务响应太慢")
        print(f"   错误详情: {e}")
        
    except Exception as e:
        print(f"\n❌ 未知错误: {type(e).__name__}")
        print(f"   错误详情: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ai_chat()
