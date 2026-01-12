# 旅行社区模块设计文档

## 📋 概述

旅行社区是一个全新的功能模块，与**行程规划**和**个人中心**位于同一级别，整合了原有的旅行日记功能。用户可以在社区中浏览所有旅行者分享的日记，也可以管理自己的日记。

## 🏗️ 架构设计

### 模块层级
```
简途应用
├── 行程规划 (/)
├── 旅行社区 (/community)  ← 新增顶级模块
│   └── 我的日记 (/diary)   ← 整合到社区
└── 个人中心 (/profile)
```

### 功能划分

#### 1. 旅行社区 (`/community`)
**定位**: 公开的社区广场，所有用户可见

**核心功能**:
- ✅ 浏览所有用户的公开日记
- ✅ 按时间/热度/距离筛选
- ✅ 地图上查看所有日记位置
- ✅ 点击查看日记详情
- 🔜 点赞、评论、收藏（待实现）
- 🔜 关注其他旅行者（待实现）

**页面组件**: `frontend/src/views/Community.vue`

**特点**:
- 瀑布流式卡片布局
- 实时统计（总日记数、用户数）
- 集成地图显示所有日记位置
- 响应式设计，移动端友好

#### 2. 我的日记 (`/diary`)
**定位**: 个人日记管理中心，需要登录

**核心功能**:
- ✅ 创建/编辑/删除个人日记
- ✅ 地图选点记录位置
- ✅ 关联景点信息
- ✅ 日记内容压缩存储
- ✅ 个人统计（累计日记、定位记录等）

**页面组件**: `frontend/src/views/TravelDiary.vue`

**特点**:
- 只显示当前登录用户的日记
- 完整的CRUD操作
- 地图交互式选点
- 数据压缩优化存储

## 🔌 API接口设计

### 后端路由

#### 社区相关 API
```python
# 文件: backend/app/routes/travel_diary.py

# 1. 获取所有公开日记（社区浏览）
GET /api/diaries/public
参数:
  - page: int (页码，默认1)
  - limit: int (每页数量，默认20)
返回:
  {
    "success": true,
    "data": [...],
    "count": 5,
    "total": 100,
    "page": 1,
    "limit": 20
  }
```

#### 个人日记 API
```python
# 2. 获取指定用户的日记
GET /api/diaries?user_id=1

# 3. 创建日记
POST /api/diaries/create
需要登录，自动使用 session['user_id']

# 4. 更新日记
PUT /api/diaries/<diary_id>
需要登录，只能修改自己的日记

# 5. 删除日记
DELETE /api/diaries/<diary_id>
需要登录，只能删除自己的日记
```

### 数据库查询优化

**公开日记查询**包含用户信息（用户名、头像）:
```sql
SELECT 
    d.diary_id, d.user_id, d.title, d.content, 
    d.latitude, d.longitude, d.create_time,
    a.name AS attraction_name,
    u.username, u.avatar AS user_avatar
FROM diaries d 
LEFT JOIN attractions a ON d.attraction_id = a.attraction_id 
LEFT JOIN users u ON d.user_id = u.user_id
ORDER BY d.create_time DESC
LIMIT %s OFFSET %s
```

## 🎨 前端设计

### 页面布局

#### Community.vue (社区页面)
```
┌─────────────────────────────────────────┐
│  🎨 顶部Banner (渐变色+统计数据)          │
├─────────────────────┬───────────────────┤
│  📝 日记卡片列表     │  🗺️ 地图+侧边栏   │
│  - 用户信息         │  - 所有日记位置    │
│  - 标题内容         │  - 快速导航        │
│  - 互动按钮         │                   │
│  - 分页控制         │                   │
└─────────────────────┴───────────────────┘
```

#### TravelDiary.vue (我的日记)
```
┌─────────────────────────────────────────┐
│  🍞 面包屑: 旅行社区 > 我的日记          │
├─────────────────────┬───────────────────┤
│  📊 统计卡片         │  ➕ 创建/编辑表单  │
│  🗺️ 地图（可选点）  │  - 标题输入        │
│  📜 日记时间线       │  - 内容编辑        │
│  - 点击定位         │  - 地点选择        │
│  - 展开阅读         │                   │
└─────────────────────┴───────────────────┘
```

### 导航栏更新

**修改前**:
```
行程规划 | 旅行日记 | 个人中心
```

**修改后**:
```
行程规划 | 旅行社区 | 个人中心
           └─ 我的日记（子页面）
```

### 路由配置
```javascript
// frontend/src/router/index.js
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/community', name: 'Community', component: Community },  // 新增
  { path: '/diary', name: 'TravelDiary', component: TravelDiary },  // 保留
  { path: '/profile', name: 'UserProfile', component: UserProfile }
]
```

## 🔐 权限控制

### 公开访问
- ✅ 社区页面 (`/community`) - 所有人可访问
- ✅ 查看公开日记列表 - 无需登录

### 需要登录
- ❌ 我的日记页面 (`/diary`) - 需要登录
- ❌ 创建/编辑/删除日记 - 需要登录
- ❌ 点赞/评论/收藏（未来功能）- 需要登录

### 后端装饰器
```python
@login_required
def create_diary():
    user_id = session['user_id']  # 自动从session获取
    # ...
```

## 📊 数据流设计

### 社区浏览流程
```
用户访问 /community
    ↓
前端调用 GET /api/diaries/public
    ↓
后端查询所有公开日记 + 用户信息
    ↓
返回分页数据
    ↓
前端渲染卡片 + 地图标记
    ↓
用户点击卡片 → 弹窗显示详情
```

### 日记创建流程
```
用户登录后访问 /diary
    ↓
前端调用 GET /api/diaries?user_id={current_user}
    ↓
显示当前用户的所有日记
    ↓
用户点击地图选点 → 获取坐标
    ↓
填写表单提交 POST /api/diaries/create
    ↓
后端压缩内容存储到数据库
    ↓
返回新创建的日记
    ↓
前端刷新列表 + 地图标记
```

## 🎯 用户体验优化

### 1. 面包屑导航
在"我的日记"页面顶部添加面包屑:
```
旅行社区 > 我的日记
```
点击"旅行社区"可返回社区首页

### 2. 快速入口
- 社区页面右上角"写日记"按钮 → 跳转到 `/diary`
- 社区侧边栏"我的日记"链接 → 跳转到 `/diary`
- 我的日记页面面包屑 → 返回 `/community`

### 3. 视觉反馈
- 加载动画（骨架屏）
- Hover效果（卡片阴影、边框高亮）
- 空状态提示

### 4. 响应式设计
- 桌面端: 左右布局（日记列表 + 地图）
- 移动端: 上下堆叠布局

## 🚀 未来扩展

### Phase 2: 社交互动
- [ ] 点赞系统（diary_likes表）
- [ ] 评论系统（diary_comments表）
- [ ] 收藏功能（diary_favorites表）

### Phase 3: 推荐算法
- [ ] 基于位置的附近日记推荐
- [ ] 基于兴趣的个性化推荐
- [ ] 热门日记排行榜

### Phase 4: 社区功能
- [ ] 用户关注系统
- [ ] 私信功能
- [ ] 话题标签 (#旅行攻略)
- [ ] 活动组织

## 📁 文件清单

### 后端文件
```
backend/
├── app/
│   ├── routes/
│   │   ├── travel_diary.py      # ✅ 新增 /public 接口
│   │   └── community.py          # (已存在，可选)
│   └── __init__.py              # ✅ 已注册 blueprint
└── test_community_api.py        # ✅ API测试脚本
```

### 前端文件
```
frontend/
├── src/
│   ├── views/
│   │   ├── Community.vue        # ✅ 新增社区页面
│   │   └── TravelDiary.vue      # ✅ 更新面包屑导航
│   ├── router/
│   │   └── index.js             # ✅ 新增 /community 路由
│   └── App.vue                  # ✅ 更新导航栏
└── ...
```

## 🧪 测试验证

### 后端测试
运行测试脚本验证API:
```bash
python backend/test_community_api.py
```

**预期结果**:
- ✅ 获取公开日记列表成功
- ✅ 返回正确的分页数据
- ✅ 包含用户名和头像信息

### 前端测试
1. 访问 `http://localhost:8080/#/community`
2. 验证社区页面正常显示
3. 点击日记卡片查看详情
4. 点击"写日记"跳转到个人日记页面
5. 在地图上验证所有标记点显示

## 📝 更新日志

### 2026-01-12
- ✅ 创建旅行社区模块
- ✅ 后端新增 `/api/diaries/public` 接口
- ✅ 前端实现 `Community.vue` 页面
- ✅ 更新导航栏"旅行社区"替代"旅行日记"
- ✅ 我的日记页面添加面包屑导航
- ✅ 路由配置完成
- ✅ API测试通过

---

## 💡 技术亮点

1. **模块化设计**: 清晰的功能划分，社区浏览和个人管理分离
2. **数据复用**: 同一套API支持不同场景（社区/个人）
3. **性能优化**: 分页加载、内容压缩、SQL优化
4. **用户体验**: 面包屑导航、快速入口、响应式设计
5. **可扩展性**: 预留社交功能接口，便于未来扩展

## 🎓 使用指南

### 用户操作流程

**1. 浏览社区**
- 访问"旅行社区"查看所有人的日记
- 点击卡片查看详情
- 地图上浏览不同位置的旅行记录

**2. 写日记**
- 点击"写日记"按钮进入个人日记页面
- 在地图上选择位置
- 填写标题和内容
- 提交保存

**3. 管理日记**
- 在"我的日记"页面查看自己的所有日记
- 编辑或删除现有日记
- 查看个人统计数据

---

**文档维护**: LYY  
**最后更新**: 2026-01-12  
**版本**: v1.0
