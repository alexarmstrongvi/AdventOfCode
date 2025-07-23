add_library(aoc_utils STATIC aoc_utils.cpp run.cpp)
target_include_directories(aoc_utils PUBLIC .)
target_link_libraries(aoc_utils PRIVATE myproject_warnings myproject_options)
