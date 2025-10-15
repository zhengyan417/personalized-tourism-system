# 路径规划模块 API 文档（C++）
版本: 0.1.0  
命名空间: `route_planning`  
依赖: C++17+ 标准库

本模块定义路径规划的请求/响应数据结构与规划器接口，适用于驾驶、步行、骑行、公共交通等模式，并支持旅游场景的偏好与约束（时间窗、区域偏好、费用/碳排、避让等）。

## 依赖与头文件建议
- 仅使用 C++17 标准库类型
- 可选依赖 `graph` 模块作为底层拓扑

依赖概述
- 构建工具：CMake >= 3.16
- 编译器：MSVC 2022 / MinGW-w64 / Clang / GCC（支持 C++17）
- 运行时：无额外第三方依赖（默认仅用标准库）

建议的头文件组织：
- route_planning/types.hpp
- route_planning/request.hpp
- route_planning/response.hpp
- route_planning/route_planner.hpp

示例包含：
```cpp
#include <vector>
#include <string>
#include <optional>
#include <variant>
#include <chrono>
#include <cstdint>
#include <limits>
#include <memory>
```

## 核心类型

```cpp
namespace route_planning {

struct GeoPoint {
    double lat{std::numeric_limits<double>::quiet_NaN()};  // [-90, 90]
    double lon{std::numeric_limits<double>::quiet_NaN()};  // [-180, 180]
    std::optional<double> ele; // 海拔(米，可选)
};

struct BBox {
    GeoPoint min; // 左下
    GeoPoint max; // 右上
};

enum class TravelMode : uint8_t {
    Driving,
    Walking,
    Cycling,
    Transit
};

enum class OptimizeType : uint8_t {
    Fastest,    // 最短时长
    Shortest,   // 最短距离
    Cheapest,   // 最低费用（路桥费/票价等）
    Scenic,     // 风景优先
    Greener     // 更低碳排
};

enum class Units : uint8_t {
    Metric,     // 米、公里
    Imperial    // 英尺、英里
};

enum class ManeuverType : uint8_t {
    Depart, Arrive, Continue, TurnLeft, TurnRight, SharpLeft, SharpRight,
    SlightLeft, SlightRight, UTurn, Roundabout, Merge, Exit, Elevator, Stairs, Ferry, Transfer
};

enum class ErrorCode : uint16_t {
    Ok = 0,
    InvalidRequest,
    UnsupportedMode,
    NoRouteFound,
    GraphDisconnected,
    TimeWindowViolation,
    ConstraintConflict,
    Timeout,
    InternalError
};

enum class AvoidFlag : uint32_t {
    None     = 0,
    Tolls    = 1 << 0,
    Highways = 1 << 1,
    Ferries  = 1 << 2,
    Unpaved  = 1 << 3,
    Stairs   = 1 << 4,
    Indoor   = 1 << 5,
};
inline AvoidFlag operator|(AvoidFlag a, AvoidFlag b) {
    return static_cast<AvoidFlag>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}
inline bool has_flag(AvoidFlag v, AvoidFlag f) {
    return (static_cast<uint32_t>(v) & static_cast<uint32_t>(f)) != 0;
}

struct TimeWindow {
    // 间隔为 [start, end]，用于景点开放时间、换乘时间窗等
    std::chrono::system_clock::time_point start;
    std::chrono::system_clock::time_point end;
};

struct CostModel {
    // 多目标线性加权，内部将归一化至 [0,1]
    double weight_time   {1.0};
    double weight_dist   {0.0};
    double weight_cost   {0.0};
    double weight_scenic {0.0};
    double weight_co2    {0.0};
};

struct AreaPreference {
    // 避开或偏好区域；可叠加多个 BBox
    std::vector<BBox> avoid_areas;
    std::vector<BBox> prefer_areas;
    double prefer_bias{0.2}; // [0,1] 偏好倾向
};

} // namespace route_planning
```

## 请求模型 RoutePlanningRequest

```cpp
namespace route_planning {

struct RouteHint {
    // 可选：预绑定最近图节点、历史偏好等
    std::optional<uint64_t> origin_node_id;
    std::optional<uint64_t> destination_node_id;
};

struct TransitOptions {
    bool realtime{false};                  // 实时班次
    std::optional<uint32_t> max_transfers; // 最大换乘次数
    std::optional<TimeWindow> time_window; // 出行时间窗
};

struct WalkingOptions {
    std::optional<double> max_distance_m;  // 最大步行距离
    bool wheelchair_accessible{false};     // 无障碍优先
    bool avoid_stairs{false};
};

struct DrivingOptions {
    bool traffic_aware{false};             // 拥堵感知（需外部数据）
    std::optional<double> max_speed_kph;   // 限速
};

struct CyclingOptions {
    bool avoid_unpaved{true};
    bool prefer_bikelanes{true};
};

struct RoutePlanningRequest {
    GeoPoint origin;
    GeoPoint destination;
    std::vector<GeoPoint> waypoints; // 途经点（可空）

    std::optional<std::chrono::system_clock::time_point> departure_time; // 与 arrival_time 互斥
    std::optional<std::chrono::system_clock::time_point> arrival_time;

    TravelMode mode{TravelMode::Walking};
    OptimizeType optimize{OptimizeType::Fastest};
    Units units{Units::Metric};

    AvoidFlag avoid{AvoidFlag::None};
    CostModel cost_model{};
    AreaPreference area_pref{};

    std::optional<uint32_t> alternatives{0}; // 备选路径数量（0 表示仅主路径）
    std::optional<uint32_t> max_solutions;   // 上限保护，避免组合爆炸
    std::optional<std::string> locale;       // 指令本地化，如 "zh-CN"

    // 模式相关细化选项
    std::optional<TransitOptions> transit;
    std::optional<WalkingOptions> walking;
    std::optional<DrivingOptions> driving;
    std::optional<CyclingOptions> cycling;

    std::optional<RouteHint> hint;

    // 校验建议:
    // - 坐标必须在合法范围
    // - departure_time 与 arrival_time 不能同时设置
    // - alternatives 建议不超过 3
};

} // namespace route_planning
```

字段要点：
- origin/destination/waypoints: WGS84，经纬度小数度；NaN 或越界无效。
- optimize 与 cost_model: 若提供 cost_model，可覆盖 optimize 的预设权重。
- avoid: 位集叠加，如 AvoidFlag::Tolls | AvoidFlag::Highways。
- area_pref: 可引导经过风景区或避开拥堵区。
- time: departure_time 与 arrival_time 二选一；未提供可默认当前时间。

## 响应模型 RoutePlanningResponse

```cpp
namespace route_planning {

struct Notice {
    std::string code;      // "PartialClosedRoad" 等
    std::string message;   // 说明
};

struct Step {
    ManeuverType type{ManeuverType::Continue};
    std::string instruction;         // 本地化文本指令
    std::optional<std::string> road_name;
    double distance_m{0};
    double duration_s{0};
    std::optional<double> bearing_before; // 航向角
    std::optional<double> bearing_after;
    std::vector<GeoPoint> polyline;  // 步进几何（可改为编码折线）
};

struct Leg {
    GeoPoint from;
    GeoPoint to;
    std::vector<Step> steps;
    double distance_m{0};
    double duration_s{0};
    std::optional<double> ascent_m;   // 爬升
    std::optional<double> descent_m;  // 下降
};

struct RouteSummary {
    double distance_m{0};
    double duration_s{0};
    std::optional<double> toll_cost;   // 费用估计
    std::optional<double> co2_g;       // 碳排估计
    std::optional<uint32_t> transfers; // 换乘次数（公共交通）
    std::optional<double> scenic_score;// 风景评分[0,1]
};

struct Route {
    std::string id;                // 唯一路径标识
    std::vector<Leg> legs;
    std::vector<GeoPoint> polyline; // 完整路径几何
    RouteSummary summary;
    std::optional<double> confidence; // 置信度[0,1]
    std::vector<Notice> notices;
};

struct Error {
    ErrorCode code{ErrorCode::InternalError};
    std::string message;
    std::optional<std::string> details;
};

struct RoutePlanningResponse {
    std::vector<Route> routes;   // 至少包含 1 条成功路线
    std::vector<Notice> notices; // 全局提示
};

} // namespace route_planning
```

响应约定：
- 成功时返回 RoutePlanningResponse；失败时返回 Error（见接口中的 Result<...>）。
- 单位：内部统一使用米、秒；文本层根据 Units 输出友好单位。

## 规划器接口约定

```cpp
namespace route_planning {

template <class T>
using Result = std::variant<T, Error>; // 成功或错误

struct BuildOptions {
    // 若使用 graph 模块作为底图
    bool directed{true};
    std::optional<std::string> region_tag; // 区域标识，便于多区域路网切换
};

class IRoutePlanner {
public:
    virtual ~IRoutePlanner() = default;

    // 同步规划
    virtual Result<RoutePlanningResponse> plan(const RoutePlanningRequest& req) const = 0;

    // 批量规划（独立求解）
    virtual std::vector<Result<RoutePlanningResponse>>
    plan_batch(const std::vector<RoutePlanningRequest>& reqs) const = 0;
};

// 工厂方法示例（可与 graph::Graph 解耦）
std::unique_ptr<IRoutePlanner> MakeRoutePlannerFromGraph(
    const void* graph_handle,
    const BuildOptions& opts = {}
);

} // namespace route_planning
```

线程安全：
- 建议 IRoutePlanner 实现为只读共享底图，可并发调用 plan。若包含可变缓存需内部同步或每线程实例化。

复杂度：
- 与底层算法相关（Dijkstra/A*、ALT/CH/MLD、时空扩展图等）。多约束旅游场景建议离线预处理+启发式。

## 参数校验与默认值

- 坐标：lat ∈ [-90,90]，lon ∈ [-180,180]，否则 `InvalidRequest`。
- 时间：departure_time 与 arrival_time 不能同时设置，否则 `InvalidRequest`。
- 模式：实现不支持的 mode 返回 `UnsupportedMode`。
- 可行性：时间窗/区域/避让导致不可达时返回 `NoRouteFound` 或 `TimeWindowViolation`。
- 备选：alternatives 建议 ≤ 3；超出可截断或返回 Notice。
- 单位：内部统一米/秒；Units 仅影响格式化输出。

## 常见错误码

- InvalidRequest: 请求不完整/越界
- UnsupportedMode: 当前实现不支持该模式
- NoRouteFound: 起终点不连通或约束过强
- GraphDisconnected: 底图缺失或分岛
- TimeWindowViolation: 与提供的时间窗矛盾
- Timeout: 在限定时间内未完成
- InternalError: 未分类内部错误

## 使用示例

最简规划：
```cpp
using namespace route_planning;

int main() {
    auto planner = MakeRoutePlannerFromGraph(nullptr, { .directed = true });

    RoutePlanningRequest req{};
    req.origin      = {31.2304, 121.4737}; // 上海
    req.destination = {31.1976, 121.5600};
    req.mode        = TravelMode::Driving;
    req.optimize    = OptimizeType::Fastest;
    req.avoid       = AvoidFlag::Tolls | AvoidFlag::Highways;
    req.alternatives = 1u;

    auto result = planner->plan(req);
    if (auto ok = std::get_if<RoutePlanningResponse>(&result)) {
        const auto& route = ok->routes.front();
        (void)route;
        return 0;
    } else {
        const auto& err = std::get<Error>(result);
        (void)err;
        return 1;
    }
}
```

带时间窗与步行无障碍：
```cpp
RoutePlanningRequest req{};
req.origin = {39.905, 116.391};
req.destination = {39.916, 116.397};
req.mode = TravelMode::Walking;
req.walking = WalkingOptions{
    .max_distance_m = 3000.0,
    .wheelchair_accessible = true,
    .avoid_stairs = true
};
req.optimize = OptimizeType::Scenic;
req.area_pref.prefer_areas.push_back(BBox{{39.90,116.38},{39.92,116.41}});
req.departure_time = std::chrono::system_clock::now();
```

## JSON 映射建议（可选）

- 若对外提供 HTTP API，可将以下字段映射：
  - GeoPoint: { "lat": double, "lon": double, "ele": double? }
  - TimeWindow: ISO-8601 字符串（UTC），如 "2025-10-15T09:30:00Z"
  - 枚举: 使用字符串或约定的整数码
  - polyline: 可提供坐标数组或编码折线字符串（需注明编码方案）
- 错误返回：HTTP 4xx/5xx 搭配 Error 对象，code 映射 ErrorCode。

## 与 graph 模块的关系（可选）

- 可将 `graph::Graph` 作为底层路网结构，权重表示时间或综合代价。
- Driving/Walking/Cycling 可通过过滤边（如 Highways/Unpaved/Stairs）与切换权重实现模式差异。
- Transit 建议使用时空扩展图或对接外部换乘引擎。

## 版本与兼容性

- 0.1.0: 初版数据模型与接口约定。
- 后续变更遵循“仅新增字段为主”的向后兼容策略；删除或语义变更将提升主版本号。