# 🗄️ 个性化旅游系统数据库 ER 图设计
版本：v1.0  
作者：C 同学（后端与数据模块）  
日期：第6周  

---

## 一、设计目标

本数据库用于支撑“个性化旅游系统”的后端逻辑，核心目标包括：

1. 存储用户基本信息及其操作行为（路线规划、游记记录等）；  
2. 提供高效的场所查询支持（通过经纬度与类别过滤实现）；  
3. 便于算法模块（推荐、路径、搜索）进行数据访问与分析；  
4. 保证表结构清晰、冗余最小、便于维护与扩展。  

---

## 二、核心实体说明

| 实体名称 | 说明 | 关键字段 |
|-----------|------|----------|
| **users** | 系统注册用户信息表 | user_id, username, email, password |
| **attractions** | 景点信息表，支持范围查询与分类筛选 | attraction_id, name, latitude, longitude, category |
| **routes** | 用户自定义或推荐的路线信息表 | route_id, user_id, route_data |
| **diaries** | 用户旅游日记表，支持霍夫曼压缩存储 | diary_id, user_id, attraction_id, content |

---

## 三、字段设计与外键关系

### 1️⃣ users 表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | INT | PK, AUTO_INCREMENT | 用户唯一标识 |
| username | VARCHAR(50) | NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE | 邮箱地址 |
| password | VARCHAR(255) | NOT NULL | 加密密码 |

---

### 2️⃣ attractions 表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| attraction_id | INT | PK, AUTO_INCREMENT | 景点唯一标识 |
| name | VARCHAR(100) | NOT NULL | 景点名称 |
| category | VARCHAR(50) | | 景点类别（如“美食”、“自然”、“历史”） |
| latitude | DOUBLE | | 纬度 |
| longitude | DOUBLE | | 经度 |
| description | TEXT | | 简要描述 |

---

### 3️⃣ routes 表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| route_id | INT | PK, AUTO_INCREMENT | 路线唯一标识 |
| user_id | INT | FK → users.user_id | 关联用户 |
| route_data | JSON | | 存储路线点坐标、时间等信息 |

---

### 4️⃣ diaries 表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| diary_id | INT | PK, AUTO_INCREMENT | 日记唯一标识 |
| user_id | INT | FK → users.user_id | 所属用户 |
| attraction_id | INT | FK → attractions.attraction_id | 关联景点 |
| title | VARCHAR(100) | | 日记标题 |
| content | MEDIUMBLOB | | 压缩后内容（二进制存储） |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

## 四、关系描述

| 关系类型 | 说明 |
|-----------|------|
| 用户 - 路线 | 一对多（一个用户可拥有多条路线） |
| 用户 - 日记 | 一对多（一个用户可撰写多篇日记） |
| 景点 - 日记 | 一对多（一个景点可关联多篇日记） |
| 用户 - 景点 | 间接关系（通过日记或路线建立联系） |

---

## 五、ER 图示（Mermaid）

```mermaid
erDiagram
    USERS {
        int user_id PK
        varchar username
        varchar email
        varchar password
    }

    ATTRACTIONS {
        int attraction_id PK
        varchar name
        varchar category
        double latitude
        double longitude
        text description
    }

    ROUTES {
        int route_id PK
        int user_id FK
        json route_data
    }

    DIARIES {
        int diary_id PK
        int user_id FK
        int attraction_id FK
        varchar title
        mediumblob content
        datetime create_time
    }

    USERS ||--o{ ROUTES : "owns"
    USERS ||--o{ DIARIES : "writes"
    ATTRACTIONS ||--o{ DIARIES : "appears_in"
