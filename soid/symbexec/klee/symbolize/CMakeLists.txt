cmake_minimum_required(VERSION 3.13.4)
project(soid)

set(LT_LLVM_INSTALL_DIR "" CACHE PATH "LLVM installation directory")

list(APPEND CMAKE_PREFIX_PATH "${LT_LLVM_INSTALL_DIR}/lib/cmake/llvm/")

find_package(LLVM REQUIRED CONFIG)

include_directories(SYSTEM ${LLVM_INCLUDE_DIRS})

include_directories("../../tomlplusplus/include/")

set(CMAKE_CXX_STANDARD 17 CACHE STRING "")

set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT LLVM_ENABLE_RTTI)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()

add_library(Symbolize SHARED Symbolize.cpp)

target_link_libraries(Symbolize "$<$<PLATFORM_ID:Darwin>:-undefined dynamic_lookup>")
