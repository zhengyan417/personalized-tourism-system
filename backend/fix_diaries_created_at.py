#!/usr/bin/env python3
"""
修复 diaries 表字段问题
将 create_time 字段统一改为 created_at（如果不存在则添加）
"""
import pymysql
from config import Config


def run_migration():
    """执行数据库迁移"""
    print("开始修复 diaries 表字段...")

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
            # 检查 diaries 表的字段
            cursor.execute(
                """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'diaries'
                AND COLUMN_NAME IN ('create_time', 'created_at')
            """,
                (Config.MYSQL_DB,),
            )

            existing_columns = [row["COLUMN_NAME"] for row in cursor.fetchall()]
            print(f"现有的时间字段: {existing_columns}")

            # 如果有 create_time 但没有 created_at，则重命名
            if (
                "create_time" in existing_columns
                and "created_at" not in existing_columns
            ):
                print("正在将 create_time 重命名为 created_at...")
                cursor.execute(
                    """
                    ALTER TABLE diaries 
                    CHANGE COLUMN create_time created_at 
                    DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
                """
                )
                print("✓ 字段重命名成功")

            # 如果两个字段都不存在，则添加 created_at
            elif (
                "created_at" not in existing_columns
                and "create_time" not in existing_columns
            ):
                print("正在添加 created_at 字段...")
                cursor.execute(
                    """
                    ALTER TABLE diaries 
                    ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
                """
                )
                print("✓ created_at 字段添加成功")

            # 如果已经有 created_at，跳过
            elif "created_at" in existing_columns:
                print("⊙ created_at 字段已存在，跳过")

            # 提交事务
            conn.commit()

            # 显示最终表结构
            print("\n当前 diaries 表结构:")
            cursor.execute("DESCRIBE diaries")
            for row in cursor.fetchall():
                print(
                    f"  {row['Field']:20} {row['Type']:30} {row['Null']:5} {row['Default']}"
                )

            print("\n✅ 修复完成！")

    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
