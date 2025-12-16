import requests

# 测试登录
url_login = 'http://localhost:5000/api/auth/login'
data = {'username': 'admin', 'password': '123456'}

print("=" * 80)
print("测试用户资料功能")
print("=" * 80)

# 1. 登录
print("\n1. 登录...")
session = requests.Session()
response = session.post(url_login, json=data)
print(f"   状态码: {response.status_code}")
if response.status_code == 200:
    print("   ✅ 登录成功")
else:
    print("   ❌ 登录失败")
    exit(1)

# 2. 获取当前用户信息（包含完整资料）
print("\n2. 获取当前用户信息 (/api/auth/me)...")
response = session.get('http://localhost:5000/api/auth/me')
print(f"   状态码: {response.status_code}")
me_data = response.json()
print(f"   用户数据: {me_data['data']}")

# 3. 获取用户资料
print("\n3. 获取用户资料 (/api/auth/profile)...")
response = session.get('http://localhost:5000/api/auth/profile')
print(f"   状态码: {response.status_code}")
profile_data = response.json()
print(f"   资料数据: {profile_data['data']}")

# 4. 更新用户资料
print("\n4. 更新用户资料...")
update_data = {
    'age': 25,
    'occupation': '软件工程师',
    'bio': '热爱旅行和编程，喜欢探索新事物。',
    'avatar': 'https://example.com/avatar.jpg'
}
response = session.put('http://localhost:5000/api/auth/profile', json=update_data)
print(f"   状态码: {response.status_code}")
result = response.json()
print(f"   更新结果: {result['message']}")

# 5. 再次获取资料验证更新
print("\n5. 验证更新后的资料...")
response = session.get('http://localhost:5000/api/auth/profile')
updated_profile = response.json()
print(f"   年龄: {updated_profile['data']['age']}")
print(f"   职业: {updated_profile['data']['occupation']}")
print(f"   简介: {updated_profile['data']['bio']}")
print(f"   头像: {updated_profile['data']['avatar']}")

# 6. 获取日记（验证用户名显示）
print("\n6. 获取日记列表（验证用户名显示）...")
response = session.get('http://localhost:5000/api/diaries?user_id=1')
if response.status_code == 200:
    diaries_data = response.json()
    if diaries_data.get('success') and diaries_data.get('data'):
        diary_list = diaries_data['data']
        print(f"   找到 {len(diary_list)} 条日记")
        if len(diary_list) > 0:
            first_diary = diary_list[0]
            print(f"   第一条日记:")
            print(f"     标题: {first_diary.get('title')}")
            print(f"     用户名: {first_diary.get('username')} ✅")
            print(f"     用户头像: {first_diary.get('user_avatar')} ✅")
            print(f"     内容: {first_diary.get('snippet')}")
    else:
        print(f"   暂无日记")
else:
    print(f"   获取失败: {response.status_code}")

print("\n" + "=" * 80)
print("✅ 测试完成！")
print("=" * 80)
