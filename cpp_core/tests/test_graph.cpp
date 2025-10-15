#include <iostream>
#include <cassert>
#include <cmath>
#include "graph/edge.h"
#include "graph/graph.h"

static bool approx(double a, double b, double eps = 1e-9) {
    return std::fabs(a - b) <= eps;
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

    cout << "[Graph] ok: vertices=" << g.vertices().size() << endl;
    cout << "All tests passed." << endl;
    return 0;
}