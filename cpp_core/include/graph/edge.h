#pragma once

namespace graph {

template <typename W = double>
class Edge {
public:
    using id_type = int;
    using weight_type = W;

    Edge(id_type src, id_type dst, const W& w = W{}) : src_(src), dst_(dst), weight_(w) {}

    id_type src() const noexcept { return src_; }
    id_type dst() const noexcept { return dst_; }
    const W& weight() const noexcept { return weight_; }
    void set_weight(const W& w) { weight_ = w; }

private:
    id_type src_;
    id_type dst_;
    W weight_;
};

} // namespace graph