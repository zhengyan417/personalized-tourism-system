# personalized-tourism-system
We want to achieve a personalized tourism system , which could help specific person to manage their tourism activity. 

## Prerequisites
- CMake >= 3.16
- C++17 编译器
  - Windows: Visual Studio 2022 (MSVC) 或 MSYS2/MinGW-w64
  - Linux/macOS: Clang/GCC 10+
- 可选：Ninja（更快）

## Build C++ core (graph)
- MinGW:
```powershell
cmake -S cpp_core -B build\cpp_core -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DBUILD_GRAPH_TESTS=ON
cmake --build build\cpp_core -j
ctest --test-dir build\cpp_core --output-on-failure
```
- Visual Studio:
```powershell
cmake -S cpp_core -B build\cpp_core -G "Visual Studio 17 2022" -A x64 -DBUILD_GRAPH_TESTS=ON
cmake --build build\cpp_core --config Release
ctest --test-dir build\cpp_core -C Release --output-on-failure
```

## Use graph in other targets
在顶层 CMakeLists.txt:
```cmake
add_subdirectory(cpp_core)
add_executable(app app/main.cpp)
target_include_directories(app PRIVATE ${CMAKE_SOURCE_DIR}/cpp_core/include)
target_link_libraries(app PRIVATE graph)
```

## Docs
- 路径规划 API: docs/api/route_planning.md