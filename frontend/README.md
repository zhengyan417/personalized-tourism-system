# Frontend (Vue 3 + Vue Router + Bootstrap + Leaflet)

基于 Vue 3 的前端子项目，集成 Vue Router、Bootstrap 5、Leaflet（高德瓦片源）。

## 环境要求

- Node.js >= 16（推荐 18+）
- npm >= 8（或使用 pnpm/yarn 自行调整命令）

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

也可从仓库根目录操作（已配置便捷脚本）：

```pwsh
npm run frontend:install
npm run frontend:serve
npm run frontend:build
```

## 目录结构

- `public/index.html` 应用挂载点
- `src/main.js` 入口；引入 Bootstrap/Leaflet、注册路由
- `src/router/index.js` 路由配置（首页、地点查询、推荐、路径规划、旅行日记）
- `src/components/map/BaseMap.vue` Leaflet 基础地图组件（高德源）
- `src/components/{recommendation,route,place,diary}` 模块占位
- `src/views/*` 路由视图

## 备注

- 默认后端地址：`http://localhost:5000`（可通过环境变量 `VUE_APP_API_BASE_URL` 覆盖）
- 地图底图使用高德矢量瓦片 `style=7`，仅用于开发演示，具体使用条款请遵循高德地图要求。
- 若需要切换为 Hash/History 路由，请在 `src/router/index.js` 调整创建方式，并配合后端做回退。

## API 使用

- Axios 封装：`src/api/index.js`
- 场所查询：`src/api/place.js`
	- `fetchNearbyPlaces({ lat, lon, radius, category, limit })`
	- `fetchCategories()`（后端未实现时返回静态占位）
- 推荐接口：`src/api/recommendation.js`
	- `fetchRecommendations(params)`
	- `fetchHotRecommendations(params)`
	- `searchRecommendations(params)`

后端本地开发默认端口 5000，若不同请在前端以 `.env.development` 配置：

```
VUE_APP_API_BASE_URL=http://localhost:5000
```

## 地图组件 BaseMap 用法

示例：

```vue
<BaseMap
	:center="[39.9042, 116.4074]"
	:zoom="11"
	:height="600"           
	:fullScreen="false"     
	:offsetTop="0"          
	:markers="markers"      
	:selectedId="selectedId" 
	@marker-click="onMarkerClick" />
```

Props：
- `center: [lat, lon]` 初始中心点
- `zoom: number` 初始缩放级别
- `height: number|string` 非全屏时容器高度（默认 400）
- `fullScreen: boolean` 是否全屏（默认 false）
- `offsetTop: number|string` 全屏时距顶部偏移，避免覆盖导航栏
- `markers: Array<{ id, name, latitude, longitude, popup }>` 标记点集合
- `selectedId: string|number|null` 选中的标记 ID，用于打开对应 popup 并居中

事件：
- `marker-click`: (markerData) => void

## 页面说明

- 首页：`src/views/Home.vue`（可切换全屏地图展示）
- 地点查询：`src/views/PlaceQuery.vue`（列表 + 地图联动、类别/半径筛选）
- 推荐：`src/views/Recommendation.vue`（待接入后端数据，可先展示热门/个性化列表）

## 常见问题（FAQ）

- 地图不显示或只见空白：
	- 确保容器有高度（非全屏时使用 `height`，全屏时结合 `offsetTop`）。
	- 检查浏览器控制台是否有瓦片加载错误（网络/跨域）。
	- 调整中心点与缩放级别，或传入 `markers` 后让地图自动 fitBounds（非全屏）。
- API 报错：
	- 确认后端端口与 `VUE_APP_API_BASE_URL` 一致。
	- 检查后端是否已注册路由（例如 `/api/places/nearby`）。

## 更新记录

- 2025-10-14 集成 Vue Router、Bootstrap、Leaflet；新增基础地图组件 BaseMap；预设首页/地点查询/推荐/路径规划/旅行日记路由；首页接入地图
- 2025-10-14 地图瓦片切换为高德源，支持全屏与顶部偏移，导航置顶
- 2025-10-20 新增 axios 封装与 place/recommendation API；BaseMap 支持 markers/selectedId；完成 PlaceQuery 列表+地图联动
