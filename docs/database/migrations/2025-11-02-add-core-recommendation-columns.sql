-- 迁移：为 attractions / facilities 增加推荐相关核心字段
-- 如果你还没有这些列，执行本脚本即可；已存在则跳过。
-- 执行前：USE travel_system;

-- attractions 增加列
ALTER TABLE attractions
  ADD COLUMN IF NOT EXISTS popularity INT NOT NULL DEFAULT 0 COMMENT '热度（访问/权重）',
  ADD COLUMN IF NOT EXISTS avg_rating DECIMAL(3,2) NULL COMMENT '平均评分（0.00-5.00）',
  ADD COLUMN IF NOT EXISTS rating_count INT NOT NULL DEFAULT 0 COMMENT '评分人数',
  ADD COLUMN IF NOT EXISTS image_url VARCHAR(255) NULL COMMENT '图片地址（可选）';

-- attractions 索引（若支持 IF NOT EXISTS）
CREATE INDEX IF NOT EXISTS idx_popularity ON attractions(popularity);
CREATE INDEX IF NOT EXISTS idx_rating ON attractions(avg_rating);

-- facilities 表（若不存在则创建，包含完整字段）
CREATE TABLE IF NOT EXISTS facilities (
    facility_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '设施唯一标识',
    name VARCHAR(100) NOT NULL COMMENT '设施名称',
    category VARCHAR(50) COMMENT '设施类别',
    latitude DOUBLE COMMENT '纬度',
    longitude DOUBLE COMMENT '经度',
    description TEXT COMMENT '设施描述',
    popularity INT NOT NULL DEFAULT 0 COMMENT '热度（访问/权重）',
    avg_rating DECIMAL(3,2) DEFAULT NULL COMMENT '平均评分（0.00-5.00）',
    rating_count INT NOT NULL DEFAULT 0 COMMENT '评分人数',
    image_url VARCHAR(255) DEFAULT NULL COMMENT '图片地址（可选）',
    visitor_count INT NOT NULL DEFAULT 0 COMMENT '访客数（热门推荐用）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设施信息表';

-- facilities 索引（若支持 IF NOT EXISTS）
CREATE INDEX IF NOT EXISTS idx_fac_lat_lon ON facilities(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_fac_category ON facilities(category);
CREATE INDEX IF NOT EXISTS idx_fac_popularity ON facilities(popularity);
CREATE INDEX IF NOT EXISTS idx_fac_rating ON facilities(avg_rating);
CREATE INDEX IF NOT EXISTS idx_fac_visitor_count ON facilities(visitor_count);
