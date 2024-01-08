#!/usr/bin/env bash

main_src="$1"
if [ ! -f "$main_src" ]; then
    echo "ERROR :: File not found: $main_src"
    exit 0
fi
target_exe="${main_src%%.c}"
exe_args="${@:2}"

make -f ${AOC_PATH}/Makefile target_exe=${target_exe} main_src=${main_src}

if [ $? -eq 0 ]; then
    printf "Running ./build/${target_exe}\n"
    printf "====== stdout/stderr ======\n"
    chmod +x "./build/${target_exe}"
    ./build/${target_exe} ${exe_args}
else
    printf "\n====== FAILED ======\n"
fi
