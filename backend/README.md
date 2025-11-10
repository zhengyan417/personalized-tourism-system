# 后端（Flask）使用说明与开发指南

本目录为“个性化旅游系统”的后端服务，基于 Flask + PyMySQL，提供景点查询、邻近检索、旅游日记、路径规划与推荐等 API。后续可通过 pybind11 对接 C++ 核心算法模块。

## 环境要求

- Python 3.10/3.11（Windows/Linux/macOS）
- MySQL 8.0（建议 utf8mb4）
- 推荐安装工具：pip、virtualenv、VS Code

## 快速开始

1) 创建并激活虚拟环境（可选）

```cmd
cd /d c:\code\travel\backend
python -m venv .venv
.venv\Scripts\activate
```

2) 安装依赖

```cmd
pip install -r requirements.txt
```

3) 初始化数据库（首次）

```sql
-- 在 MySQL 客户端中执行：
SOURCE c:/code/travel/docs/database/schema.sql;
```

可选：如果你已存在旧库，需要补齐“热度/评分/设施表”等第7周之后新增的字段/表，执行迁移脚本：

```sql
SOURCE c:/code/travel/docs/database/migrations/2025-11-02-add-rating-popularity.sql;
```

4) 导入数据

```cmd
cd /d c:\code\travel\backend
python -m app.utils.data_import
```

默认读取：
- `docs/database/attractions_data.csv`
- `docs/database/facilities_data.csv`（可选，存在则导入）

CSV 支持以下列（列名不区分顺序，部分可选）：
- 必选：name, category, latitude, longitude, description
- 可选：popularity, avg_rating, rating_count, image_url

5) 启动后端服务

```cmd
cd /d c:\code\travel\backend
python app.py
```

默认监听 `http://127.0.0.1:5000`。

## 配置项（app/utils/database.py）

在 `app/utils/database.py` 中配置 MySQL 连接（host/user/password/database/charset）。推荐通过环境变量覆盖，或在生产环境使用更安全的配置管理。

## 主要目录结构

```
backend/
	app/
		routes/         # 各模块路由（place_query, route_planning, travel_diary, recommendation 等）
		services/       # 业务服务层
		models/         # 数据模型（可选）
		utils/          # 数据库、导入脚本、工具函数
	requirements.txt
	app.py           # Flask 入口
```

## 提供的核心 API（部分）

1) 景点查询（place_query）
- GET `/api/places/`：可选参数 `category`、`keyword`
- GET `/api/places/<attraction_id>`：按 ID 查询
- GET `/api/places/nearby?lat=..&lon=..&radius=..&category=..`：邻近查询

返回字段示例（部分）：
```json
{
	"attraction_id": 1,
	"name": "颐和园",
	"category": "景点",
	"latitude": 39.999,
	"longitude": 116.273,
	"description": "北京著名皇家园林",
	"popularity": 1200,
	"avg_rating": 4.7,
	"rating_count": 356,
	"image_url": null,
	"distance_km": 2.35
}
```

2) 旅游日记（travel_diary）
http://127.0.0.1:5000/api/diaries/?user_id=1
- GET/POST/PUT/DELETE 按 Blueprint 提供标准 CRUD（压缩存储内容）

3) 路径规划（route_planning）
- GET/POST 支持表单或 JSON 传参，使用 Haversine 距离做简化示例

4) 推荐（recommendation）
- 后续将接入 C++ 核心算法（pybind11），当前可提供占位或回退逻辑

## 第6周 / 第7周 后端任务完成度核查

对照《week-6.md》《week-7.md》：

- ER 图与表结构：`docs/database/schema.sql` 已提供 users、attractions、routes、diaries；第7周新增 facilities 与 attractions 的热度/评分列，并提供迁移脚本（见 migrations）。
- 数据导入脚本：`app/utils/data_import.py` 可导入景点与设施数据，支持 `popularity/avg_rating/rating_count/image_url` 可选列。
- API 基础框架：`app/routes/` 下已包含 place_query、travel_diary、route_planning 等 Blueprint；place_query 支持邻近查询与去重（描述级合并）。
- 数据完整性：建议在导入 CSV 前检查必填字段（当前脚本已进行基本的字段读取与默认处理）。
- 核心缺口：
	- 设施 API 尚未提供专门的 `GET /api/facilities/...` 路由（可后续补充）。
	- `sample_data.sql` 暂为空；如需一键演示，可补充 10~20 条示例数据。

## 常见问题（FAQ）

1) 运行时报错“找不到表/列”
- 请先执行 `schema.sql`，若是从老库升级请执行 `migrations/2025-11-02-*.sql`。

2) 邻近查询无结果
- 检查传入经纬度/半径，确认表中对应记录的经纬度不为空。

3) 中文乱码
- 确保 MySQL 使用 `utf8mb4` 字符集，连接参数包含 `charset=utf8mb4`。

4) 请求超时
- 默认 Flask 开发服为单进程，推荐生产使用 `waitress` 或 `gunicorn`，并开启连接池与索引（已在 schema 中为常用字段建索引）。

## 后续计划（与第8周目标衔接）

- C++ 推荐核心接入：通过 pybind11 封装堆排序、倒排索引等，提供 Top-10、关键词检索；后端保留 Python 回退逻辑。
- 推荐 API：`GET /api/recommendations`（Top-10，支持 `order_by=popularity|avg_rating|distance`），`GET /api/recommendations/search?q=...`，`POST /api/preferences`。
- 数据缓存与并发：引入简单缓存（如 LRU 或 Redis），并优化连接池/并发处理。

---

如需一键联调前端，请在 `frontend/.env.development` 配置：

```
VUE_APP_API_BASE_URL=http://localhost:5000
VUE_APP_USE_MOCK=false
```

前端本地启动后，`/api/places/nearby` 等接口将直接访问本后端。
