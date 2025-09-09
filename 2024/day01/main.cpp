////////////////////////////////////////////////////////////////////////////////
// Day 01: Historian Hysteria
////////////////////////////////////////////////////////////////////////////////

// 1st party
#include "run.hpp"
#include "aoc_utils.hpp"

// Standard library
#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <numeric>
#include <ranges>
#include <vector>

namespace {
// Aliases
namespace aoc    = aoc_utils;
namespace fs     = std::filesystem;
namespace ranges = std::ranges;
namespace views  = std::views;

////////////////////////////////////////////////////////////////////////////////
// Declarations
struct InputType {
    std::vector<int32_t> left;
    std::vector<int32_t> right;
};

auto read_data(const fs::path &filepath) -> InputType {
    std::ifstream file(filepath);
    if (!file) {
        throw aoc::FileReadException(filepath);
    };

    std::vector<int> left, right;

    std::string line;
    int line_num = -1;
    while (std::getline(file, line)) {
        line_num++;
        std::istringstream iss(line);
        int val1{}, val2{};
        if (!(iss >> val1 >> val2)) {
            throw aoc::FileParseException(line, line_num);
        }
        left.push_back(val1);
        right.push_back(val2);
    }

    return {left, right};
}

template<ranges::view R>
constexpr auto sum(R&& view) {
    using T = ranges::range_value_t<R>;
    return ranges::fold_left(view, T{}, std::plus<>{});
}

auto compute_total_diff(InputType& input) -> int64_t {
    auto& [left, right] = input;

    ranges::sort(left);
    ranges::sort(right);

    // Option 1: Procedural
    // int total_diff = 0;
    // for (size_t i = 0; i < left.size(); i++) {
    //     total_diff += abs(left[i] - right[i]);
    // }
    // return total_diff;

    // Option 2: Functional
    constexpr auto diff  = [](int a, int b) {return std::abs(a - b);};
    return std::transform_reduce(
        /* first1    = */ left.cbegin(),
        /* last1     = */ left.cend(),
        /* first2    = */ right.cbegin(),
        /* init      = */ 0,
        /* reduce    = */ std::plus<>(),
        /* transform = */ diff
    );

    // Option 3: Functional with Ranges/Views
    // return sum(views::zip_transform(diff, left, right));

}

auto compute_score(const InputType& input) -> int64_t {
    const auto& [left, right] = input;

    const aoc::Counter<int> cnt(right);

    // Option 1: Procedural
    // int64_t score = 0;
    // for (const int32_t x : left) {
    //     score += x * cnt[x];
    // }
    // return score;

    // Option 2: Functional
    return sum(left | views::transform([&cnt](int32_t x) { return x * cnt[x];}));

}

}

////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    const aoc::InputPathArgs args = aoc::parse_args(argc, argv);
    aoc::run<InputType>(
        args.input_path,
        read_data,
        /* part1 = */ compute_total_diff,
        /* part2 = */ compute_score
    );
    // aoc::benchmark<InputType>(
    //     args.input_path,
    //     read_data,
    //     /* part1 = */ compute_total_diff,
    //     /* part2 = */ compute_score
    // );
}
