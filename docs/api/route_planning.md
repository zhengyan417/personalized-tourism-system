# 路径规划模块 API 文档（C++）

版本: 0.1.0  
命名空间: `route_planning`  
依赖: C++20 标准库（<vector>, <string>, <optional>, <chrono>, <cstdint>, <limits>），可选依赖 `graph` 模块作为底层拓扑。

本模块提供路径规划请求/响应的数据模型与规划器接口约定，适用于驾驶、步行、骑行等常见出行方式，并兼容旅游场景中的偏好与约束（如避让景区拥堵、开放时间窗口、费用/碳排优化等）。

## 头文件组织建议
- route_planning/types.hpp
- route_planning/request.hpp
- route_planning/response.hpp
- route_planning/route_planner.hpp

示例引用:
```cpp
#include "route_planning/route_planner.hpp"
#include "route_planning/request.hpp"
#include "route_planning/response.hpp"
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
    Scenic,     // 风景优先（更偏景观道路/POI）
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
inline AvoidFlag operator|(AvoidFlag a, AvoidFlag b) { return static_cast<AvoidFlag>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b)); }
inline bool has_flag(AvoidFlag v, AvoidFlag f) { return (static_cast<uint32_t>(v) & static_cast<uint32_t>(f)) != 0; }

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
    bool realtime{false};                 // 实时班次
    std::optional<uint32_t> max_transfers; // 最大换乘次数
    std::optional<TimeWindow> time_window; // 可行驶/游览时间窗
};

struct WalkingOptions {
    std::optional<double> max_distance_m; // 最大步行距离
    bool wheelchair_accessible{false};    // 无障碍优先
    bool avoid_stairs{false};
};

struct DrivingOptions {
    bool traffic_aware{false};            // 交通拥堵感知（需外部数据）
    std::optional<double> max_speed_kph;  // 限速
};

struct CyclingOptions {
    bool avoid_unpaved{true};
    bool prefer_bikelanes{true};
};

struct RoutePlanningRequest {
    GeoPoint origin;
    GeoPoint destination;
    std::vector<GeoPoint> waypoints;      // 途经点（可空）
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

    // 校验约束:
    // - 坐标必须在合法范围
    // - departure_time 与 arrival_time 不能同时设置
    // - alternatives 建议不超过 3
};

} // namespace route_planning
```

字段说明（要点）:
- origin/destination/waypoints: WGS84，经纬度小数度；NaN 或越界视为无效。
- mode/optimize: 选择出行方式与优化目标；当提供 cost_model 时，optimize 作为预设可覆盖。
- avoid: 叠加避让项，如 AvoidFlag::Tolls | AvoidFlag::Highways。
- area_pref: 旅游场景可通过 prefer_areas 引导经过风景区。
- time fields: departure_time 与 arrival_time 二选一；不提供则使用“当前时间”作为默认。
- transit/walking/driving/cycling: 按模式生效，其他模式忽略。

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
    std::vector<GeoPoint> polyline;  // 步进几何（可选：改为编码折线）
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
    std::string id;               // 唯一路径标识
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
    std::vector<Route> routes;       // 至少包含 1 条成功路线
    std::vector<Notice> notices;     // 全局提示
};

} // namespace route_planning
```

## 规划器接口约定

```cpp
namespace route_planning {

template <class T>
using Result = std::variant<T, Error>; // 成功或错误

struct BuildOptions {
    // 以 graph::Graph 为底图构建的可选参数（若使用 graph 模块）
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

// 工厂方法示例（可根据项目选择是否显式暴露）
std::unique_ptr<IRoutePlanner> MakeRoutePlannerFromGraph(
    const void* graph_handle, // 可与 graph::Graph 解耦的句柄或桥接
    const BuildOptions& opts = {}
);

} // namespace route_planning
```

线程安全:
- IRoutePlanner 的 `plan` 可并发调用，前提是实现为只读共享底图；如包含可变缓存，应使用内部并发控制或为每线程实例化。

时间复杂度:
- 取决于底层算法（Dijkstra/A*、ALT/CH/MLD 等）；在旅游多约束下建议离线预处理+启发式加速。

## 参数校验与默认值

- 坐标范围: lat ∈ [-90,90]，lon ∈ [-180,180]；否则返回 `InvalidRequest`。
- 时间参数: `departure_time` 与 `arrival_time` 不能同时出现；同时出现返回 `InvalidRequest`。
- 模式支持: 若实现未开启某模式，返回 `UnsupportedMode`。
- 约束冲突: 例如 `avoid_stairs=true` 且 `wheelchair_accessible=false` 并要求通过仅含楼梯的连通段，返回 `ConstraintConflict`。
- 备选数量: `alternatives` 建议 ≤ 3，超出可截断或返回提示 Notice。

## 常见错误码

- InvalidRequest: 请求字段不完整或超出范围
- NoRouteFound: 起终点不连通或约束过强
- GraphDisconnected: 底图缺失或分岛
- TimeWindowViolation: 对景点/换乘时间窗不可行
- Timeout: 算法在限定时间内未完成
- InternalError: 未分类内部故障

## 使用示例

最简规划:
```cpp
#include "route_planning/route_planner.hpp"
#include "route_planning/request.hpp"
#include "route_planning/response.hpp"

using namespace route_planning;

int main() {
    auto planner = MakeRoutePlannerFromGraph(/*graph_handle*/ nullptr, { .directed = true });

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
        // 使用 route.summary / route.polyline / route.legs
        return 0;
    } else {
        const auto& err = std::get<Error>(result);
        // 处理错误
        return 1;
    }
}
```

带时间窗与步行无障碍:
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

## 单位与坐标

- 默认单位为 Metric；若设置为 Imperial，距离以英里/英尺表示于文本层（内部计算仍使用米/秒）。
- polyline 提供原始点串；若需压缩，可在实现中采用编码折线（例如 Google Polyline 算法）对外另暴露 `std::string encoded_polyline`。

## 与 graph 模块的关系（可选）

- 可将 `graph::Graph<VData, WeightT, EData>` 作为底层路网，边权重可表示时间或综合代价。
- 在 Driving/Walking/Cycling 模式下，通过映射不同权重或约束过滤边集（如避开 Unpaved、Highways）。
- Transit 需要时空扩展图（时刻表边），或外部换乘引擎对接。

## 版本与兼容性

- 0.1.0: 初版数据模型与接口约定。
- 后续可能新增字段时遵循“仅新增，少移除”的向后兼容策略；删除或变更语义将提升主版本号。

```// filepath: /docs/api/route-planning.md
# 路径规划模块 API 文档（C++）

版本: 0.1.0  
命名空间: `route_planning`  
依赖: C++20 标准库（<vector>, <string>, <optional>, <chrono>, <cstdint>, <limits>），可选依赖 `graph` 模块作为底层拓扑。

本模块提供路径规划请求/响应的数据模型与规划器接口约定，适用于驾驶、步行、骑行等常见出行方式，并兼容旅游场景中的偏好与约束（如避让景区拥堵、开放时间窗口、费用/碳排优化等）。

## 头文件组织建议
- route_planning/types.hpp
- route_planning/request.hpp
- route_planning/response.hpp
- route_planning/route_planner.hpp

示例引用:
```cpp
#include "route_planning/route_planner.hpp"
#include "route_planning/request.hpp"
#include "route_planning/response.hpp"
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
    Scenic,     // 风景优先（更偏景观道路/POI）
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
inline AvoidFlag operator|(AvoidFlag a, AvoidFlag b) { return static_cast<AvoidFlag>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b)); }
inline bool has_flag(AvoidFlag v, AvoidFlag f) { return (static_cast<uint32_t>(v) & static_cast<uint32_t>(f)) != 0; }

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
    bool realtime{false};                 // 实时班次
    std::optional<uint32_t> max_transfers; // 最大换乘次数
    std::optional<TimeWindow> time_window; // 可行驶/游览时间窗
};

struct WalkingOptions {
    std::optional<double> max_distance_m; // 最大步行距离
    bool wheelchair_accessible{false};    // 无障碍优先
    bool avoid_stairs{false};
};

struct DrivingOptions {
    bool traffic_aware{false};            // 交通拥堵感知（需外部数据）
    std::optional<double> max_speed_kph;  // 限速
};

struct CyclingOptions {
    bool avoid_unpaved{true};
    bool prefer_bikelanes{true};
};

struct RoutePlanningRequest {
    GeoPoint origin;
    GeoPoint destination;
    std::vector<GeoPoint> waypoints;      // 途经点（可空）
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

    // 校验约束:
    // - 坐标必须在合法范围
    // - departure_time 与 arrival_time 不能同时设置
    // - alternatives 建议不超过 3
};

} // namespace route_planning
```

字段说明（要点）:
- origin/destination/waypoints: WGS84，经纬度小数度；NaN 或越界视为无效。
- mode/optimize: 选择出行方式与优化目标；当提供 cost_model 时，optimize 作为预设可覆盖。
- avoid: 叠加避让项，如 AvoidFlag::Tolls | AvoidFlag::Highways。
- area_pref: 旅游场景可通过 prefer_areas 引导经过风景区。
- time fields: departure_time 与 arrival_time 二选一；不提供则使用“当前时间”作为默认。
- transit/walking/driving/cycling: 按模式生效，其他模式忽略。

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
    std::vector<GeoPoint> polyline;  // 步进几何（可选：改为编码折线）
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
    std::string id;               // 唯一路径标识
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
    std::vector<Route> routes;       // 至少包含 1 条成功路线
    std::vector<Notice> notices;     // 全局提示
};

} // namespace route_planning
```

## 规划器接口约定

```cpp
namespace route_planning {

template <class T>
using Result = std::variant<T, Error>; // 成功或错误

struct BuildOptions {
    // 以 graph::Graph 为底图构建的可选参数（若使用 graph 模块）
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

// 工厂方法示例（可根据项目选择是否显式暴露）
std::unique_ptr<IRoutePlanner> MakeRoutePlannerFromGraph(
    const void* graph_handle, // 可与 graph::Graph 解耦的句柄或桥接
    const BuildOptions& opts = {}
);

} // namespace route_planning
```

线程安全:
- IRoutePlanner 的 `plan` 可并发调用，前提是实现为只读共享底图；如包含可变缓存，应使用内部并发控制或为每线程实例化。

时间复杂度:
- 取决于底层算法（Dijkstra/A*、ALT/CH/MLD 等）；在旅游多约束下建议离线预处理+启发式加速。

## 参数校验与默认值

- 坐标范围: lat ∈ [-90,90]，lon ∈ [-180,180]；否则返回 `InvalidRequest`。
- 时间参数: `departure_time` 与 `arrival_time` 不能同时出现；同时出现返回 `InvalidRequest`。
- 模式支持: 若实现未开启某模式，返回 `UnsupportedMode`。
- 约束冲突: 例如 `avoid_stairs=true` 且 `wheelchair_accessible=false` 并要求通过仅含楼梯的连通段，返回 `ConstraintConflict`。
- 备选数量: `alternatives` 建议 ≤ 3，超出可截断或返回提示 Notice。

## 常见错误码

- InvalidRequest: 请求字段不完整或超出范围
- NoRouteFound: 起终点不连通或约束过强
- GraphDisconnected: 底图缺失或分岛
- TimeWindowViolation: 对景点/换乘时间窗不可行
- Timeout: 算法在限定时间内未完成
- InternalError: 未分类内部故障

## 使用示例

最简规划:
```cpp
#include "route_planning/route_planner.hpp"
#include "route_planning/request.hpp"
#include "route_planning/response.hpp"

using namespace route_planning;

int main() {
    auto planner = MakeRoutePlannerFromGraph(/*graph_handle*/ nullptr, { .directed = true });

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
        // 使用 route.summary / route.polyline / route.legs
        return 0;
    } else {
        const auto& err = std::get<Error>(result);
        // 处理错误
        return 1;
    }
}
```

带时间窗与步行无障碍:
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

## 单位与坐标

- 默认单位为 Metric；若设置为 Imperial，距离以英里/英尺表示于文本层（内部计算仍使用米/秒）。
- polyline 提供原始点串；若需压缩，可在实现中采用编码折线（例如 Google Polyline 算法）对外另暴露 `std::string encoded_polyline`。

## 与 graph 模块的关系（可选）

- 可将 `graph::Graph<VData, WeightT, EData>` 作为底层路网，边权重可表示时间或综合代价。
- 在 Driving/Walking/Cycling 模式下，通过映射不同权重或约束过滤边集（如避开 Unpaved、Highways）。
- Transit 需要时空扩展图（时刻表边），或外部换乘引擎对接。

## 版本与兼容性

- 0.1.0: 初版数据模型与接口约定。
- 后续可能新增字段时遵循“仅新增，少移除”的向后兼容策略；删除或变更语义将提