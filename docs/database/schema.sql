/*
 * 文件路径：/docs/database/schema.sql
 * 项目名称：个性化旅游系统
 * 模块负责人：C 同学
 * 版本：v1.0
 * 日期：第6周
 * 说明：
 *   本文件定义系统核心数据库结构，包括：
 *   - users：用户信息表
 *   - attractions：景点信息表
 *   - routes：路线信息表
 *   - diaries：旅游日记表
 * 
 *   本设计兼顾数据规范性与查询性能，符合第三范式。
 */

-- ===============================================
-- 一、创建数据库
-- ===============================================
CREATE DATABASE IF NOT EXISTS travel_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE travel_system;

-- ===============================================
-- 二、用户表：users
-- ===============================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户唯一标识',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE COMMENT '电子邮箱',
    password VARCHAR(255) NOT NULL COMMENT '加密后密码',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- ===============================================
-- 三、景点表：attractions
-- ===============================================
DROP TABLE IF EXISTS attractions;
CREATE TABLE attractions (
    attraction_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '景点唯一标识',
    name VARCHAR(100) NOT NULL COMMENT '景点名称',
    category VARCHAR(50) COMMENT '景点类别',
    latitude DOUBLE COMMENT '纬度',
    longitude DOUBLE COMMENT '经度',
    description TEXT COMMENT '景点描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景点信息表';

-- 添加联合索引以加速范围查询
CREATE INDEX idx_lat_lon ON attractions(latitude, longitude);
CREATE INDEX idx_category ON attractions(category);

-- ===============================================
-- 四、路线表：routes
-- ===============================================
DROP TABLE IF EXISTS routes;
CREATE TABLE routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '路线唯一标识',
    user_id INT NOT NULL COMMENT '关联用户',
    route_data JSON COMMENT '路线详细数据（JSON格式）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户路线表';

CREATE INDEX idx_user_route ON routes(user_id);

-- ===============================================
-- 五、旅游日记表：diaries
-- ===============================================
DROP TABLE IF EXISTS diaries;
CREATE TABLE diaries (
    diary_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日记唯一标识',
    user_id INT NOT NULL COMMENT '所属用户',
    attraction_id INT COMMENT '关联景点',
    title VARCHAR(100) COMMENT '日记标题',
    content MEDIUMBLOB COMMENT '压缩后内容（二进制存储）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (attraction_id) REFERENCES attractions(attraction_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='旅游日记表';

CREATE INDEX idx_user_diary ON diaries(user_id);
CREATE INDEX idx_attraction_diary ON diaries(attraction_id);

-- ===============================================
-- 六、初始数据（可选）
-- ===============================================
INSERT INTO users (username, email, password)
VALUES ('admin', 'admin@example.com', '123456');

INSERT INTO attractions (name, category, latitude, longitude, description)
VALUES 
('颐和园', '景点', 39.999, 116.273, '北京著名皇家园林'),
('王府井', '美食', 39.916, 116.417, '北京热门商业街');

-- ===============================================
-- 七、完成提示
-- ===============================================
/*
 * ✅ 数据库结构创建完成。
 * 主要表：
 *   - users：用户信息
 *   - attractions：景点信息
 *   - routes：用户路线
 *   - diaries：旅游日记
 * 
 * 后续工作：
 *   - 可在 /docs/api/place-query.md 定义范围查询接口；
 *   - 可在 /docs/api/travel-diary.md 定义日记 CRUD 接口；
 *   - 可通过 Flask SQLAlchemy 或 PyMySQL 与该数据库连接。
 */
