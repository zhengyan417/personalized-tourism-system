#include "graph/graph.h"
#include <fstream>    // 新增
#include <sstream>    // 新增
#include <string>     // 新增
#include <algorithm>  // 新增

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

// ...existing code...
bool Graph::remove_vertex(id_type id) {
    bool existed = vertices_.erase(id) > 0;
    // 移除出边
    adj_.erase(id);
    // 移除所有指向该顶点的入边
    for (auto& kv : adj_) {
        auto& vec = kv.second;
        vec.erase(std::remove_if(vec.begin(), vec.end(),
                                 [id](const auto& p){ return p.first == id; }),
                  vec.end());
    }
    return existed;
}

bool Graph::remove_edge(id_type src, id_type dst, bool remove_all_parallel) {
    auto it = adj_.find(src);
    if (it == adj_.end()) return false;
    auto& vec = it->second;

    bool removed = false;
    if (remove_all_parallel) {
        auto old_size = vec.size();
        vec.erase(std::remove_if(vec.begin(), vec.end(),
                                 [dst](const auto& p){ return p.first == dst; }),
                  vec.end());
        removed = vec.size() != old_size;
    } else {
        auto pos = std::find_if(vec.begin(), vec.end(),
                                [dst](const auto& p){ return p.first == dst; });
        if (pos != vec.end()) {
            vec.erase(pos);
            removed = true;
        }
    }
    return removed;
}

bool Graph::has_edge(id_type src, id_type dst) const {
    auto it = adj_.find(src);
    if (it == adj_.end()) return false;
    const auto& vec = it->second;
    return std::any_of(vec.begin(), vec.end(),
                       [dst](const auto& p){ return p.first == dst; });
}

size_t Graph::edge_count() const noexcept {
    size_t sum = 0;
    for (const auto& kv : adj_) sum += kv.second.size();
    return sum;
}

const std::vector<std::pair<Graph::id_type, Graph::weight_type>>&
Graph::neighbors(id_type src) const {
    auto it = adj_.find(src);
    if (it == adj_.end()) return empty_;
    return it->second;
}

bool Graph::save_to_file(const std::string& path) const {
    std::ofstream ofs(path, std::ios::out | std::ios::trunc);
    if (!ofs.is_open()) return false;

    ofs << "PTS-GRAPH 1\n";
    ofs << "V " << vertices_.size() << " E " << edge_count() << "\n";
    for (auto id : vertices_) {
        ofs << "v " << id << "\n";
    }
    for (const auto& kv : adj_) {
        const auto src = kv.first;
        for (const auto& e : kv.second) {
            ofs << "e " << src << " " << e.first << " " << e.second << "\n";
        }
    }
    return ofs.good();
}

Graph Graph::load_from_file(const std::string& path) {
    Graph g;
    std::ifstream ifs(path);
    if (!ifs.is_open()) return g;

    std::string line;
    while (std::getline(ifs, line)) {
        // 跳过空行与注释
        if (line.empty() || line[0] == '#') continue;

        std::istringstream iss(line);
        std::string tag;
        if (!(iss >> tag)) continue;

        if (tag == "v") {
            id_type id{};
            if (iss >> id) g.add_vertex(id);
        } else if (tag == "e") {
            id_type s{}, d{};
            weight_type w{1.0};
            if (iss >> s >> d) {
                if (!(iss >> w)) w = 1.0;
                g.add_edge(s, d, w);
            }
        } else {
            // 可选头信息：PTS-GRAPH / V / E 行，忽略
            continue;
        }
    }
    return g;
}

} // namespace graph