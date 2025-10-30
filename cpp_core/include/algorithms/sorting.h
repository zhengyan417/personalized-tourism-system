/**
 * @file sorting.h
 * @brief 推荐模块排序算法头文件
 * @author 甘和君
 * @date 第6周
 */

#pragma once

#include <vector>
#include <functional>
#include <string>

namespace recommendation {

/**
 * @brief 推荐项数据结构
 */
struct RecommendationItem {
    int attraction_id;      ///< 景点ID
    std::string name;       ///< 景点名称
    std::string type;       ///< 景点类型
    double score;           ///< 推荐分数（用于个性化推荐）
    double popularity;      ///< 热度（0.0-1.0）
    double rating;          ///< 评分（0.0-5.0）
    int visitor_count;      ///< 访客数量
    
    /**
     * @brief 默认构造函数
     */
    RecommendationItem() 
        : attraction_id(0), 
          score(0.0), 
          popularity(0.0), 
          rating(0.0), 
          visitor_count(0) {}
};

/**
 * @brief 使用堆排序算法获取Top-N推荐结果
 * 
 * 基于用户历史行为和偏好特征，使用堆排序算法返回Top-N个性化景点推荐列表。
 * 时间复杂度：O(N log K)，其中N是总项目数，K是top_n
 * 
 * @param items 待排序的推荐项列表
 * @param top_n 返回的推荐数量
 * @param comparator 比较函数，定义排序规则
 * @return Top-N推荐结果，按比较器规则排序
 */
std::vector<RecommendationItem> heapSortTopN(
    const std::vector<RecommendationItem>& items, 
    int top_n,
    std::function<bool(const RecommendationItem&, const RecommendationItem&)> comparator);

/**
 * @brief 使用快速选择算法获取Top-N热门推荐
 * 
 * 基于景点热度和评分，使用快速选择算法返回当前热门景点推荐。
 * 时间复杂度：平均O(N)，最坏O(N^2)
 * 
 * @param items 推荐项列表（会被部分修改）
 * @param top_n 返回的推荐数量
 * @param comparator 比较函数（基于热度或评分）
 * @return Top-N热门推荐，按比较器规则排序
 */
std::vector<RecommendationItem> quickSelectTopN(
    std::vector<RecommendationItem>& items, 
    int top_n,
    std::function<bool(const RecommendationItem&, const RecommendationItem&)> comparator);

/**
 * @brief 基于内容推荐的比较器
 * 
 * 按推荐分数降序排列，用于个性化推荐
 * 
 * @param a 第一个推荐项
 * @param b 第二个推荐项
 * @return 如果a的分数大于b的分数返回true
 */
bool contentBasedComparator(const RecommendationItem& a, const RecommendationItem& b);

/**
 * @brief 基于热度的比较器
 * 
 * 按热度降序排列，用于热门推荐
 * 
 * @param a 第一个推荐项
 * @param b 第二个推荐项
 * @return 如果a的热度大于b的热度返回true
 */
bool popularityComparator(const RecommendationItem& a, const RecommendationItem& b);

/**
 * @brief 基于评分的比较器
 * 
 * 按评分降序排列，用于高质量景点推荐
 * 
 * @param a 第一个推荐项
 * @param b 第二个推荐项
 * @return 如果a的评分大于b的评分返回true
 */
bool ratingComparator(const RecommendationItem& a, const RecommendationItem& b);

} // namespace recommendation