import pymysql
from werkzeug.security import check_password_hash

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='lyy060519',
    database='travel_system',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()
cur.execute('SELECT user_id, username, password, email FROM users')
rows = cur.fetchall()

print('现有用户数量:', len(rows))
for r in rows:
    print(f"ID={r['user_id']}, 用户名={r['username']}, 密码长度={len(r['password'])}, 密码前缀={r['password'][:20]}, Email={r['email']}")
    
    # 检查密码是否是 werkzeug 格式
    pwd = r['password']
    if pwd.startswith('pbkdf2:sha256:'):
        print(f"  ✅ 密码格式正确 (werkzeug pbkdf2)")
    elif pwd.startswith('scrypt:'):
        print(f"  ✅ 密码格式正确 (werkzeug scrypt)")
    else:
        print(f"  ❌ 密码格式错误！可能是明文或其他格式")

cur.close()
conn.close()
