#pragma once
#include <unordered_set>
#include <unordered_map>
#include <vector>
#include <utility>
#include <string>   // 新增
#include <cstddef>  // 新增

namespace graph {

class Graph {
public:
    using id_type = int;
    using weight_type = double;

    bool add_vertex(id_type id);
    bool has_vertex(id_type id) const;
    void add_edge(id_type src, id_type dst, weight_type weight = 1.0);

    // ...existing code...
    // ------------- 新增接口 -------------
    // 删除顶点：移除该点、其出边、以及指向该点的入边
    bool remove_vertex(id_type id);

    // 删除边：默认移除所有平行边；remove_all_parallel=false 时仅移除一条
    bool remove_edge(id_type src, id_type dst, bool remove_all_parallel = true);

    // 查询边是否存在
    bool has_edge(id_type src, id_type dst) const;

    // 统计
    size_t vertex_count() const noexcept { return vertices_.size(); }
    size_t edge_count() const noexcept;

    const std::unordered_set<id_type>& vertices() const { return vertices_; }
    const std::vector<std::pair<id_type, weight_type>>& neighbors(id_type src) const;

    // ------------- 序列化/反序列化 -------------
    // 行文本格式：
    // PTS-GRAPH 1
    // V <nV> E <nE>
    // v <id>
    // e <src> <dst> <weight>
    bool save_to_file(const std::string& path) const;
    static Graph load_from_file(const std::string& path);

private:
    std::unordered_set<id_type> vertices_;
    std::unordered_map<id_type, std::vector<std::pair<id_type, weight_type>>> adj_;
    static const std::vector<std::pair<id_type, weight_type>> empty_;
};

} // namespace graph