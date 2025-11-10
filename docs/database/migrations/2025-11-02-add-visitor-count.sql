-- 迁移：为 attractions / facilities 增加 visitor_count 字段与索引
-- 执行前请：USE travel_system;

ALTER TABLE attractions
  ADD COLUMN IF NOT EXISTS visitor_count INT NOT NULL DEFAULT 0 COMMENT '近一段时间访客数（热门推荐使用）';

CREATE INDEX IF NOT EXISTS idx_visitor_count ON attractions(visitor_count);

ALTER TABLE facilities
  ADD COLUMN IF NOT EXISTS visitor_count INT NOT NULL DEFAULT 0 COMMENT '近一段时间访客数（热门推荐使用）';

CREATE INDEX IF NOT EXISTS idx_fac_visitor_count ON facilities(visitor_count);
