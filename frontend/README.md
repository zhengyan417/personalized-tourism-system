# Frontend (Vue 3 + Vue Router + Bootstrap + Leaflet)

基于 Vue 3 的前端子项目，集成 Vue Router、Bootstrap 5、Leaflet（OpenStreetMap 瓦片）。

## 环境要求

- Node.js >= 16（推荐 18+）
- npm >= 8（或使用 pnpm/yarn 自行调整命令）

## 开发

1. 安装依赖

```pwsh
npm install
```

### 测试开关（切换测试/正式后端）

- 在`.env.development`中设置：`VUE_APP_FRONTEND_TEST=true`
  

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
cd /d C:\code\travel
npm run frontend:install
npm run frontend:serve
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
- 地图底图改为 OpenStreetMap（与 OSRM 路由配套）；请遵循 OSM 使用政策（合理并发与缓存）。
- 若需要切换为 Hash/History 路由，请在 `src/router/index.js` 调整创建方式，并配合后端做回退。
- 导航提供商统一为 OSRM（后端 `/api/routes/navigate` 已固定使用 OSRM）。

## API 使用

- Axios 封装：`src/api/index.js`
- 场所查询：`src/api/place.js`
	- `fetchNearbyPlaces({ lat, lon, radius, category, limit })`
	- `fetchCategories()`（后端未实现时返回静态占位）
- 推荐接口：`src/api/recommendation.js`
	- `fetchRecommendations(params)`
	- `fetchHotRecommendations(params)`
	- `searchRecommendations(params)`
- 路径规划：`src/api/route.js`
	- `fetchRoadRoute(params)` 可不传 `provider`（后端已固定为 OSRM）。

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
- 推荐：`src/views/Recommendation.vue`（关键词搜索、偏好设置、虚拟滚动、Top10 高亮、地图标记联动）
- 路径规划：`src/views/RoutePlanning.vue`，新增导航服务下拉框、fallback 提示与路程摘要展示；地图会根据返回的 polyline 绘制路径。

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
- 2025-11-02 推荐模块页面：搜索框、偏好面板（算法/排序/TopN/类别）、虚拟滚动卡片列表、Top10 高亮、地图标记联动；Mock 接口补充坐标
- 2025-11-02 新增“前端测试开关”：支持 TEST/PROD 两套后端切换，优先级 URL 参数 > localStorage > 环境变量；提供 .env.* 示例
- 2025-11-11 地图与首页整合升级：
	- 修复 Leaflet 缩放时“Cannot read properties of null (_latLngToNewLayerPoint)”报错：在缩放动画期间延迟重绘路径图层；增加 whenReady/canAnimate 守卫，并在卸载时彻底移除事件监听，保留平滑缩放体验。
	- BaseMap 新增：定位控件（locateUser）、位置精度圈、location-update 事件；路径规划能力（props: routeMode/routeMarkers；事件: route-point-add），起终点/中间点样式、序号标注与分段距离标签。
	- 前端内置 Mock 扩展：/api/places/*、/api/recommendations/*、/api/diaries（GET/POST/详情）、/api/route/plan，种子数据稳定可重复；通过 VUE_APP_USE_MOCK 控制开关。
	- 首页一体化：在 Home 集成“附近 / 推荐 / 路径 / 日记”四个功能 Tab，地图全屏展示 + 左侧面板操作即可完成全部功能。
	- 面板交互：左侧功能面板支持拖动；右上角提供定位快捷按钮。
	- 附近：新增经纬度输入与“取地图中心”，可直接输入/定位作为查询点；类别/半径筛选保留。
-- 2025-11-18 路径规划升级：新增导航提供商选择器说明、`fetchRoadRoute` provider 参数文档以及高德密钥配置提示。
- 2025-12-01 地图底图切换为 OpenStreetMap；后端导航统一 OSRM，前端文档同步更新。
	- 推荐：将偏好设置压缩为紧凑行（算法/排序/TopN），类别筛选置于“更多”折叠；与地图联动。
	- 日记：新增 TravelDiary 页面与 API（src/api/diary.js）；在首页可直接新建/浏览日记并在地图上查看位置。
	- 主题：加入深浅色主题切换组件（ThemeToggle），地图样式适配暗色模式。
