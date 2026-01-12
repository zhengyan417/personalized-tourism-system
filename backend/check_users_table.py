import pymysql
from config import Config

# 直接连接数据库
conn = pymysql.connect(
    host=Config.MYSQL_HOST,
    port=Config.MYSQL_PORT,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB,
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        cur.execute('DESCRIBE users')
        rows = cur.fetchall()
        print("\n=== Users Table Structure ===")
        for row in rows:
            print(f"{row['Field']}: {row['Type']} - Null:{row['Null']} - Key:{row['Key']}")
        
        print("\n=== Sample User Data ===")
        cur.execute('SELECT user_id, username, email FROM users LIMIT 1')
        sample = cur.fetchone()
        if sample:
            print(f"Sample user: {sample}")
        else:
            print("No users found in database")
finally:
    conn.close()


