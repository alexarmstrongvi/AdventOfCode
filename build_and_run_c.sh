#!/usr/bin/env bash
# Poor man's make

################################################################################
# Clean up build files from previous compilation
if [ -d build ]; then rm -r build; fi 
mkdir build

################################################################################
file="$1"
if [ ! -f "$file" ]; then
    echo "ERROR :: File not found: $file"
    exit 0
fi
stem="${file%%.c}"
exe="${stem}"
echo "Compiling ${file} to build/"
ops=''
ops="$ops -Wall"
ops="$ops -Wextra"
ops="$ops -Wpedantic"
ops="$ops -Werror"
ops="$ops -Wno-unused-comparison"
ops="$ops -Wno-unused-value"
ops="$ops -Wno-unused-variable"
ops="$ops -std=c17"
ops="$ops -g" # generate debug info
ops="$ops -I ${AOC_PATH}/include"
ops="$ops -o build/${exe}"
# ops="$ops -Ofast"
clang $ops "${AOC_PATH}"/utils/*.c "$file" 
exe_args="${@:2}"

if [ $? -eq 0 ]; then
    printf "Running ./build/${exe}\n"
    printf "====== stdout/stderr ======\n"
    chmod +x "./build/${exe}"
    ./build/${exe} ${exe_args}
else
    printf "\n====== FAILED ======\n"
fi
