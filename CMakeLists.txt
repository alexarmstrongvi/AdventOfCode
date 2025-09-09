cmake_minimum_required(VERSION 4.0)
project(advent_of_code VERSION 0.0.1 LANGUAGES CXX)

if (PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)
    message(FATAL_ERROR "In-source builds not allowed")
endif()

include(cmake/ProjectOptions.cmake)

add_library(myproject_warnings INTERFACE)
# add_library(myproject::warnings ALIAS myproject_warnings)
target_compile_options(myproject_warnings INTERFACE "$<BUILD_INTERFACE:${myproject_WARNINGS}>")

add_library(myproject_options INTERFACE)
target_compile_features(myproject_options INTERFACE cxx_std_23)
target_compile_options(myproject_options INTERFACE "${myproject_COMPILE_OPTIONS}")
target_link_options(myproject_options INTERFACE "${myproject_LINK_OPTIONS}")

add_subdirectory(lib/cpp)

file(
    GLOB_RECURSE AOC_SOURCES
    RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} "*/day*/main.cpp"
)
foreach(src ${AOC_SOURCES})
    get_filename_component(dir ${src} DIRECTORY)
    string(REPLACE "/" "_" exe_name ${dir})

    add_executable(${exe_name} ${src})
    set_target_properties(${exe_name} PROPERTIES
        RUNTIME_OUTPUT_NAME "main"
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${dir}/$<CONFIG>
    )
    target_link_libraries(${exe_name} PRIVATE aoc_utils myproject_warnings myproject_options)
endforeach()
