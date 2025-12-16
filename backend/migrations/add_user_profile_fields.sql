-- 添加用户资料扩展字段
-- 执行时间：2025-12-15
-- 说明：为 users 表添加年龄、职业、个人简介、头像、更新时间等字段

USE travel_system;

-- 添加年龄字段
ALTER TABLE users 
ADD COLUMN age INT NULL COMMENT '年龄' AFTER email;

-- 添加职业字段
ALTER TABLE users 
ADD COLUMN occupation VARCHAR(100) NULL COMMENT '职业' AFTER age;

-- 添加个人简介字段
ALTER TABLE users 
ADD COLUMN bio TEXT NULL COMMENT '个人简介' AFTER occupation;

-- 添加头像URL字段
ALTER TABLE users 
ADD COLUMN avatar VARCHAR(500) NULL COMMENT '头像URL' AFTER bio;

-- 添加最后更新时间字段
ALTER TABLE users 
ADD COLUMN updated_at DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间' AFTER created_at;

-- 验证表结构
DESCRIBE users;
