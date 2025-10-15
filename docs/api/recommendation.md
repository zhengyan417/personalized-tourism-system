# 推荐模块 API 文档

  

**文件路径：** `/docs/api/recommendation.md`  

**模块负责人：** 甘和君（项目经理 & 推荐模块）  

**版本：** v1.0  

**日期：** 第6周

  

---

  

## 一、接口概述

  

推荐模块（Recommendation API）基于用户偏好、行为历史和内容特征，为用户提供个性化的景点推荐服务。该模块是"个性化旅游系统"的智能核心，为前端推荐页面和主页推荐流提供数据支持。

  

## 二、接口列表
  
|  接口名称   | 请求方式 | 路径                            | 功能说明            |
| :-----: | ---- | ----------------------------- | --------------- |
| 获取个性化推荐 | GET  | `/api/recommendations`        | 基于用户偏好获取个性化景点推荐 |
| 获取热门推荐  | GET  | `/api/recommendations/hot`    | 获取热门景点推荐（非个性化）  |
| 关键词搜索推荐 | GET  | `/api/recommendations/search` | 基于关键词的景点搜索与推荐   |

  

## 三、接口定义

  

### 1️⃣ GET /api/recommendations


#### 📘 功能描述

基于用户历史行为和偏好特征，使用堆排序算法返回Top-N个性化景点推荐列表。
  

#### 🧾 请求参数

| 参数名 | 类型 | 是否必填 | 默认值 | 说明 |
| :---: |------|----------|--------|------|
| `user_id` | int | ✅ | — | 用户ID |
| `top_n` | int | ❌ | 10 | 返回推荐数量（使用堆排序优化） |
| `algorithm` | string | ❌ | "content_based" | 推荐算法类型：`content_based`(基于内容) / `collaborative`(协同过滤) |


#### 📥 请求示例

```http

GET /api/recommendations?user_id=123&top_n=10&algorithm=content_based

```

  
#### 📤 响应格式

```json

{

  "success": true,

  "data": {

    "recommendations": [

      {

        "attraction_id": 1,

        "name": "故宫博物院",

        "type": "历史景点",

        "score": 0.95,

        "reason": "基于您的历史浏览记录推荐",

        "image_url": "/images/forbidden-city.jpg",

        "popularity": 0.8,

        "rating": 4.7

      }

    ],

    "algorithm_used": "content_based",

    "processing_time": "0.045s"

  }

}

```

  

### 2️⃣ GET /api/recommendations/hot

  

#### 📘 功能描述

基于景点热度和评分，使用快速选择算法返回当前热门景点推荐（无需用户登录）。

  

#### 🧾 请求参数

|    参数名    | 类型     | 是否必填 | 默认值          | 说明                                   |
| :-------: | ------ | ---- | ------------ | ------------------------------------ |
|  `top_n`  | int    | ❌    | 10           | 返回推荐数量（使用快速选择算法优化）                   |
| `sort_by` | string | ❌    | "popularity" | 排序依据：`popularity`(热度) / `rating`(评分) |

#### 📥 请求示例

```http

GET /api/recommendations/hot?top_n=15&sort_by=rating

```

  

#### 📤 响应格式

```json

{

  "success": true,

  "data": {

    "recommendations": [

      {

        "attraction_id": 2,

        "name": "颐和园",

        "type": "自然风光",

        "popularity": 0.9,

        "rating": 4.8,

        "visitor_count": 15000

      }

    ],

    "sort_method": "rating",

    "total_attractions": 200

  }

}

```

  

### 3️⃣ GET /api/recommendations/search

  

#### 📘 功能描述

基于倒排索引算法，支持对景点名称、类别、关键字的快速搜索，并对搜索结果按相关度排序。

  

#### 🧾 请求参数

| 参数名 | 类型 | 是否必填 | 默认值 | 说明 |
|--------|------|----------|--------|------|
| `query` | string | ✅ | — | 搜索关键词 |
| `search_type` | string | ❌ | "all" | 搜索类型：`name`(名称) / `category`(类别) / `all`(全部) |
| `limit` | int | ❌ | 20 | 最大返回结果数 |

#### 📥 请求示例

```http

GET /api/recommendations/search?query=自然风光&search_type=category&limit=15

```

  

#### 📤 响应格式

```json

{

  "success": true,

  "data": {

    "query": "自然风光",

    "results": [

      {

        "attraction_id": 3,

        "name": "香山公园",

        "type": "自然风光",

        "relevance_score": 0.98,

        "match_field": "category",

        "highlight": "自然风光"

      }

    ],

    "total_count": 45,

    "search_time": "0.023s"

  }

}

```

  

## 四、错误码说明

  
| 错误码 | 说明       | 解决方案          |
| --- | -------- | ------------- |
| 400 | 参数错误     | 检查请求参数格式和必填项  |
| 404 | 用户不存在    | 检查user_id是否正确 |
| 500 | 推荐算法内部错误 | 服务器端算法执行异常    |

## 五、算法说明
  

- **堆排序算法**：用于Top-N推荐，时间复杂度O(N log K)，避免完全排序

- **倒排索引**：用于关键词搜索，提供快速检索能力  

- **快速选择算法**：用于热门推荐，部分排序优化性能

  

---

  

**文档维护说明：** 本文档随推荐算法迭代而更新，重大接口变更需同步通知前端开发人员。