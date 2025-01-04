#!/usr/bin/env bash

main_src="$1"
if [ ! -f "$main_src" ]; then
    echo "ERROR :: File not found: $main_src"
    exit 0
fi
target_exe="./build/${main_src%%.cpp}"
exe_args="${@:2}"

################################################################################
# Clean up build files from previous compilation
if [ -d build ]; then rm -r build; fi 
mkdir build

################################################################################
# echo "Compiling..."
ops=''
ops="$ops -Wall"
ops="$ops -Wextra"
ops="$ops -Wpedantic"
# ops="$ops -Werror"
ops="$ops -Wno-unused-comparison"
ops="$ops -Wno-unused-value"
ops="$ops -Wno-unused-variable"
ops="$ops -std=c++20"
ops="$ops -stdlib=libc++"
ops="$ops -g"
ops="$ops -I$AOC_PATH/aoc_utils/cpp $AOC_PATH/aoc_utils/cpp/aoc_utils.cpp"
ops="$ops -o $target_exe"
clang++ $ops "$main_src"

if [ $? -eq 0 ]; then
    # printf "====== RUNNING ======\n"
    chmod +x "$target_exe"
    $target_exe $exe_args
    # printf "\n====== DONE ======\n"
else
    printf "\n====== FAILED ======\n"
fi
