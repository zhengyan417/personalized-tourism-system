#include <vector>
#include <algorithm>
#include <functional>
#include <queue>
#include <iostream>
#include "../../include/algorithms/sorting.h"

namespace recommendation {

/**
 * @brief 使用堆排序获取Top-N推荐结果
 * @param items 待排序的推荐项列表
 * @param top_n 返回的推荐数量
 * @param comparator 比较函数
 * @return Top-N推荐结果
 */
std::vector<RecommendationItem> heapSortTopN(
    const std::vector<RecommendationItem>& items, 
    int top_n,
    std::function<bool(const RecommendationItem&, const RecommendationItem&)> comparator) {
    
    if (items.empty() || top_n <= 0) {
        return {};
    }

    // 使用最小堆来维护Top-N元素
    auto minHeapComparator = [&comparator](const RecommendationItem& a, const RecommendationItem& b) {
        return comparator(b, a); // 反转比较器以创建最小堆
    };
    
    std::priority_queue<RecommendationItem, 
                       std::vector<RecommendationItem>, 
                       decltype(minHeapComparator)> min_heap(minHeapComparator);

    // 构建大小为top_n的最小堆
    for (const auto& item : items) {
        if (min_heap.size() < top_n) {
            min_heap.push(item);
        } else if (comparator(item, min_heap.top())) {
            min_heap.pop();
            min_heap.push(item);
        }
    }

    // 从堆中提取结果（逆序）
    std::vector<RecommendationItem> result;
    result.reserve(min_heap.size());
    while (!min_heap.empty()) {
        result.push_back(min_heap.top());
        min_heap.pop();
    }

    // 反转结果使其按分数降序排列
    std::reverse(result.begin(), result.end());
    return result;
}

/**
 * @brief 快速选择算法 - 分区函数
 */
int quickSelectPartition(std::vector<RecommendationItem>& items, int left, int right,
                        std::function<bool(const RecommendationItem&, const RecommendationItem&)> comparator) {
    RecommendationItem pivot = items[right];
    int i = left - 1;
    
    for (int j = left; j < right; j++) {
        if (comparator(items[j], pivot)) {
            i++;
            std::swap(items[i], items[j]);
        }
    }
    std::swap(items[i + 1], items[right]);
    return i + 1;
}

/**
 * @brief 快速选择算法实现
 */
RecommendationItem quickSelect(std::vector<RecommendationItem>& items, int left, int right, int k,
                              std::function<bool(const RecommendationItem&, const RecommendationItem&)> comparator) {
    if (left == right) {
        return items[left];
    }

    int pivot_index = quickSelectPartition(items, left, right, comparator);
    
    if (k == pivot_index) {
        return items[k];
    } else if (k < pivot_index) {
        return quickSelect(items, left, pivot_index - 1, k, comparator);
    } else {
        return quickSelect(items, pivot_index + 1, right, k, comparator);
    }
}

/**
 * @brief 使用快速选择算法获取Top-N热门推荐
 * @param items 推荐项列表
 * @param top_n 返回的推荐数量
 * @param comparator 比较函数（基于热度或评分）
 * @return Top-N热门推荐
 */
std::vector<RecommendationItem> quickSelectTopN(
    std::vector<RecommendationItem>& items, 
    int top_n,
    std::function<bool(const RecommendationItem&, const RecommendationItem&)> comparator) {
    
    if (items.empty() || top_n <= 0) {
        return {};
    }

    top_n = std::min(top_n, static_cast<int>(items.size()));
    
    // 使用快速选择找到第top_n大的元素
    quickSelect(items, 0, items.size() - 1, top_n - 1, comparator);
    
    // 取前top_n个元素
    std::vector<RecommendationItem> result(items.begin(), items.begin() + top_n);
    
    // 对结果进行排序
    std::sort(result.begin(), result.end(), comparator);
    
    return result;
}

/**
 * @brief 基于内容推荐的比较器
 */
bool contentBasedComparator(const RecommendationItem& a, const RecommendationItem& b) {
    return a.score > b.score; // 按推荐分数降序
}

/**
 * @brief 基于热度的比较器
 */
bool popularityComparator(const RecommendationItem& a, const RecommendationItem& b) {
    return a.popularity > b.popularity; // 按热度降序
}

/**
 * @brief 基于评分的比较器
 */
bool ratingComparator(const RecommendationItem& a, const RecommendationItem& b) {
    return a.rating > b.rating; // 按评分降序
}

} // namespace recommendation