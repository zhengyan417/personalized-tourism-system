#include <iostream>
#include <cassert>
#include <cmath>
#include <queue>      // 新增
#include <vector>     // 新增
#include <limits>     // 新增
#include <string>     // 新增
#include <unordered_map>  // 新增：BFS 中使用
#include "graph/edge.h"
#include "graph/graph.h"

static bool approx(double a, double b, double eps = 1e-9) {
    return std::fabs(a - b) <= eps;
}

static void build_grid_graph(graph::Graph& g, int rows, int cols, graph::Graph::weight_type w = 1.0) {
    // 顶点 id: r*cols + c + 1
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            int id = r * cols + c + 1;
            g.add_vertex(id);
        }
    }
    // 4-邻接（双向有向边）
    auto id_of = [cols](int r, int c){ return r * cols + c + 1; };
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < cols; ++c) {
            int u = id_of(r, c);
            if (c + 1 < cols) { // 右
                int v = id_of(r, c + 1);
                g.add_edge(u, v, w);
                g.add_edge(v, u, w);
            }
            if (r + 1 < rows) { // 下
                int v = id_of(r + 1, c);
                g.add_edge(u, v, w);
                g.add_edge(v, u, w);
            }
        }
    }
}

static int bfs_shortest_steps(const graph::Graph& g, int start, int goal) {
    if (start == goal) return 0;
    std::unordered_map<int, int> dist;
    std::queue<int> q;
    dist[start] = 0;
    q.push(start);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (const auto& p : g.neighbors(u)) {
            int v = p.first;
            if (!dist.count(v)) {
                dist[v] = dist[u] + 1;
                if (v == goal) return dist[v];
                q.push(v);
            }
        }
    }
    return std::numeric_limits<int>::max(); // 不可达
}

int main() {
    using std::cout;
    using std::endl;
    using graph::Graph;

    // Edge 基础测试
    {
        graph::Edge<double> e(10, 20, 3.5);
        assert(e.src() == 10);
        assert(e.dst() == 20);
        assert(approx(e.weight(), 3.5));
        cout << "[Edge] ok: src=" << e.src() << " dst=" << e.dst() << " w=" << e.weight() << endl;
    }

    // Graph 基础测试
    Graph g;
    assert(!g.has_vertex(1));
    assert(g.add_vertex(1) == true);
    assert(g.add_vertex(1) == false);
    assert(g.has_vertex(1));

    g.add_edge(1, 2, 2.5);
    assert(g.has_vertex(2));
    assert(g.has_edge(1, 2));

    {
        const auto& nbrs1 = g.neighbors(1);
        assert(nbrs1.size() == 1);
        assert(nbrs1[0].first == 2);
        assert(approx(nbrs1[0].second, 2.5));

        const auto& nbrs2 = g.neighbors(2);
        assert(nbrs2.empty());
    }

    g.add_edge(1, 3, 1.0);
    g.add_edge(3, 4, 4.2);
    assert(g.has_vertex(3) && g.has_vertex(4));

    {
        const auto& nbrs1 = g.neighbors(1);
        assert(nbrs1.size() == 2);
        bool has_2 = false, has_3 = false;
        for (auto& p : nbrs1) {
            if (p.first == 2 && approx(p.second, 2.5)) has_2 = true;
            if (p.first == 3 && approx(p.second, 1.0)) has_3 = true;
        }
        assert(has_2 && has_3);

        const auto& nbrs3 = g.neighbors(3);
        assert(nbrs3.size() == 1);
        assert(nbrs3[0].first == 4 && approx(nbrs3[0].second, 4.2));

        const auto& nbrs999 = g.neighbors(999);
        assert(nbrs999.empty());
    }

    // 删除边/顶点验证
    assert(g.remove_edge(1, 2));        // 删除 1->2
    assert(!g.has_edge(1, 2));
    assert(g.remove_vertex(4));         // 删除顶点4，同时移除 3->4
    assert(!g.has_edge(3, 4));
    cout << "[Graph] ok: basic remove ops" << endl;

    // ------------- 构建道路网络（225 顶点，840 边）并验证遍历与序列化 -------------
    Graph big;
    const int R = 15, C = 15; // 15x15 网格
    build_grid_graph(big, R, C, 1.0);
    const size_t expected_vertices = static_cast<size_t>(R) * static_cast<size_t>(C); // 225
    const size_t undirected_edges = static_cast<size_t>(R) * (C - 1) + static_cast<size_t>(C) * (R - 1); // 420
    const size_t expected_directed_edges = undirected_edges * 2; // 840

    assert(big.vertex_count() == expected_vertices);
    assert(big.edge_count() == expected_directed_edges);

    // BFS 最短步数（曼哈顿距离）：从 (0,0)->(R-1,C-1)
    auto id_of = [C](int r, int c){ return r * C + c + 1; };
    int start = id_of(0, 0);
    int goal  = id_of(R - 1, C - 1);
    int steps = bfs_shortest_steps(big, start, goal);
    assert(steps == (R - 1) + (C - 1)); // 28
    cout << "[Graph] ok: BFS shortest steps=" << steps << endl;

    // 邻接 spot-check: 1 的邻居应为 2 与 1+15=16
    {
        const auto& nbrs = big.neighbors(1);
        assert(nbrs.size() == 2);
        bool has2 = false, has16 = false;
        for (auto& p : nbrs) {
            if (p.first == 2) has2 = true;
            if (p.first == 16) has16 = true;
        }
        assert(has2 && has16);
    }

    // 序列化/反序列化一致性
    const std::string path = "test_graph_io.txt";
    assert(big.save_to_file(path) && "save_to_file failed");
    Graph loaded = Graph::load_from_file(path);
    assert(loaded.vertex_count() == big.vertex_count());
    assert(loaded.edge_count() == big.edge_count());
    // 再做一次 BFS 验证
    int steps2 = bfs_shortest_steps(loaded, start, goal);
    assert(steps2 == steps);
    cout << "[Graph] ok: serialize/deserialize verified" << endl;

    cout << "[Graph] ok: vertices=" << big.vertices().size()
         << " edges=" << big.edge_count() << endl;
    cout << "All tests passed." << endl;
    return 0;
}