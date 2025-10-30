/**
 * @file inverted_index.h
 * @brief 倒排索引算法头文件 - 用于关键词搜索推荐
 * @author 甘和君
 * @date 第6周
 */

#pragma once

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>

namespace recommendation {

/**
 * @brief 景点数据结构
 */
struct Attraction {
    int id;                         ///< 景点ID
    std::string name;               ///< 景点名称
    std::string type;               ///< 景点类型
    std::string description;        ///< 景点描述
    
    /**
     * @brief 默认构造函数
     */
    Attraction() : id(0) {}
};

/**
 * @brief 倒排列表项
 */
struct Posting {
    int doc_id;                     ///< 文档ID（景点ID）
    std::string field;              ///< 匹配字段（name/category/description）
    double tf;                      ///< 词频
    std::string display_name;       ///< 显示名称
    
    /**
     * @brief 构造函数
     */
    Posting(int id, const std::string& f, double term_freq, const std::string& name)
        : doc_id(id), field(f), tf(term_freq), display_name(name) {}
};

/**
 * @brief 搜索结果数据结构
 */
struct SearchResult {
    int attraction_id;              ///< 景点ID
    std::string name;               ///< 景点名称
    std::string type;               ///< 景点类型
    double relevance_score;         ///< 相关度分数（0.0-1.0）
    std::string match_field;        ///< 匹配字段
    std::string highlight;          ///< 高亮文本
    
    /**
     * @brief 默认构造函数
     */
    SearchResult() 
        : attraction_id(0), 
          relevance_score(0.0) {}
};

/**
 * @brief 倒排索引类
 * 
 * 基于倒排索引算法，支持对景点名称、类别、关键字的快速搜索，
 * 并对搜索结果按相关度排序。
 */
class InvertedIndex {
private:
    /// @brief 倒排索引：词 -> 倒排列表
    std::unordered_map<std::string, std::vector<Posting>> inverted_index_;
    
    /// @brief 停用词集合
    std::unordered_set<std::string> stop_words_;
    
    /**
     * @brief 初始化停用词表
     */
    void initializeStopWords();
    
    /**
     * @brief 检查是否为停用词
     * @param token 待检查的词
     * @return 如果是停用词返回true
     */
    bool isStopWord(const std::string& token);
    
    /**
     * @brief 令牌标准化处理
     * @param token 原始令牌
     * @return 标准化后的令牌
     */
    std::string normalizeToken(const std::string& token);
    
    /**
     * @brief 计算词频
     * @param token 目标词
     * @param tokens 文档中的所有词
     * @return 词频值
     */
    double calculateTF(const std::string& token, const std::vector<std::string>& tokens);
    
    /**
     * @brief 计算相关度分数
     * @param posting 倒排列表项
     * @param query_length 查询词长度
     * @return 相关度分数
     */
    double calculateRelevanceScore(const Posting& posting, int query_length);
    
    /**
     * @brief 生成高亮文本
     * @param query 搜索查询
     * @param doc_id 文档ID
     * @return 高亮文本
     */
    std::string generateHighlight(const std::string& query, int doc_id);
    
    /**
     * @brief 文本索引处理
     * @param text 待索引文本
     * @param doc_id 文档ID
     * @param field 字段名
     * @param display_name 显示名称
     */
    void indexText(const std::string& text, int doc_id, 
                  const std::string& field, const std::string& display_name);
    
    /**
     * @brief 获取景点名称
     * @param doc_id 文档ID
     * @return 景点名称
     */
    std::string getAttractionName(int doc_id);
    
    /**
     * @brief 获取景点类型
     * @param doc_id 文档ID
     * @return 景点类型
     */
    std::string getAttractionType(int doc_id);

public:
    /**
     * @brief 默认构造函数
     */
    InvertedIndex();
    
    /**
     * @brief 添加景点到倒排索引
     * 
     * 将景点的名称、类别和描述等信息添加到倒排索引中
     * 
     * @param attraction 景点信息
     */
    void addAttraction(const Attraction& attraction);
    
    /**
     * @brief 搜索景点
     * 
     * 基于倒排索引算法，支持对景点名称、类别、关键字的快速搜索，
     * 并对搜索结果按相关度排序。
     * 
     * @param query 搜索关键词
     * @param search_type 搜索类型："name"(名称) / "category"(类别) / "all"(全部)
     * @param limit 最大返回结果数
     * @return 搜索结果列表，按相关度降序排列
     */
    std::vector<SearchResult> search(const std::string& query, 
                                   const std::string& search_type = "all", 
                                   int limit = 20);
    
    /**
     * @brief 文本分词
     * 
     * 将文本分割成令牌序列
     * 
     * @param text 待分词文本
     * @return 分词结果
     */
    std::vector<std::string> tokenize(const std::string& text);
};

} // namespace recommendation