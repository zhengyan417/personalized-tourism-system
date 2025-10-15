#pragma once
#include <utility>

namespace graph {

template <typename T>
class Vertex {
public:
    using id_type = int;
    using data_type = T;

    Vertex(id_type id, const T& data) : id_(id), data_(data) {}
    Vertex(id_type id, T&& data) : id_(id), data_(std::move(data)) {}

    id_type id() const noexcept { return id_; }
    const T& data() const noexcept { return data_; }
    T& data() noexcept { return data_; }

    void set_data(const T& v) { data_ = v; }
    void set_data(T&& v) { data_ = std::move(v); }

private:
    id_type id_;
    T data_;
};

} // namespace graph