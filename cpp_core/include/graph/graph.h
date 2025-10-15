#pragma once
#include <unordered_set>
#include <unordered_map>
#include <vector>
#include <utility>

namespace graph {

class Graph {
public:
    using id_type = int;
    using weight_type = double;

    bool add_vertex(id_type id);
    bool has_vertex(id_type id) const;
    void add_edge(id_type src, id_type dst, weight_type weight = 1.0);

    const std::unordered_set<id_type>& vertices() const { return vertices_; }
    const std::vector<std::pair<id_type, weight_type>>& neighbors(id_type src) const;

private:
    std::unordered_set<id_type> vertices_;
    std::unordered_map<id_type, std::vector<std::pair<id_type, weight_type>>> adj_;
    static const std::vector<std::pair<id_type, weight_type>> empty_;
};

} // namespace graph