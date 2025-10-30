#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "../../include/algorithms/inverted_index.h"
#include "../../include/algorithms/sorting.h"


namespace py = pybind11;

/**
 * @brief 推荐模块Python绑定
 */
PYBIND11_MODULE(recommendation_core, m) {
    m.doc() = "个性化旅游推荐系统核心算法模块";
    
    // RecommendationItem 绑定
    py::class_<recommendation::RecommendationItem>(m, "RecommendationItem")
        .def(py::init<>())
        .def_readwrite("attraction_id", &recommendation::RecommendationItem::attraction_id)
        .def_readwrite("name", &recommendation::RecommendationItem::name)
        .def_readwrite("type", &recommendation::RecommendationItem::type)
        .def_readwrite("score", &recommendation::RecommendationItem::score)
        .def_readwrite("popularity", &recommendation::RecommendationItem::popularity)
        .def_readwrite("rating", &recommendation::RecommendationItem::rating)
        .def("__repr__", [](const recommendation::RecommendationItem& item) {
            return "RecommendationItem(id=" + std::to_string(item.attraction_id) + 
                   ", name=" + item.name + ", score=" + std::to_string(item.score) + ")";
        });
    
    // 排序算法绑定
    m.def("heap_sort_top_n", &recommendation::heapSortTopN, 
          "使用堆排序算法获取Top-N推荐",
          py::arg("items"), py::arg("top_n"), py::arg("comparator"));
    
    m.def("quick_select_top_n", &recommendation::quickSelectTopN, 
          "使用快速选择算法获取Top-N热门推荐",
          py::arg("items"), py::arg("top_n"), py::arg("comparator"));
    
    // 预定义比较器
    m.def("content_based_comparator", &recommendation::contentBasedComparator,
          "基于内容推荐的比较器");
    
    m.def("popularity_comparator", &recommendation::popularityComparator,
          "基于热度的比较器");
    
    m.def("rating_comparator", &recommendation::ratingComparator,
          "基于评分的比较器");
    
    // SearchResult 绑定
    py::class_<recommendation::SearchResult>(m, "SearchResult")
        .def(py::init<>())
        .def_readwrite("attraction_id", &recommendation::SearchResult::attraction_id)
        .def_readwrite("name", &recommendation::SearchResult::name)
        .def_readwrite("type", &recommendation::SearchResult::type)
        .def_readwrite("relevance_score", &recommendation::SearchResult::relevance_score)
        .def_readwrite("match_field", &recommendation::SearchResult::match_field)
        .def_readwrite("highlight", &recommendation::SearchResult::highlight)
        .def("__repr__", [](const recommendation::SearchResult& result) {
            return "SearchResult(id=" + std::to_string(result.attraction_id) + 
                   ", name=" + result.name + ", score=" + std::to_string(result.relevance_score) + 
                   ", field=" + result.match_field + ")";
        });
    
    // Attraction 绑定
    py::class_<recommendation::Attraction>(m, "Attraction")
        .def(py::init<>())
        .def_readwrite("id", &recommendation::Attraction::id)
        .def_readwrite("name", &recommendation::Attraction::name)
        .def_readwrite("type", &recommendation::Attraction::type)
        .def_readwrite("description", &recommendation::Attraction::description)
        .def("__repr__", [](const recommendation::Attraction& attr) {
            return "Attraction(id=" + std::to_string(attr.id) + 
                   ", name=" + attr.name + ", type=" + attr.type + ")";
        });
    
    // InvertedIndex 类绑定
    py::class_<recommendation::InvertedIndex>(m, "InvertedIndex")
        .def(py::init<>())
        .def("add_attraction", &recommendation::InvertedIndex::addAttraction,
             "添加景点到倒排索引", py::arg("attraction"))
        .def("search", &recommendation::InvertedIndex::search,
             "搜索景点", py::arg("query"), 
             py::arg("search_type") = "all", 
             py::arg("limit") = 20)
        .def("tokenize", &recommendation::InvertedIndex::tokenize,
             "文本分词", py::arg("text"))
        .def("normalize_token", &recommendation::InvertedIndex::normalizeToken,
             "令牌标准化", py::arg("token"));
    
    // 模块信息
    m.attr("__version__") = "1.0.0";
    m.attr("__author__") = "甘和君";
    m.attr("__description__") = "个性化旅游推荐系统核心算法";
    
    // 导出常量
    m.attr("DEFAULT_TOP_N") = 10;
    m.attr("MAX_SEARCH_LIMIT") = 100;
}

/**
 * @brief 示例使用代码
 */
void example_usage() {
    /**
     * Python示例使用代码：
     * 
     * import recommendation_core as rc
     * 
     * # 个性化推荐示例
     * items = [
     *     rc.RecommendationItem(attraction_id=1, name="故宫", score=0.95, popularity=0.8, rating=4.7),
     *     rc.RecommendationItem(attraction_id=2, name="颐和园", score=0.88, popularity=0.9, rating=4.8),
     *     # ... 更多景点
     * ]
     * 
     * # 使用堆排序获取Top-5推荐
     * top_recommendations = rc.heap_sort_top_n(
     *     items, 
     *     5, 
     *     rc.content_based_comparator
     * )
     * 
     * # 倒排索引搜索示例
     * index = rc.InvertedIndex()
     * attraction = rc.Attraction(id=1, name="故宫博物院", type="历史景点", description="中国古代宫殿建筑")
     * index.add_attraction(attraction)
     * 
     * results = index.search("故宫", "all", 10)
     * for result in results:
     *     print(f"景点: {result.name}, 相关度: {result.relevance_score}")
     */
}