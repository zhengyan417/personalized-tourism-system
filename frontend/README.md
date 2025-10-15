# Frontend (Vue 3 + Vue Router + Bootstrap + Leaflet)

## 开发

1. 安装依赖

```pwsh
cd .\frontend
npm install
```

2. 启动开发服务器

```pwsh
npm run serve
```

3. 生产构建

```pwsh
npm run build
```

## 目录结构

- `public/index.html` 应用挂载点
- `src/main.js` 入口；引入 Bootstrap/Leaflet、注册路由
- `src/router/index.js` 路由配置（首页、地点查询、推荐、路径规划、旅行日记）
- `src/components/map/BaseMap.vue` Leaflet 基础地图组件（高德源）
- `src/components/{recommendation,route,place,diary}` 模块占位
- `src/views/*` 路由视图

## 备注



## 更新记录

- 2025-10-14 集成 Vue Router、Bootstrap、Leaflet；新增基础地图组件 BaseMap；预设首页/地点查询/推荐/路径规划/旅行日记路由；首页接入地图
