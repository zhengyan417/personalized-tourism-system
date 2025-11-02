#include "../../include/algorithms/inverted_index.h"
#include <algorithm>
#include <sstream>
#include <locale>
#include <cctype>
#include <iostream>

namespace recommendation {

/**
 * @brief 构造函数
 */
InvertedIndex::InvertedIndex() {
    // 初始化停用词
    initializeStopWords();
}

/**
 * @brief 添加景点到索引
 * @param attraction 景点信息
 */
void InvertedIndex::addAttraction(const Attraction& attraction) {
    int doc_id = attraction.id;
    
    // 索引名称字段
    indexText(attraction.name, doc_id, "name", attraction.name);
    
    // 索引类别字段
    indexText(attraction.type, doc_id, "category", attraction.type);
    
    // 索引描述字段（如果有）
    if (!attraction.description.empty()) {
        indexText(attraction.description, doc_id, "description", attraction.name);
    }
}

/**
 * @brief 文本索引处理
 */
void InvertedIndex::indexText(const std::string& text, int doc_id, 
                             const std::string& field, const std::string& display_name) {
    std::vector<std::string> tokens = tokenize(text);
    
    for (const auto& token : tokens) {
        if (isStopWord(token)) {
            continue;
        }
        
        std::string normalized_token = normalizeToken(token);
        
        // 添加到倒排索引
        inverted_index_[normalized_token].emplace_back(
            doc_id, field, calculateTF(token, tokens), display_name
        );
    }
}

/**
 * @brief 搜索处理
 * @param query 搜索查询
 * @param search_type 搜索类型
 * @param limit 最大返回结果数
 * @return 搜索结果
 */
std::vector<SearchResult> InvertedIndex::search(
    const std::string& query, 
    const std::string& search_type, 
    int limit) {
    
    std::vector<std::string> query_tokens = tokenize(query);
    std::unordered_map<int, SearchResult> doc_scores;
    
    for (const auto& token : query_tokens) {
        if (isStopWord(token)) {
            continue;
        }
        
        std::string normalized_token = normalizeToken(token);
        auto it = inverted_index_.find(normalized_token);
        
        if (it != inverted_index_.end()) {
            for (const auto& posting : it->second) {
                // 根据搜索类型过滤
                if (search_type != "all" && posting.field != search_type) {
                    continue;
                }
                
                // 计算相关度分数
                double relevance_score = calculateRelevanceScore(posting, query_tokens.size());
                
                if (doc_scores.find(posting.doc_id) == doc_scores.end()) {
                    // 创建 SearchResult 对象并逐个赋值
                    SearchResult result;
                    result.attraction_id = posting.doc_id;  // 修改为 attraction_id
                    result.name = getAttractionName(posting.doc_id);
                    result.type = getAttractionType(posting.doc_id);
                    result.relevance_score = relevance_score;
                    result.match_field = posting.field;      // 修改为 match_field
                    result.highlight = generateHighlight(query, posting.doc_id);
                    
                    doc_scores[posting.doc_id] = result;
                } else {
                    // 合并相同文档的分数
                    doc_scores[posting.doc_id].relevance_score += relevance_score;
                }
            }
        }
    }
    
    // 转换为向量并排序
    std::vector<SearchResult> results;
    for (auto& pair : doc_scores) {
        results.push_back(pair.second);
    }
    
    // 按相关度分数降序排序
    std::sort(results.begin(), results.end(), 
              [](const SearchResult& a, const SearchResult& b) {
                  return a.relevance_score > b.relevance_score;
              });
    
    // 限制返回数量
    if (limit > 0 && results.size() > limit) {
        results.resize(limit);
    }
    
    return results;
}

/**
 * @brief 文本分词
 */
std::vector<std::string> InvertedIndex::tokenize(const std::string& text) {
    std::vector<std::string> tokens;
    std::stringstream ss(text);
    std::string token;
    
    while (ss >> token) {
        // 简单的空格分词，实际项目中可以使用更复杂的分词器
        tokens.push_back(token);
    }
    
    return tokens;
}

/**
 * @brief 令牌标准化
 */
std::string InvertedIndex::normalizeToken(const std::string& token) {
    std::string result = token;
    
    // 转换为小写
    std::transform(result.begin(), result.end(), result.begin(), ::tolower);
    
    // 移除标点符号（简单实现）
    result.erase(std::remove_if(result.begin(), result.end(), 
                               [](char c) { return std::ispunct(c); }), 
                result.end());
    
    return result;
}

/**
 * @brief 计算词频
 */
double InvertedIndex::calculateTF(const std::string& token, 
                                 const std::vector<std::string>& tokens) {
    int count = 0;
    std::string normalized_token = normalizeToken(token);
    
    for (const auto& t : tokens) {
        if (normalizeToken(t) == normalized_token) {
            count++;
        }
    }
    return static_cast<double>(count) / tokens.size();
}

/**
 * @brief 计算相关度分数
 */
double InvertedIndex::calculateRelevanceScore(const Posting& posting, int query_length) {
    // 简单的TF评分，实际项目中可以加入IDF等更复杂的计算
    double base_score = posting.tf * 10.0;
    
    // 字段权重调整
    if (posting.field == "name") {
        base_score *= 2.0; // 名称匹配权重更高
    } else if (posting.field == "category") {
        base_score *= 1.5; // 类别匹配权重中等
    }
    
    return base_score;
}

/**
 * @brief 生成高亮文本
 */
std::string InvertedIndex::generateHighlight(const std::string& query, int doc_id) {
    // 简化实现：返回匹配的字段
    // 实际项目中可以实现真正的高亮逻辑
    return query;
}

/**
 * @brief 初始化停用词
 */
void InvertedIndex::initializeStopWords() {
    stop_words_ = {
        "的", "地", "得", "和", "与", "或", "是", "在", "有", "了",
        "the", "a", "an", "and", "or", "is", "in", "on", "at", "to", "for"
    };
}

/**
 * @brief 检查是否为停用词
 */
bool InvertedIndex::isStopWord(const std::string& token) {
    std::string normalized = normalizeToken(token);
    return stop_words_.find(normalized) != stop_words_.end();
}

/**
 * @brief 获取景点名称（模拟实现）
 */
std::string InvertedIndex::getAttractionName(int doc_id) {
    // 实际项目中应该从数据库或缓存中获取
    // 这里返回模拟数据
    return "景点" + std::to_string(doc_id);
}

/**
 * @brief 获取景点类型（模拟实现）
 */
std::string InvertedIndex::getAttractionType(int doc_id) {
    // 实际项目中应该从数据库或缓存中获取
    // 这里返回模拟数据
    return "类型" + std::to_string(doc_id);
}

} // namespace recommendation