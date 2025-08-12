
// 1st party
#include "run.hpp"
#include "aoc_utils.hpp"

// Standard library
#include <algorithm>
#include <concepts>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <ranges>
#include <sstream>
#include <vector>

// Aliases
namespace fs     = std::filesystem;
namespace aoc    = aoc_utils;
namespace ranges = std::ranges;
namespace views  = std::views;

////////////////////////////////////////////////////////////////////////////////
// Part 1
constexpr bool is_safe_level(int x, int y, bool is_increasing) {
    const int diff {std::abs(y-x)};
    return 1 <= diff && diff <= 3 && (x<y) == is_increasing;
}

template<ranges::random_access_range R>
bool is_safe_report(const R& nums) {
    return ranges::all_of(
        nums | views::pairwise,
        [is_increasing = nums[0] < nums[1]]
        (const auto pair){
            const auto [x, y] = pair;
            return is_safe_level(x, y, is_increasing);
        }
    );

    // Option 1: Procedural
    // if (nums.size() <= 1) {
    //     return true;
    // }
    // const bool is_increasing = nums[0] < nums[1];
    // for (size_t i=0; i < nums.size()-1; ++i) {
    //     if (!is_safe_level(nums[i], nums[i+1], is_increasing)) {
    //         return false;
    //     }
    // }

    return true;
}

////////////////////////////////////////////////////////////////////////////////
// Part 2
template<ranges::random_access_range R>
requires std::integral<std::ranges::range_value_t<R>>
bool _is_tolerable_report_increasing(const R& nums) {
    using T       = std::ranges::range_value_t<R>;
    using diff_t  = std::ranges::range_difference_t<R>;
    const auto sz = [](const diff_t i){
        return static_cast<std::ranges::range_size_t<R>>(i);
    };

    auto found_bad_level = false;
    diff_t i = 0;
    const auto begin = std::ranges::begin(nums);
    const auto is_safe = [](const T x, const T y) {return x+1 <= y && y <= x+3;};

    while (sz(i+1) < nums.size()) {
        if (is_safe(begin[i], begin[i+1])) {
            i += 1;
            continue;
        } else if (found_bad_level) {
            return false;
        } else if (sz(i+2) == nums.size()) {
            return true;
        }
        found_bad_level = true;

        // Determine if i or i+1 should be dropped
        if (is_safe(begin[i], begin[i+2])) { // drop i+1
            i += 2;
            continue;
        } else if (i == 0 && is_safe(begin[i+1], begin[i+2])) { // drop i
            i += 2;
            continue;
        } else if ( i != 0 && is_safe(begin[i-1], begin[i+1])) { // drop i
            i += 1;
            continue;
        }
        return false;
    }
    return true;
}

template<ranges::random_access_range R>
bool is_tolerable_report(const R& nums) {
    if (nums.size() <= 1) {
        return true;
    }
    return (
        _is_tolerable_report_increasing(nums)
        ||
        _is_tolerable_report_increasing(nums | views::reverse)
    );
}

////////////////////////////////////////////////////////////////////////////////
using Report = std::vector<int>;
using InputType = std::vector<Report>;
auto read_data(const fs::path &filepath) -> InputType {
    std::ifstream file(filepath);
    if (!file) {
        throw aoc::FileReadException(filepath);
    };

    std::string line;
    int val{0};
    std::vector<std::vector<int>> rows{};

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        std::vector<int> row{};
        while (iss >> val) {
            row.push_back(val);
        }
        rows.push_back(row);
    }

    return rows;
}

////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    const aoc::InputPathArgs args = aoc::parse_args(argc, argv);
    aoc::run<InputType>(
        args.input_path,
        read_data,
        /* part1 = */ [](const InputType& reports){ 
            return ranges::count_if(reports, is_safe_report<Report>);
        },
        /* part2 = */ [](const InputType& reports){ 
            return ranges::count_if(reports, is_tolerable_report<Report>);
        }
    );
}

