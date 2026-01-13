#!/usr/bin/env python3
"""
执行社区功能数据库迁移脚本
创建点赞、评论、关注相关表，并为 diaries 和 users 表添加统计字段
"""
import pymysql
from config import Config


def run_migration():
    """执行数据库迁移"""
    print("开始执行社区功能数据库迁移...")

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
            # 1. 创建 diary_likes 表
            print("\n1. 创建 diary_likes 表...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS diary_likes (
                    like_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '点赞唯一标识',
                    diary_id INT NOT NULL COMMENT '日记ID',
                    user_id INT NOT NULL COMMENT '点赞用户ID',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
                    UNIQUE KEY uk_diary_user (diary_id, user_id) COMMENT '同一用户对同一日记只能点赞一次',
                    KEY idx_diary_likes_diary (diary_id),
                    KEY idx_diary_likes_user (user_id),
                    FOREIGN KEY (diary_id) REFERENCES diaries(diary_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日记点赞表'
            """
            )
            print("✓ diary_likes 表创建成功")

            # 2. 创建 diary_comments 表
            print("\n2. 创建 diary_comments 表...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS diary_comments (
                    comment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评论唯一标识',
                    diary_id INT NOT NULL COMMENT '日记ID',
                    user_id INT NOT NULL COMMENT '评论用户ID',
                    content TEXT NOT NULL COMMENT '评论内容',
                    parent_id INT DEFAULT NULL COMMENT '父评论ID（用于回复）',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
                    KEY idx_diary_comments_diary (diary_id),
                    KEY idx_diary_comments_user (user_id),
                    KEY idx_diary_comments_parent (parent_id),
                    FOREIGN KEY (diary_id) REFERENCES diaries(diary_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_id) REFERENCES diary_comments(comment_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日记评论表'
            """
            )
            print("✓ diary_comments 表创建成功")

            # 3. 创建 user_follows 表
            print("\n3. 创建 user_follows 表...")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_follows (
                    follow_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '关注唯一标识',
                    follower_id INT NOT NULL COMMENT '粉丝ID',
                    following_id INT NOT NULL COMMENT '被关注用户ID',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '关注时间',
                    UNIQUE KEY uk_follower_following (follower_id, following_id) COMMENT '防止重复关注',
                    KEY idx_user_follows_follower (follower_id),
                    KEY idx_user_follows_following (following_id),
                    FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (following_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户关注表'
            """
            )
            print("✓ user_follows 表创建成功")

            # 4. 为 diaries 表添加统计字段
            print("\n4. 为 diaries 表添加统计字段...")
            cursor.execute(
                """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'diaries' 
                AND COLUMN_NAME IN ('like_count', 'comment_count', 'view_count', 'is_public')
            """,
                (Config.MYSQL_DB,),
            )

            existing_diary_columns = [row["COLUMN_NAME"] for row in cursor.fetchall()]

            if "like_count" not in existing_diary_columns:
                cursor.execute(
                    "ALTER TABLE diaries ADD COLUMN like_count INT DEFAULT 0 COMMENT '点赞数'"
                )
                print("  ✓ 添加 like_count 字段")
            else:
                print("  ⊙ like_count 字段已存在")

            if "comment_count" not in existing_diary_columns:
                cursor.execute(
                    "ALTER TABLE diaries ADD COLUMN comment_count INT DEFAULT 0 COMMENT '评论数'"
                )
                print("  ✓ 添加 comment_count 字段")
            else:
                print("  ⊙ comment_count 字段已存在")

            if "view_count" not in existing_diary_columns:
                cursor.execute(
                    "ALTER TABLE diaries ADD COLUMN view_count INT DEFAULT 0 COMMENT '浏览数'"
                )
                print("  ✓ 添加 view_count 字段")
            else:
                print("  ⊙ view_count 字段已存在")

            if "is_public" not in existing_diary_columns:
                cursor.execute(
                    "ALTER TABLE diaries ADD COLUMN is_public TINYINT(1) DEFAULT 1 COMMENT '是否公开（1=公开，0=私密）'"
                )
                print("  ✓ 添加 is_public 字段")
            else:
                print("  ⊙ is_public 字段已存在")

            # 5. 为 users 表添加统计字段
            print("\n5. 为 users 表添加统计字段...")
            cursor.execute(
                """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME IN ('nickname', 'avatar_url', 'follower_count', 'following_count')
            """,
                (Config.MYSQL_DB,),
            )

            existing_user_columns = [row["COLUMN_NAME"] for row in cursor.fetchall()]

            if "nickname" not in existing_user_columns:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN nickname VARCHAR(50) NULL COMMENT '昵称' AFTER username"
                )
                print("  ✓ 添加 nickname 字段")
            else:
                print("  ⊙ nickname 字段已存在")

            if "avatar_url" not in existing_user_columns:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500) NULL COMMENT '头像URL' AFTER nickname"
                )
                print("  ✓ 添加 avatar_url 字段")
            else:
                print("  ⊙ avatar_url 字段已存在")

            if "follower_count" not in existing_user_columns:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN follower_count INT DEFAULT 0 COMMENT '粉丝数'"
                )
                print("  ✓ 添加 follower_count 字段")
            else:
                print("  ⊙ follower_count 字段已存在")

            if "following_count" not in existing_user_columns:
                cursor.execute(
                    "ALTER TABLE users ADD COLUMN following_count INT DEFAULT 0 COMMENT '关注数'"
                )
                print("  ✓ 添加 following_count 字段")
            else:
                print("  ⊙ following_count 字段已存在")

            # 6. 创建触发器来自动更新统计字段
            print("\n6. 创建触发器...")

            # 点赞触发器
            cursor.execute("DROP TRIGGER IF EXISTS after_like_insert")
            cursor.execute(
                """
                CREATE TRIGGER after_like_insert
                AFTER INSERT ON diary_likes
                FOR EACH ROW
                UPDATE diaries SET like_count = like_count + 1 WHERE diary_id = NEW.diary_id
            """
            )

            cursor.execute("DROP TRIGGER IF EXISTS after_like_delete")
            cursor.execute(
                """
                CREATE TRIGGER after_like_delete
                AFTER DELETE ON diary_likes
                FOR EACH ROW
                UPDATE diaries SET like_count = like_count - 1 WHERE diary_id = OLD.diary_id
            """
            )
            print("  ✓ 点赞触发器创建成功")

            # 评论触发器
            cursor.execute("DROP TRIGGER IF EXISTS after_comment_insert")
            cursor.execute(
                """
                CREATE TRIGGER after_comment_insert
                AFTER INSERT ON diary_comments
                FOR EACH ROW
                UPDATE diaries SET comment_count = comment_count + 1 WHERE diary_id = NEW.diary_id
            """
            )

            cursor.execute("DROP TRIGGER IF EXISTS after_comment_delete")
            cursor.execute(
                """
                CREATE TRIGGER after_comment_delete
                AFTER DELETE ON diary_comments
                FOR EACH ROW
                UPDATE diaries SET comment_count = comment_count - 1 WHERE diary_id = OLD.diary_id
            """
            )
            print("  ✓ 评论触发器创建成功")

            # 提交事务
            conn.commit()

            print("\n✅ 社区功能数据库迁移完成！")
            print("\n已创建表:")
            print("  - diary_likes (日记点赞)")
            print("  - diary_comments (日记评论)")
            print("  - user_follows (用户关注)")
            print("\n已添加字段:")
            print("  diaries: like_count, comment_count, view_count, is_public")
            print("  users: nickname, avatar_url, follower_count, following_count")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
