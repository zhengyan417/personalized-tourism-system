````markdown
# 前端所需 HTTP API 规范（前后端对接参考）

本文件列出了前端在当前功能（首页/附近/推荐/路径规划/旅行日记）中依赖的后端接口定义、请求/响应示例和注意事项，供后端实现或 Mock 使用。

通用约定：
- 所有接口前缀统一为 `/api`。
- 请求/响应均使用 JSON（Content-Type: application/json）。
- 成功返回 HTTP 200，并在 body 中包含数据（具体接口另行说明）。错误返回合适的 4xx/5xx 状态，并包含 `{ code: string, message: string, details?: any }`。

---

## 1. 场所（Places）

### 1.1 查询附近场所
- 路径：`GET /api/places/nearby`
- 描述：基于经纬度和半径查询附近景点/POI
- 参数（Query）：
  - `lat` (number, required)：纬度
  - `lon` (number, required)：经度
  - `radius` (number, optional, km)：半径（km），默认 5
  - `category` (string, optional)：类别过滤
  - `limit` (integer, optional)：最大返回条数，默认 100
- 响应示例：

```json
{
  "items": [
    { "id": 123, "name": "故宫", "latitude": 39.916345, "longitude": 116.397155, "category": "历史景点", "distance_km": 1.23 }
  ],
  "count": 1
}
```

注意：`distance_km` 可由后端计算并返回（保留两位小数）；若后端不返回，前端可使用 Haversine 计算。

### 1.2 场所详情
- 路径：`GET /api/places/{id}`
- 描述：获取单个场所详情
- 响应示例：

```json
{
  "id": 123,
  "name": "故宫",
  "latitude": 39.916345,
  "longitude": 116.397155,
  "category": "历史景点",
  "description": "…",
  "images": ["/static/img/1.jpg"]
}
```

### 1.3 类别列表
- 路径：`GET /api/places/categories`
- 描述：返回可用的类别字符串数组（用于前端下拉/筛选）
- 响应示例：

```json
["历史景点", "自然风光", "美食", "博物馆"]
```

### 1.4 根据中心点查找地图中心最近点（可选）
- 路径：`GET /api/places/nearest?lat={lat}&lon={lon}`
- 描述：返回与给定坐标最近的 1-5 个场所，便于“取地图中心”后做最近点联动
- 响应示例：同 `/api/places/nearby` 的 items 列表

---

## 2. 推荐（Recommendations）

### 2.1 获取推荐列表
- 路径：`GET /api/recommendations`
- 描述：基于用户/偏好返回推荐场所列表
- 参数（Query）：
  - `user_id` (int, optional)
  - `algorithm` (string, optional) : `content_based`|`collaborative`（默认 `content_based`）
  - `top_n` (int, optional)：返回数量
  - `lat`/`lon` (number, optional)：可提供位置进行就近排序
- 响应示例：

```json
{
  "items": [
    { "attraction_id": 201, "name": "颐和园", "latitude": 39.999, "longitude": 116.275, "type": "历史景点", "score": 0.92, "popularity": 1234 }
  ]
}
```

### 2.2 搜索推荐（关键词）
- 路径：`GET /api/recommendations/search?query={q}&limit={n}`
- 描述：按关键词搜索并返回结果（用于顶部搜索框）

### 2.3 可选：热门/榜单接口
- 路径：`GET /api/recommendations/hot?limit=10`

注意：前端需要 `attraction_id`/`id`、`name`、`latitude`、`longitude`、`type`/`category`、可选 `score`/`popularity`/`rating` 字段。

---

## 3. 路径规划（Route Planning）

> 前端目前使用简单规划接口：提交起点、终点与途经点（id 或坐标），后端返回一条或多条路径供前端渲染。

### 3.1 规划路线
- 路径：`POST /api/route/plan`
- 描述：计算路线，返回路径多段几何（用于在地图上绘制）
- 请求体示例：

```json
{
  "start": { "id": "123", "latitude": 39.9, "longitude": 116.3 },
  "end":   { "id": "456", "latitude": 39.92, "longitude": 116.4 },
  "waypoints": [ { "id": "wp1", "latitude": 39.91, "longitude": 116.35 } ],
  "mode": "walking",            // optional: walking|cycling|driving
  "optimize": "fastest"        // optional
}
```

- 成功响应示例：

```json
{
  "routes": [
    {
      "id": "route-abc",
      "path": [[39.9,116.3],[39.905,116.31],[39.92,116.4]],
      "legs": [ { "distance_m": 1500, "duration_s": 1200 } ],
      "summary": { "distance_m": 1500, "duration_s": 1200 }
    }
  ],
  "total_distance_km": 1.5
}
```

响应约定（前端期望）：
- `path`: 数组形式的 [lat, lon] 列表，前端直接传入 `BaseMap` 的 `plannedPath`。
- `summary` 或顶级 `total_distance_km`：用于在 UI 显示总距离/时间估算。

### 3.2 Mock / 简化版本
- 为便于前端早期开发，后端可提供 `planSimple`，接受与上面相同的请求，但返回基于直线插值的简单路径（不做路网计算）。

---

## 4. 旅行日记（Travel Diary）

### 4.1 获取用户日记列表
- 路径：`GET /api/diaries?user_id={id}`
- 响描述：返回用户的日记摘要（带经纬度用于地图标记）
- 响应示例：

```json
{
  "items": [ { "id": 501, "title": "早餐在老街", "snippet": "…", "latitude": 39.9, "longitude": 116.3, "date": "2025-11-18" } ]
}
```

### 4.2 创建日记
- 路径：`POST /api/diaries`
- 请求体示例：

```json
{
  "user_id": 1,
  "title": "午后漫步",
  "content": "今天逛了公园，很惬意",
  "latitude": 39.91,
  "longitude": 116.33
}
```

- 成功响应：创建后的日记对象（含 id 与 date）

### 4.3 日记详情
- 路径：`GET /api/diaries/{id}`

---

## 5. 其他与工具性接口

- `GET /api/config`：返回前端可用的运行时配置（如 `use_mock`, `api_base_url`, `feature_flags`），便于前后端动态切换。
- `GET /api/health`：简单健康检查，返回 `{ status: "ok" }`。

---

## 6. 认证与权限（可选）

- 若服务需要用户认证，建议采用 JWT Bearer Token，通过 `Authorization: Bearer <token>` 传递。
- 对于开发阶段可暂时使用 `user_id` query/body 字段做简单隔离。

---

## 7. 提交/返回约定与注意事项
- 时间格式：统一使用 ISO-8601（UTC）字符串，例如 `2025-11-20T08:00:00Z`。
- 坐标：WGS84，经度/纬度使用小数度（double），小数精度建议 6 位（0.000001）。
- 错误返回约定：{ code: "InvalidRequest", message: "...", details: {...} }。
- 分页：若列表接口需要分页，请使用 `?limit={n}&offset={o}`。

---

如果你需要，我可以将上述规范同步到后端开发人员常用的 OpenAPI/Swagger 格式（YAML），以便自动生成 Mock server 与客户端 SDK。是否需要我把它转换为 OpenAPI 3.0 文件？

````
