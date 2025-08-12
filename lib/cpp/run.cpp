#include "run.hpp"

#include <array>
#include <iostream>
#include <algorithm>
#include <fstream>
#include <string>
#include <print>
#include <regex>

namespace aoc_utils {

auto find_solution_path(
    std::filesystem::path path
) -> std::optional<std::filesystem::path> {
    namespace fs = std::filesystem;

    const std::string filename = path.filename().string();
    std::optional<fs::path> solution_path;
    if (filename == "input.txt") {
        solution_path = path.parent_path() / fs::path{"solution.txt"};
    } else if (filename == "example_input.txt") {
        solution_path = path.parent_path() / fs::path{"example_solution.txt"};
    }
    if (solution_path.has_value() && !fs::exists(solution_path.value())) {
        solution_path.reset();
    }
    return solution_path;
}

constexpr auto to_microsec(Clock::duration duration) -> double {
    return static_cast<std::chrono::duration<double, std::micro>>(duration).count();
}

auto median(std::vector<Clock::duration>& data) -> Clock::duration {
    if (data.size() < 1) {
        throw std::domain_error("Cannot compute MAD of vector with <2 elements");
    }
    auto mid = data.begin() + static_cast<std::ptrdiff_t>(data.size()/2);
    std::nth_element(data.begin(), mid, data.end());
    return data[data.size()/2];
}

auto median_absolute_deviation(
    std::vector<Clock::duration>& data,
    Clock::duration med
) -> Clock::duration {
    if (data.empty()) {
        throw std::domain_error("Cannot compute MAD of empty vector");
    }

    std::vector<Clock::duration> deviations;
    deviations.reserve(data.size());
    for (auto x : data) {
        deviations.push_back(std::chrono::abs(x - med));
    }

    return median(deviations);
}

////////////////////////////////////////////////////////////////////////////////
auto read_solutions(
    const std::filesystem::path& filepath
) -> std::pair<Solution, Solution> {
    std::ifstream file(filepath);
    if (!file) {
        throw aoc_utils::FileReadException(filepath);
    };

    std::string line;
    std::regex pattern(R"(Part \d: (\d+) \[(\d+\.\d+)ms\])");
    std::smatch match;

    std::array<Solution,2> solutions;
    int count = 0;

    while (std::getline(file, line) && count < std::ssize(solutions)) {
        if (!std::regex_search(line, match, pattern)) {
            throw FileParseException(line);
        }
        int answer = std::stoi(match[1].str());
        double milliseconds = std::stod(match[2].str());
        auto nanosec = std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::duration<double, std::milli>(milliseconds)
        );

        solutions[aoc_utils::uz(count++)] = Solution{answer, nanosec};
    }

     return {solutions[0], solutions[1]};
}

namespace ansi {
    constexpr std::string
        red   = "\033[1;91m",
        green = "\033[1;92m",
        reset = "\033[0m";
}

void print_result(
    std::string_view part,
    SolutionType answer,
    std::chrono::nanoseconds elapsed,
    std::optional<Solution> solution
) {
    std::cout << std::format(
        "{}: {} [{:.1f} us]", 
        part, answer, to_microsec(elapsed)
    );
    if (solution.has_value()) {
        const auto& sol = solution.value();
        if (answer != sol.answer) {
            std::cout << "[" << ansi::red << "Wrong! " << ansi::reset;
        } else {
            std::cout << "[" << ansi::green << "Correct!" << ansi::reset;
        }
        const auto diff = static_cast<double>((sol.time - elapsed).count());
        const auto p_diff = (diff / static_cast<double>(sol.time.count())) * 100;
        if (p_diff > 10.0) {
            std::cout << ansi::green << std::format(" {:.1f}% Faster", p_diff) << ansi::reset;
        } else if (p_diff < -5.0) {
            std::cout << ansi::red << std::format(" {:.1f}% Slower", p_diff) << ansi::reset;
        }
        std::cout << std::format(
            ", baseline: {:.1f}us]", //, diff={}ns]",
            to_microsec(solution.value().time)
            // (sol.time- elapsed).count()
        );
    }
    std::cout << std::endl;
}

void print_benchmark_stats(std::vector<Clock::duration>& timings) {
    auto mid = timings.begin() + static_cast<std::ptrdiff_t>(timings.size()/2);
    std::nth_element(timings.begin(), mid, timings.end());
    const auto median = timings[timings.size()/2];
    const auto mad = median_absolute_deviation(timings, median);
    const auto [it_min, it_max] = std::ranges::minmax_element(timings);
    std::println(
        "median = {:.1f} +/- {:.1f}; range=[{:.1f} to {:.1f}]; N={}", 
        to_microsec(median),
        to_microsec(mad),
        to_microsec(*it_min),
        to_microsec(*it_max),
        timings.size()
    );
}

}
