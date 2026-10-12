cmake_minimum_required(VERSION 3.10)
project(go2w_dds_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(unitree_sdk2 2.0.0 EXACT CONFIG REQUIRED)
add_executable(go2w_dds_probe main.cpp)
target_link_libraries(go2w_dds_probe PRIVATE unitree_sdk2)
