-- 添加旅游画像与偏好城市字段
-- 执行时间：2025-12-16
-- 说明：为 users 表补充 travel_persona（旅游画像）与 favorite_cities（常去/心仪城市清单）字段

USE travel_system;

ALTER TABLE users
    ADD COLUMN travel_persona VARCHAR(255) NULL COMMENT '旅游画像/出行偏好' AFTER avatar,
    ADD COLUMN favorite_cities TEXT NULL COMMENT '常去或心仪的旅游城市列表' AFTER travel_persona;

-- 检查表结构
DESCRIBE users;
