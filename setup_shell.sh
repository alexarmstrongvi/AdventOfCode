export AOC_PATH="$(dirname $(realpath $0))"
echo "AOC_Path = $AOC_PATH"
alias C="$AOC_PATH/lib/c/build_and_run_c.sh"
alias Cpp="$AOC_PATH/lib/cpp/runcpp"
alias haskell="$AOC_PATH/lib/haskell/runhaskell"
alias rust="$AOC_PATH/lib/rust/runrust"
# export MallocStackLogging=1
# unset MallocStackLogging

