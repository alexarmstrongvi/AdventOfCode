#pragma once
// 1st party
#include "aoc_utils.hpp"

// Standard library
#include <cstdint>
#include <chrono>
#include <filesystem>
#include <functional>
#include <optional>
#include <print>
#include <tuple> // std::tie
#include <utility> // for std::pair

namespace aoc_utils {

using Clock = std::chrono::high_resolution_clock;
using SolutionType = int64_t;

struct Solution {
    SolutionType answer;
    std::chrono::nanoseconds time;
};

auto find_solution_path(
    std::filesystem::path path
) -> std::optional<std::filesystem::path>;

auto read_solutions(
    const std::filesystem::path& filepath
) -> std::pair<Solution, Solution>;

void print_result(
    std::string_view part,
    SolutionType answer,
    std::chrono::nanoseconds elapsed,
    std::optional<Solution> solution
);

void print_benchmark_stats(std::vector<Clock::duration>& timings);

auto median(std::vector<Clock::duration>& data) -> Clock::duration;

template<typename F>
auto benchmark_part(F func) -> std::vector<Clock::duration> {
    static constexpr std::chrono::seconds max_time {1};
    static constexpr int max_iterations = 50;
    static constexpr int warm_up = 5;

    std::vector<Clock::duration> timings;
    timings.reserve(max_iterations);

    auto start_benchmark = Clock::now();

    for (int i = 0; i < warm_up + max_iterations; ++i) {
        auto start = Clock::now();
        func();
        auto elapsed = Clock::now() - start;
        auto elapsed_benchmark = Clock::now() - start_benchmark;
        if (elapsed_benchmark > max_time) {
            timings.push_back(elapsed);
            break;
        }
        if (i >= warm_up) {
            timings.push_back(elapsed);
        }
    }

    return timings;
}

////////////////////////////////////////////////////////////////////////////////

template<
    typename InputType, 
    typename F0, 
    typename F1, 
    typename F2
>
void run(
    const std::filesystem::path &filepath,
    F0 read_input,
    F1 part1_func,
    F2 part2_func
) {
    auto solution_path = find_solution_path(filepath);
    std::optional<Solution> solution1, solution2;
    if (solution_path) {
        std::tie(solution1, solution2) = read_solutions(solution_path.value());
    }
    Clock::time_point start {};

    InputType input = read_input(filepath);

    auto start_run = Clock::now();
    // Part 1
    start = Clock::now();
    const SolutionType answer1 = part1_func(input);
    auto elapsed1 = Clock::now() - start;
    if (solution1.has_value() && answer1 != solution1->answer) {
        print_result("Part 1", answer1, elapsed1, solution1);
        return;
    }

    // Part 2
    start = Clock::now();
    const SolutionType answer2 = part2_func(input);
    auto elapsed2 = Clock::now() - start;
    if (solution2.has_value() && answer2 != solution2->answer) {
        print_result("Part 2", answer2, elapsed2, solution2);
        return;
    }

    auto elapsed_run = Clock::now() - start_run;
    const bool run_benchmark = (
        elapsed_run < std::chrono::seconds{1}
        && solution1.has_value() 
        && solution2.has_value() 
    );
    if (run_benchmark) {
        auto timings1 = benchmark_part([&](){
            // Declare volatile to limit optimizations
            [[maybe_unused]]
            volatile auto result = part1_func(input);
        });
        std::print("Part 1: ");
        // std::println("Part 1 benchmark stats");
        print_benchmark_stats(timings1);
        elapsed1 = median(timings1);
        auto timings2 = benchmark_part([&](){
            // Declare volatile to limit optimizations
            [[maybe_unused]]
            volatile auto result = part2_func(input);
        });
        std::print("Part 2: ");
        // std::println("Part 2 benchmark stats");
        print_benchmark_stats(timings2);
        elapsed2 = median(timings2);
    }
    print_result("Part 1", answer1, elapsed1, solution1);
    print_result("Part 2", answer2, elapsed2, solution2);

}

template<typename InputType, typename Func1, typename Func2>
void benchmark(
    const std::filesystem::path &filepath,
    std::function<InputType(const std::filesystem::path &filepath)> read_input,
    Func1 part1_func,
    Func2 part2_func
) {
    InputType input = read_input(filepath);

    auto timings1 = benchmark_part([&](){
        // Declare volatile to limit optimizations
        [[maybe_unused]]
        volatile auto result = part1_func(input);
    });
    std::print("Part 1");
    print_benchmark_stats(timings1);

    auto timings2 = benchmark_part([&](){
        // Declare volatile to limit optimizations
        [[maybe_unused]]
        volatile auto result = part2_func(input);
    });
    std::print("Part 1");
    // std::println("Part 2 benchmark stats");
    print_benchmark_stats(timings2);
}

} // namespace aoc_utils
