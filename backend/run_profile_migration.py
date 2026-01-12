import pymysql
from config import Config

# 直接连接数据库
conn = pymysql.connect(
    host=Config.MYSQL_HOST,
    port=Config.MYSQL_PORT,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DB
)

try:
    with conn.cursor() as cur:
        print("=== 执行迁移：添加 travel_persona 和 favorite_cities 字段 ===")
        
        # 检查字段是否已存在
        cur.execute("SHOW COLUMNS FROM users LIKE 'travel_persona'")
        if cur.fetchone():
            print("✓ travel_persona 字段已存在")
        else:
            cur.execute("ALTER TABLE users ADD COLUMN travel_persona VARCHAR(255) NULL COMMENT '旅游画像/出行偏好' AFTER avatar")
            print("✓ 已添加 travel_persona 字段")
        
        cur.execute("SHOW COLUMNS FROM users LIKE 'favorite_cities'")
        if cur.fetchone():
            print("✓ favorite_cities 字段已存在")
        else:
            cur.execute("ALTER TABLE users ADD COLUMN favorite_cities TEXT NULL COMMENT '常去或心仪的旅游城市列表' AFTER travel_persona")
            print("✓ 已添加 favorite_cities 字段")
        
        conn.commit()
        
        # 验证
        print("\n=== 验证表结构 ===")
        cur.execute('DESCRIBE users')
        for row in cur.fetchall():
            print(row)
        
        print("\n✅ 迁移完成！")
except Exception as e:
    print(f"❌ 迁移失败: {e}")
    conn.rollback()
finally:
    conn.close()
