#include "graph/graph.h"

namespace graph {

const std::vector<std::pair<Graph::id_type, Graph::weight_type>> Graph::empty_ = {};

bool Graph::add_vertex(id_type id) {
    return vertices_.insert(id).second;
}

bool Graph::has_vertex(id_type id) const {
    return vertices_.find(id) != vertices_.end();
}

void Graph::add_edge(id_type src, id_type dst, weight_type weight) {
    vertices_.insert(src);
    vertices_.insert(dst);
    adj_[src].emplace_back(dst, weight);
}

const std::vector<std::pair<Graph::id_type, Graph::weight_type>>&
Graph::neighbors(id_type src) const {
    auto it = adj_.find(src);
    if (it == adj_.end()) return empty_;
    return it->second;
}

} // namespace graph