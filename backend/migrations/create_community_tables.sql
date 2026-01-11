-- ===============================================
-- 社区功能数据库表
-- 功能：日记点赞、评论、关注等社交功能
-- ===============================================

USE travel_system;

-- 1. 日记点赞表
CREATE TABLE IF NOT EXISTS diary_likes (
    like_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '点赞唯一标识',
    diary_id INT NOT NULL COMMENT '日记ID',
    user_id INT NOT NULL COMMENT '点赞用户ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    UNIQUE KEY uk_diary_user (diary_id, user_id) COMMENT '同一用户对同一日记只能点赞一次',
    FOREIGN KEY (diary_id) REFERENCES diaries(diary_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日记点赞表';

CREATE INDEX idx_diary_likes_diary ON diary_likes(diary_id);
CREATE INDEX idx_diary_likes_user ON diary_likes(user_id);

-- 2. 日记评论表
CREATE TABLE IF NOT EXISTS diary_comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评论唯一标识',
    diary_id INT NOT NULL COMMENT '日记ID',
    user_id INT NOT NULL COMMENT '评论用户ID',
    content TEXT NOT NULL COMMENT '评论内容',
    parent_id INT DEFAULT NULL COMMENT '父评论ID（用于回复）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
    FOREIGN KEY (diary_id) REFERENCES diaries(diary_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES diary_comments(comment_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日记评论表';

CREATE INDEX idx_diary_comments_diary ON diary_comments(diary_id);
CREATE INDEX idx_diary_comments_user ON diary_comments(user_id);
CREATE INDEX idx_diary_comments_parent ON diary_comments(parent_id);

-- 3. 用户关注表
CREATE TABLE IF NOT EXISTS user_follows (
    follow_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '关注唯一标识',
    follower_id INT NOT NULL COMMENT '粉丝ID',
    following_id INT NOT NULL COMMENT '被关注用户ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '关注时间',
    UNIQUE KEY uk_follower_following (follower_id, following_id) COMMENT '防止重复关注',
    FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户关注表';

CREATE INDEX idx_user_follows_follower ON user_follows(follower_id);
CREATE INDEX idx_user_follows_following ON user_follows(following_id);

-- 4. 为 diaries 表添加统计字段
-- 使用存储过程来安全地添加列
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS add_diary_columns()
BEGIN
    -- 添加 like_count
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='diaries' AND COLUMN_NAME='like_count') THEN
        ALTER TABLE diaries ADD COLUMN like_count INT DEFAULT 0 COMMENT '点赞数';
    END IF;
    
    -- 添加 comment_count
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='diaries' AND COLUMN_NAME='comment_count') THEN
        ALTER TABLE diaries ADD COLUMN comment_count INT DEFAULT 0 COMMENT '评论数';
    END IF;
    
    -- 添加 view_count
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='diaries' AND COLUMN_NAME='view_count') THEN
        ALTER TABLE diaries ADD COLUMN view_count INT DEFAULT 0 COMMENT '浏览数';
    END IF;
    
    -- 添加 is_public
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='diaries' AND COLUMN_NAME='is_public') THEN
        ALTER TABLE diaries ADD COLUMN is_public TINYINT(1) DEFAULT 1 COMMENT '是否公开（1=公开，0=私密）';
    END IF;
END$$
DELIMITER ;

CALL add_diary_columns();
DROP PROCEDURE IF EXISTS add_diary_columns;

-- 5. 为 users 表添加统计字段
DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS add_user_columns()
BEGIN
    -- 添加 follower_count
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='users' AND COLUMN_NAME='follower_count') THEN
        ALTER TABLE users ADD COLUMN follower_count INT DEFAULT 0 COMMENT '粉丝数';
    END IF;
    
    -- 添加 following_count
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='users' AND COLUMN_NAME='following_count') THEN
        ALTER TABLE users ADD COLUMN following_count INT DEFAULT 0 COMMENT '关注数';
    END IF;
    
    -- 添加 diary_count
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='users' AND COLUMN_NAME='diary_count') THEN
        ALTER TABLE users ADD COLUMN diary_count INT DEFAULT 0 COMMENT '日记数';
    END IF;
    
    -- 添加 nickname
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='users' AND COLUMN_NAME='nickname') THEN
        ALTER TABLE users ADD COLUMN nickname VARCHAR(50) DEFAULT NULL COMMENT '昵称';
    END IF;
    
    -- 添加 avatar_url
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='users' AND COLUMN_NAME='avatar_url') THEN
        ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255) DEFAULT NULL COMMENT '头像URL';
    END IF;
    
    -- 添加 bio
    IF NOT EXISTS (SELECT * FROM information_schema.COLUMNS 
                  WHERE TABLE_SCHEMA='travel_system' AND TABLE_NAME='users' AND COLUMN_NAME='bio') THEN
        ALTER TABLE users ADD COLUMN bio TEXT DEFAULT NULL COMMENT '个人简介';
    END IF;
END$$
DELIMITER ;

CALL add_user_columns();
DROP PROCEDURE IF EXISTS add_user_columns;

-- 6. 创建触发器：点赞时更新日记点赞数
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS trg_diary_like_insert
AFTER INSERT ON diary_likes
FOR EACH ROW
BEGIN
    UPDATE diaries SET like_count = like_count + 1 WHERE diary_id = NEW.diary_id;
END$$

CREATE TRIGGER IF NOT EXISTS trg_diary_like_delete
AFTER DELETE ON diary_likes
FOR EACH ROW
BEGIN
    UPDATE diaries SET like_count = like_count - 1 WHERE diary_id = OLD.diary_id;
END$$
DELIMITER ;

-- 7. 创建触发器：评论时更新日记评论数
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS trg_diary_comment_insert
AFTER INSERT ON diary_comments
FOR EACH ROW
BEGIN
    UPDATE diaries SET comment_count = comment_count + 1 WHERE diary_id = NEW.diary_id;
END$$

CREATE TRIGGER IF NOT EXISTS trg_diary_comment_delete
AFTER DELETE ON diary_comments
FOR EACH ROW
BEGIN
    UPDATE diaries SET comment_count = comment_count - 1 WHERE diary_id = OLD.diary_id;
END$$
DELIMITER ;

-- 8. 创建触发器：关注时更新用户统计
DELIMITER $$
CREATE TRIGGER IF NOT EXISTS trg_user_follow_insert
AFTER INSERT ON user_follows
FOR EACH ROW
BEGIN
    UPDATE users SET following_count = following_count + 1 WHERE user_id = NEW.follower_id;
    UPDATE users SET follower_count = follower_count + 1 WHERE user_id = NEW.following_id;
END$$

CREATE TRIGGER IF NOT EXISTS trg_user_follow_delete
AFTER DELETE ON user_follows
FOR EACH ROW
BEGIN
    UPDATE users SET following_count = following_count - 1 WHERE user_id = OLD.follower_id;
    UPDATE users SET follower_count = follower_count - 1 WHERE user_id = OLD.following_id;
END$$
DELIMITER ;

-- 9. 插入测试数据
-- 确保有一些测试用户
INSERT IGNORE INTO users (user_id, username, email, password, nickname) VALUES
(1, 'caipj315', 'cai@example.com', 'pbkdf2:sha256:600000$EQ8rAukz$10bc7e03e01c8ac6c9a8ea9ebee8ca4cf2b1fe46d3e00c8799debb8b2fbecc5e', '旅行达人小蔡'),
(2, 'traveler01', 'traveler01@example.com', 'pbkdf2:sha256:600000$salt123$hash123', '环球旅行家'),
(3, 'foodlover', 'food@example.com', 'pbkdf2:sha256:600000$salt456$hash456', '美食探索者'),
(4, 'photographer', 'photo@example.com', 'pbkdf2:sha256:600000$salt789$hash789', '风光摄影师');

-- 插入一些测试日记（确保是公开的）
INSERT IGNORE INTO diaries (diary_id, user_id, title, content, latitude, longitude, is_public, like_count, comment_count, view_count) VALUES
(1, 2, '北京颐和园一日游', COMPRESS('今天去了颐和园，风景非常美丽！昆明湖波光粼粼，长廊画栋雕梁，真是不虚此行。推荐大家一定要来看看！'), 39.999, 116.273, 1, 15, 3, 128),
(2, 3, '王府井美食探店', COMPRESS('在王府井找到了超好吃的烤鸭！外皮酥脆，肉质鲜嫩，配上甜面酱简直绝了。还尝试了炸酱面和豆汁，很有北京特色。'), 39.916, 116.417, 1, 23, 5, 256),
(3, 4, '故宫的日落', COMPRESS('傍晚时分的故宫格外美丽，夕阳洒在红墙金瓦上，整个紫禁城都被染成了金色。作为摄影爱好者，这里是绝佳的拍摄地点！'), 39.9163, 116.3972, 1, 31, 8, 512),
(4, 2, '长城徒步记', COMPRESS('今天挑战了八达岭长城，虽然很累但非常值得！站在烽火台上远眺，感受到了古人的智慧和毅力。秋天的长城层林尽染，景色壮观。'), 40.3586, 116.0149, 1, 28, 6, 384);

-- 插入一些测试点赞
INSERT IGNORE INTO diary_likes (diary_id, user_id) VALUES
(1, 1), (1, 3), (1, 4),
(2, 1), (2, 2), (2, 4),
(3, 1), (3, 2), (3, 3),
(4, 1), (4, 3);

-- 插入一些测试评论
INSERT IGNORE INTO diary_comments (comment_id, diary_id, user_id, content) VALUES
(1, 1, 1, '拍的真好！我下周也要去'),
(2, 1, 3, '颐和园确实很美，上次去就很震撼'),
(3, 2, 1, '请问具体是哪家烤鸭店？'),
(4, 2, 2, '王府井的小吃真的很多'),
(5, 3, 1, '这个角度太赞了！'),
(6, 3, 2, '摄影大师！求教参数'),
(7, 4, 1, '爬长城要准备什么装备吗？'),
(8, 4, 4, '秋天去长城最合适了');

-- 插入一些测试关注关系
INSERT IGNORE INTO user_follows (follower_id, following_id) VALUES
(1, 2), (1, 3), (1, 4),
(2, 3), (2, 4),
(3, 2), (3, 4),
(4, 2);

-- ===============================================
-- 完成！
-- ===============================================
SELECT '社区功能数据库表创建完成！' AS status;
