
// 1st party
#include "run.hpp"
#include "aoc_utils.hpp"

// Standard library
// #include <algorithm> // provides fold_left
#include <numeric>
#include <ranges>
#include <regex>
#include <string>
#include <string_view>

namespace {
// Aliases
namespace aoc    = aoc_utils;
namespace ranges = std::ranges;
namespace views  = std::views;

using InputType = std::string;

////////////////////////////////////////////////////////////////////////////////
// Part 1
inline auto cregex_matches(std::string_view text, const std::regex& re) {
    return ranges::subrange(
        std::cregex_iterator(text.cbegin(), text.cend(), re),
        std::cregex_iterator()
    );
}


int64_t part1(const std::string_view text) {
    const std::regex re(R"(mul\((\d+),(\d+)\))");

    // Option 1: Functional (Views)
    return aoc::sum(
        cregex_matches(text, re) | views::transform(
            [](const auto& match) {
                return std::stoi(match[1]) * std::stoi(match[2]);
            }
        )
    );

    // Option 2: Functional (Algorithms)
    // return std::transform_reduce(
    //     /* first     = */ std::cregex_iterator(text.cbegin(), text.cend(), re),
    //     /* last      = */ std::cregex_iterator(),
    //     /* init      = */ int64_t{0},
    //     /* reduce    = */ std::plus{},
    //     /* transform = */ [](const auto& match) {
    //         return std::stoi(match[1]) * std::stoi(match[2]);
    //     }
    // );
 
    // Option 3: Procedural
    // std::cregex_iterator it(text.cbegin(), text.cend(), re);
    // int64_t total = 0;
    // for (; it != std::cregex_iterator(); ++it) {
    //     const auto& match = *it;
    //     total += std::stoi(match[1]) * std::stoi(match[2]);
    // }
    // return total;

}

////////////////////////////////////////////////////////////////////////////////
// Part 2
int64_t part2(const std::string_view text) {
    std::regex re(
        "(?:"
             R"(mul\((\d{1,3}),(\d{1,3})\))"
             R"(|(do\(\)))"
             R"(|(don't\(\)))"
        ")"
    );
    return std::transform_reduce(
        /* first     = */ std::cregex_iterator(text.cbegin(), text.cend(), re),
        /* last      = */ std::cregex_iterator(),
        /* init      = */ int64_t{0},
        /* reduce    = */ std::plus{},
        /* transform = */ [is_enabled = true](const auto& match) mutable {
            const bool enable  = match[3].matched;
            const bool disable = match[4].matched;
            if (enable) {
                is_enabled = true;
            } else if (disable) {
                is_enabled = false;
            } else if (is_enabled) {
                return std::stoi(match[1]) * std::stoi(match[2]);
            }
            return 0;
        }
    );
}

}
////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    const aoc::InputPathArgs args = aoc::parse_args(argc, argv);
    aoc::run<InputType>(args.input_path, aoc::read_text, part1, part2);
}

