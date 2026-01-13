#!/usr/bin/env python3
"""
执行旅游画像字段迁移脚本
添加 travel_persona 和 favorite_cities 字段到 users 表
"""
import pymysql
from config import Config


def run_migration():
    """执行数据库迁移"""
    print("开始执行旅游画像字段迁移...")

    # 连接数据库
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with conn.cursor() as cursor:
            # 先检查字段是否已存在
            cursor.execute(
                """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME IN ('travel_persona', 'favorite_cities')
            """,
                (Config.MYSQL_DB,),
            )

            existing_columns = [row["COLUMN_NAME"] for row in cursor.fetchall()]
            print(f"已存在的字段: {existing_columns}")

            # 添加 travel_persona 字段
            if "travel_persona" not in existing_columns:
                print("正在添加 travel_persona 字段...")
                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN travel_persona VARCHAR(255) NULL 
                    COMMENT '旅游画像/出行偏好' 
                    AFTER avatar
                """
                )
                print("✓ travel_persona 字段添加成功")
            else:
                print("⊙ travel_persona 字段已存在，跳过")

            # 添加 favorite_cities 字段
            if "favorite_cities" not in existing_columns:
                print("正在添加 favorite_cities 字段...")
                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN favorite_cities TEXT NULL 
                    COMMENT '常去或心仪的旅游城市列表' 
                    AFTER travel_persona
                """
                )
                print("✓ favorite_cities 字段添加成功")
            else:
                print("⊙ favorite_cities 字段已存在，跳过")

            # 提交事务
            conn.commit()

            # 显示最终表结构
            print("\n当前 users 表结构:")
            cursor.execute("DESCRIBE users")
            for row in cursor.fetchall():
                print(
                    f"  {row['Field']:20} {row['Type']:30} {row['Null']:5} {row['Key']:5} {row['Default']}"
                )

            print("\n✅ 迁移完成！")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
