**周期：** 2025/10/14 ~ 2025/10/19 12.00am
# 主要目标
1. 完成前后端分离架构搭建
2. 明确接口规范
3. 启动算法设计
4. 完成智能体开发

# 分工计划

***注意***
## 完成任务后，自行用删除线，如~~任务二~~

### 甘和君
- 开发前端agent。正式发布在初发平台上。
- 完成并且优化项目方案书及对应PPT,准备在下周一课上报告。
- 确定最终功能清单，创建并编写 `/docs/project-management/functional-spec.md`。包含用户故事、功能点列表。
- 编写推荐模块API接口文档。创建并编写 `/docs/api/recommendation.md`。推荐系统的完整API接口说明
- ~~完成项目完整结构的构建~~
- 制作第六周周报与第七周安排。创建并编写 `/docs/project-management/weekly-plans/week-07.md`。

### 蔡佩霖
- 开发后端agent。正式发布在初发平台上。
- 设计路径规划模块API接口。创建并编写 `/docs/api/route-planning.md`。路径规划请求、响应参数详解。
- 实现C++图基础类。创建并实现 `/cpp_core/include/graph/` 下的头文件。`graph.h`, `vertex.h`, `edge.h` (类的声明)。
- 实现图类基础方法。创建并实现 `/cpp_core/src/graph/` 下的源文件。`graph.cpp`, `vertex.cpp`, `edge.cpp` (类的基础实现，如添加顶点、边)。
- 创建C++模块构建配置。创建 `/cpp_core/CMakeLists.txt`。确保C++项目能成功编译。
### 刘永琰
- 设计数据库ER图。创建并编写 `/docs/database/er_diagram.md`。可描述核心表关系，附示意图或Mermaid代码。
- 创建MySQL表结构脚本。 创建并编写 `/docs/database/schema.sql`。创建 `users`, `attractions`, `routes`, `diaries` 等核心表的SQL。
- 编写场所查询API文档。 创建并编写 `/docs/api/place-query.md`。邻近查询、类别过滤等接口说明。
- 编写旅游日记API文档。 创建并编写 `/docs/api/travel-diary.md`。日记CRUD、压缩等接口说明。
- 搭建Flask后端骨架。在 `/backend/` 目录下创建 `app/` 子目录结构，完整的 `/backend/app/` 包结构，含 `__init__.py`。


### 唐士淼
- 搭建Vue.js项目骨架。在 `/frontend/` 目录下，使用 Vue CLI 创建标准项目。完整的 `/frontend/` 目录结构，包含 `src/`, `public/` 等。
- 集成Vue Router。配置 `/frontend/src/router/index.js`。路由配置文件，预设推荐、路径规划等路由。
- 集成Leaflet地图库。在 `/frontend/src/components/map/` 创建基础地图组件。`BaseMap.vue` (一个初始化并显示地图的基础组件)。
- 集成Bootstrap。在 `/frontend/` 下安装并配置Bootstrap依赖。`package.json` 中引入Bootstrap，并在 `main.js` 中导入。
- 设计前端组件结构。在 `/frontend/src/components/` 下创建各模块的空白组件目录。`recommendation/`, `route/`, `place/`, `diary/` 等组件文件夹。

# git协作流程

1. 所有人从 `main` 分支创建个人功能分支，例如：

- 甘和君: `git checkout -b feature/gan-week6-docs`
    
- 蔡佩霖: `git checkout -b feature/cai-week6-cpp-api`
    
- 刘永琰: `git checkout -b feature/liu-week6-db-api`
    
- 唐士淼: `git checkout -b feature/tang-week6-frontend`

2. 在各自分支上按上述计划开发，并**及时推送 (`git push`)** 到远程仓库。
3. 
- **代码审查**：所有人完成开发后，在GitHub上向 `dev` 分支发起 **Pull Request**。
- **相互审查**：至少指定一位其他成员审查你的PR。
- **合并**：审查通过后，合并到 `dev` 分支，并**删除原功能分支**。
- **同步**：最后，所有人在本地切换回 `dev` 分支，执行 `git pull origin dev` 拉取所有人的成果。

# 验收标准

- **访问 `http://localhost:8080`** 可看到前端欢迎页面。
- **`/docs` 目录** 下包含完整的功能清单、API文档和数据库设计。
- **`/cpp_core` 目录** 下的代码可以通过 `cmake` 和 `make` 成功编译。
- **`/backend` 目录** 拥有一个结构清晰的Flask应用包。


