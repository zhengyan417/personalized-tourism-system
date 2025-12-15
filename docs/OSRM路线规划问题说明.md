# OSRM路线规划服务问题说明

## 问题描述

系统中的路线规划功能默认使用 OSRM (Open Source Routing Machine) 公共服务器 `router.project-osrm.org`。

当前遇到的问题：**OSRM公共服务器在中国大陆地区访问超时**，导致路线规划降级为直线距离。

## 原因分析

1. OSRM公共演示服务器部署在国外，从中国访问存在网络延迟或被防火墙阻断
2. 公共服务器不保证高可用性和稳定性
3. 可能存在访问频率限制

## 解决方案

### 方案1：使用高德地图API（推荐）

系统已经集成了高德地图导航API作为备选方案。

**配置步骤：**

1. 注册高德开放平台账号：https://lbs.amap.com/
2. 创建应用并获取API Key
3. 在后端配置文件中设置环境变量：

```bash
# Windows (cmd)
set AMAP_API_KEY=你的高德API_Key

# Windows (PowerShell)
$env:AMAP_API_KEY="你的高德API_Key"

# Linux/Mac
export AMAP_API_KEY=你的高德API_Key
```

4. 修改路线规划API，使用 `fetch_amap_route` 替代 `fetch_osrm_route`

**文件修改：**
`backend/app/routes/route_planning.py` 中的路线规划接口，将：
```python
from app.services.navigate_service import fetch_osrm_route
result = fetch_osrm_route(start, end, waypoints, profile)
```

改为：
```python
from app.services.navigate_service import fetch_amap_route
result = fetch_amap_route(start, end, waypoints, profile)
```

### 方案2：部署本地OSRM服务器

如果需要使用开源方案，可以自行部署OSRM服务器。

**Docker部署（推荐）：**

```bash
# 1. 下载地图数据（以北京为例）
wget http://download.geofabrik.de/asia/china-latest.osm.pbf

# 2. 预处理数据
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/china-latest.osm.pbf
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/china-latest.osrm
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/china-latest.osrm

# 3. 启动OSRM服务
docker run -t -i -p 5000:5000 -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/china-latest.osrm
```

**配置后端使用本地服务：**

```bash
# 设置环境变量
set OSRM_BASE_URL=http://localhost:5000

# 或在 backend/config.py 中修改
OSRM_BASE_URL = os.getenv('OSRM_BASE_URL', 'http://localhost:5000')
```

### 方案3：增加超时时间和重试逻辑

如果网络偶尔可以访问OSRM，可以增加超时时间（已修改为15秒）和添加重试机制。

**当前状态：**
- ✅ 已将OSRM超时时间从8秒增加到15秒
- ✅ 失败时自动降级为直线距离
- ⚠️ 但当前网络环境下仍然超时

## 当前配置

```python
# backend/app/services/navigate_service.py
OSRM_BASE_DEFAULT = "https://router.project-osrm.org"
OSRM_DEFAULT_TIMEOUT = 15  # 秒
```

## 推荐做法

**短期方案：** 保持当前降级机制，用户可以看到直线距离估算

**长期方案：** 
1. 注册高德地图API并切换到高德导航服务（国内访问速度快，稳定性高）
2. 或者在服务器上部署本地OSRM实例

## 测试脚本

已创建测试脚本 `test_osrm.py`，可以用来验证OSRM服务可用性：

```bash
python test_osrm.py
```

## 相关文件

- `backend/app/services/navigate_service.py` - 导航服务实现
- `backend/app/routes/route_planning.py` - 路线规划API接口
- `backend/config.py` - 配置文件
- `test_osrm.py` - OSRM服务测试脚本

---

**更新日期：** 2025-12-15
**状态：** OSRM公共服务在当前网络环境下不可用，已增加超时时间，系统会自动降级为直线距离
