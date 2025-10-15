cmake_minimum_required(VERSION 3.16)
project(personalized_tourism_graph LANGUAGES CXX VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(graph STATIC
    src/graph/graph.cpp
    # 模板类头文件实现，以下源文件不参与编译
    # src/graph/vertex.cpp
    # src/graph/edge.cpp
)
target_include_directories(graph PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

# 第三方依赖（留空即可，未来需要时再启用）
# find_package(fmt 10 CONFIG REQUIRED)
# target_link_libraries(graph PUBLIC fmt::fmt)

option(BUILD_GRAPH_TESTS "Build graph tests" ON)
if (BUILD_GRAPH_TESTS)
    enable_testing()
    add_executable(test_graph tests/test_graph.cpp)
    target_include_directories(test_graph PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    target_link_libraries(test_graph PRIVATE graph)
    add_test(NAME test_graph COMMAND test_graph)
endif()

# 打包配置，默认关闭，避免缺失模板文件报错
option(ENABLE_GRAPH_PACKAGE_CONFIG "Generate CMake package config files" OFF)
if (ENABLE_GRAPH_PACKAGE_CONFIG)
    include(CMakePackageConfigHelpers)
    configure_file(${CMAKE_CURRENT_SOURCE_DIR}/cmake/graphConfig.cmake.in
                   ${CMAKE_CURRENT_BINARY_DIR}/graphConfig.cmake @ONLY)
    write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/graphConfigVersion.cmake
        VERSION ${PROJECT_VERSION}
        COMPATIBILITY SameMajorVersion
    )
    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/graphConfig.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/graphConfigVersion.cmake
    DESTINATION lib/cmake/graph)
endif()