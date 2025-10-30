cmake_minimum_required(VERSION 3.16)
project(personalized_tourism_system LANGUAGES CXX VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找pybind11包
find_package(pybind11 CONFIG REQUIRED)

# 推荐算法核心库
add_library(recommendation_algorithms STATIC
    cpp_core/src/algorithms/sorting.cpp
    cpp_core/src/algorithms/inverted_index.cpp
)

target_include_directories(recommendation_algorithms 
    PUBLIC 
        ${CMAKE_CURRENT_SOURCE_DIR}/cpp_core/src/algorithms
)

# Python绑定模块
pybind11_add_module(recommendation_core
    cpp_core/bindings/recommendation_bindings.cpp
)

target_link_libraries(recommendation_core 
    PRIVATE 
        recommendation_algorithms 
        pybind11::module
)

# 设置Python模块输出目录
set_target_properties(recommendation_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/python_package
    SUFFIX ".so"  # 在Linux上，Windows上会自动使用.pyd
)

# 图算法库（原有的）
add_library(graph STATIC
    src/graph/graph.cpp
)
target_include_directories(graph PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

# 第三方依赖（留空即可，未来需要时再启用）
# find_package(fmt 10 CONFIG REQUIRED)
# target_link_libraries(graph PUBLIC fmt::fmt)

# 测试配置
option(BUILD_TESTS "Build tests" ON)
if (BUILD_TESTS)
    enable_testing()
    
    # 图算法测试
    add_executable(test_graph tests/test_graph.cpp)
    target_include_directories(test_graph PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_link_libraries(test_graph PRIVATE graph)
    add_test(NAME test_graph COMMAND test_graph)
    
    # 推荐算法测试（可选）
    option(BUILD_RECOMMENDATION_TESTS "Build recommendation tests" ON)
    if (BUILD_RECOMMENDATION_TESTS)
        add_executable(test_recommendation cpp_core/tests/test_recommendation.cpp)
        target_include_directories(test_recommendation 
            PRIVATE 
                ${CMAKE_CURRENT_SOURCE_DIR}/cpp_core/src/algorithms
        )
        target_link_libraries(test_recommendation PRIVATE recommendation_algorithms)
        add_test(NAME test_recommendation COMMAND test_recommendation)
    endif()
endif()

# 安装配置
install(TARGETS recommendation_core
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(TARGETS recommendation_algorithms graph
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

# 头文件安装
install(DIRECTORY cpp_core/src/algorithms/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/recommendation
    FILES_MATCHING PATTERN "*.h"
)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.h"
)

# 打包配置
option(ENABLE_PACKAGE_CONFIG "Generate CMake package config files" OFF)
if (ENABLE_PACKAGE_CONFIG)
    include(CMakePackageConfigHelpers)
    
    # 主项目配置
    configure_package_config_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/cmake/personalized_tourism_systemConfig.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/personalized_tourism_systemConfig.cmake
        INSTALL_DESTINATION lib/cmake/personalized_tourism_system
    )
    
    write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/personalized_tourism_systemConfigVersion.cmake
        VERSION ${PROJECT_VERSION}
        COMPATIBILITY SameMajorVersion
    )
    
    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/personalized_tourism_systemConfig.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/personalized_tourism_systemConfigVersion.cmake
        DESTINATION lib/cmake/personalized_tourism_system
    )
    
    # 导出目标
    install(EXPORT personalized_tourism_systemTargets
        FILE personalized_tourism_systemTargets.cmake
        DESTINATION lib/cmake/personalized_tourism_system
    )
endif()