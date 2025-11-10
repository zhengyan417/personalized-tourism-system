-- 为 attractions / facilities 添加唯一索引，防止 (name, latitude, longitude) 重复
-- 执行前：请确保已清理现有重复，否则会失败
-- 执行前：USE travel_system;

-- attractions 唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS ux_attractions_name_lat_lon
  ON attractions(name, latitude, longitude);

-- facilities 唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS ux_facilities_name_lat_lon
  ON facilities(name, latitude, longitude);
