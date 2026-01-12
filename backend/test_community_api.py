import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_public_diaries():
    """测试获取公开日记列表"""
    print("\n" + "="*50)
    print("测试: 获取公开日记列表")
    print("="*50)
    
    url = f"{BASE_URL}/api/diaries/public"
    params = {
        "page": 1,
        "limit": 10
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功!")
            print(f"\n返回数据:")
            print(f"  - 成功标识: {data.get('success')}")
            print(f"  - 日记数量: {data.get('count')}")
            print(f"  - 总数: {data.get('total')}")
            print(f"  - 当前页: {data.get('page')}")
            print(f"  - 每页数量: {data.get('limit')}")
            
            diaries = data.get('data', [])
            if diaries:
                print(f"\n前3篇日记预览:")
                for i, diary in enumerate(diaries[:3], 1):
                    print(f"\n  {i}. {diary.get('title')}")
                    print(f"     作者: {diary.get('username')}")
                    print(f"     日期: {diary.get('date')}")
                    print(f"     地点: {diary.get('attraction_name') or '无'}")
                    print(f"     内容预览: {diary.get('snippet', '')[:50]}...")
            else:
                print(f"\n⚠️  暂无日记数据")
        else:
            print(f"❌ 请求失败")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到后端服务 ({BASE_URL})")
        print(f"   请确保后端服务已启动!")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_user_diaries():
    """测试获取指定用户的日记"""
    print("\n" + "="*50)
    print("测试: 获取指定用户的日记")
    print("="*50)
    
    url = f"{BASE_URL}/api/diaries"
    params = {
        "user_id": 1  # 测试用户ID
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 请求成功!")
            print(f"\n用户 ID={params['user_id']} 的日记:")
            print(f"  - 日记数量: {data.get('count')}")
            
            diaries = data.get('data', [])
            if diaries:
                for i, diary in enumerate(diaries[:3], 1):
                    print(f"\n  {i}. {diary.get('title')}")
                    print(f"     日期: {diary.get('date')}")
            else:
                print(f"\n  该用户暂无日记")
        else:
            print(f"❌ 请求失败")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到后端服务")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    print("\n🔍 开始测试旅行社区API")
    print(f"后端地址: {BASE_URL}")
    
    test_public_diaries()
    test_user_diaries()
    
    print("\n" + "="*50)
    print("✅ 测试完成!")
    print("="*50 + "\n")
