# 用户登录与数据持久化流程说明

## 概述

后端已经实现了完整的用户登录、个人资料和旅行日记的持久化功能。所有数据都会自动关联到登录用户。

## 认证流程

### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123",
  "email": "test@example.com"
}
```

**响应**:
```json
{
  "status": "success",
  "message": "注册成功"
}
```

### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

**响应**（包含完整用户资料）:
```json
{
  "status": "success",
  "message": "登录成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "age": null,
    "occupation": null,
    "bio": null,
    "avatar": null,
    "travel_persona": null,
    "favorite_cities": null,
    "created_at": "2025-12-22 10:00:00",
    "updated_at": null
  }
}
```

**注意**: 登录成功后，服务器会设置 session cookie，后续所有请求都会自动携带此 cookie。

### 3. 获取当前登录用户信息
```http
GET /api/auth/me
```

**响应**（包含日记统计）:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "age": 25,
    "occupation": "工程师",
    "bio": "热爱旅行",
    "avatar": "https://example.com/avatar.jpg",
    "travel_persona": "冒险家",
    "favorite_cities": "北京, 上海, 杭州",
    "diary_count": 5,
    "created_at": "2025-12-22 10:00:00",
    "updated_at": "2025-12-22 15:30:00"
  }
}
```

### 4. 更新个人资料
```http
PUT /api/auth/profile
Content-Type: application/json

{
  "age": 25,
  "occupation": "工程师",
  "bio": "热爱旅行的程序员",
  "avatar": "https://example.com/avatar.jpg",
  "travel_persona": "冒险家",
  "favorite_cities": "北京, 上海, 杭州"
}
```

**响应**:
```json
{
  "status": "success",
  "message": "资料更新成功"
}
```

### 5. 退出登录
```http
POST /api/auth/logout
```

**响应**:
```json
{
  "status": "success",
  "message": "已退出登录"
}
```

## 旅行日记功能

### 1. 创建日记（需要登录）
```http
POST /api/diaries/create
Content-Type: application/json

{
  "title": "西湖游记",
  "content": "今天去了杭州西湖，风景很美...",
  "latitude": 30.2547,
  "longitude": 120.1490,
  "attraction_id": 123
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "diary_id": 1,
    "user_id": 1,
    "username": "testuser",
    "title": "西湖游记",
    "content": "今天去了杭州西湖，风景很美...",
    "snippet": "今天去了杭州西湖，风景很美...",
    "latitude": 30.2547,
    "longitude": 120.1490,
    "date": "2025-12-22 16:00"
  }
}
```

**注意**: 
- 创建日记时不需要提供 `user_id`，系统会自动使用当前登录用户的 ID
- 必须先登录，否则返回 401 错误

### 2. 获取日记列表

**获取当前登录用户的日记**:
```http
GET /api/diaries/
```

**获取指定用户的日记**:
```http
GET /api/diaries/?user_id=1
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "diary_id": 1,
      "user_id": 1,
      "username": "testuser",
      "title": "西湖游记",
      "content": "...",
      "snippet": "...",
      "date": "2025-12-22 16:00",
      "latitude": 30.2547,
      "longitude": 120.1490
    }
  ],
  "count": 1
}
```

### 3. 获取单个日记详情
```http
GET /api/diaries/1
```

### 4. 更新日记（需要登录，且只能更新自己的日记）
```http
PUT /api/diaries/1
Content-Type: application/json

{
  "title": "西湖游记（更新）",
  "content": "今天去了杭州西湖，风景很美，天气也不错..."
}
```

**权限控制**:
- 只能更新自己创建的日记
- 尝试更新他人日记会返回 403 错误

### 5. 删除日记（需要登录，且只能删除自己的日记）
```http
DELETE /api/diaries/1
```

**权限控制**:
- 只能删除自己创建的日记
- 尝试删除他人日记会返回 403 错误

## 前端集成建议

### 1. 登录后保存用户信息
```javascript
// 登录成功后
const response = await axios.post('/api/auth/login', {
  username: 'testuser',
  password: 'password123'
}, {
  withCredentials: true  // 重要：携带 cookie
});

// 保存用户信息到 Vuex 或 localStorage
localStorage.setItem('user', JSON.stringify(response.data.data));
```

### 2. 所有请求自动携带认证信息
```javascript
// 在 axios 配置中启用 withCredentials
const api = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true  // 自动携带 session cookie
});
```

### 3. 创建日记时不需要传 user_id
```javascript
// ❌ 错误：不需要传 user_id
await api.post('/api/diaries/create', {
  user_id: 1,  // 不需要
  title: '西湖游记',
  content: '...'
});

// ✅ 正确：系统自动使用当前登录用户
await api.post('/api/diaries/create', {
  title: '西湖游记',
  content: '...'
});
```

### 4. 处理未登录状态
```javascript
// 拦截 401 错误，跳转到登录页
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 清除本地用户信息
      localStorage.removeItem('user');
      // 跳转到登录页
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

## 数据持久化保证

### Session 配置
- Session 有效期：7 天
- Session 存储：文件系统（可升级为 Redis）
- Cookie 配置：HttpOnly + SameSite=Lax

### 数据库关联
- 所有日记都通过 `user_id` 关联到用户表
- 用户资料和日记都会自动持久化到 MySQL
- 登录状态通过 session 维持，重启浏览器后仍然有效（7天内）

### 安全性
- 密码使用 werkzeug.security 加密存储
- Session cookie 设置 HttpOnly 防止 XSS
- CORS 配置支持局域网和 localhost 访问
- 日记的创建、更新、删除都需要登录
- 用户只能操作自己的日记（权限控制）

## 测试流程

1. **注册新用户**
2. **登录** - 获取 session cookie
3. **更新个人资料** - 数据保存到数据库
4. **创建日记** - 自动关联当前用户
5. **查看日记列表** - 只显示当前用户的日记
6. **更新/删除日记** - 只能操作自己的日记
7. **关闭浏览器重新打开** - session 仍然有效（7天内）
8. **调用 /api/auth/me** - 获取完整用户信息和日记统计

## 常见问题

### Q: 为什么前端请求返回 401？
A: 确保前端 axios 配置了 `withCredentials: true`，这样才能自动携带 session cookie。

### Q: 为什么创建日记时提示 "请先登录"？
A: 检查是否已经登录，以及前端是否正确配置了 `withCredentials`。

### Q: 为什么重启浏览器后还需要重新登录？
A: 检查浏览器是否禁用了 cookie，或者 session 是否已过期（默认 7 天）。

### Q: 如何清除所有 session？
A: 删除后端的 `flask_session` 目录（如果使用文件系统存储）。

### Q: 生产环境如何配置？
A: 
1. 设置环境变量 `SECRET_KEY` 为强密码
2. 将 `SESSION_COOKIE_SECURE` 改为 `True`（要求 HTTPS）
3. 考虑使用 Redis 存储 session（更高性能）
4. 配置正确的 CORS 域名白名单
