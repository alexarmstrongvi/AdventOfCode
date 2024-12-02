// 1st party
#include "aoc_utils.hpp"

// Standard library
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sstream>
#include <utility>
#include <vector>

// Aliases
namespace fs = std::filesystem;
namespace aoc = aoc_utils;

////////////////////////////////////////////////////////////////////////////////
// Declarations
std::pair<std::vector<int>, std::vector<int>> read_data(const fs::path &filepath);

////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    // Get input
    const aoc::InputPathArgs args = aoc::parse_args(argc, argv);
    if (args.help) {
        std::cerr << args.help_msg << std::endl;
        return 1;
    }

    if (args.verbose) {
        std::cout << "INFO | Reading file " << args.input_path << '\n';
    }

    auto [left, right] = read_data(args.input_path);

    ////////////////////////////////////////
    // Solution
    ////////////////////////////////////////
    sort(left.begin(), left.end());
    sort(right.begin(), right.end());

    // Option 1: Procedural
    // int total_diff = 0;
    // for (size_t i = 0; i < left.size(); i++) {
    //     total_diff += abs(left[i] - right[i]);
    // }

    // Option 2: Functional
    auto last = args.max_lines ? left.cbegin() + args.max_lines.value() : left.cend();
    int total_diff = std::transform_reduce(
        /* first1    = */ left.cbegin(),
        /* last1     = */ last,
        /* first2    = */ right.cbegin(),
        /* init      = */ 0,
        /* reduce    = */ std::plus<>(),
        /* transform = */ [](int a, int b) { return std::abs(a - b); }
    );

    std::cout << "Part 1: " << total_diff << std::endl;

    const aoc::Counter cnt(right);

    // Option 1: Procedural
    // int score = 0;
    // for (const int id : left) {
    //     score += id * cnt[id];
    // }

    // Option 2: Functional
    int score = std::accumulate(
        left.cbegin(),
        left.cend(),
        0,
        [&cnt](int sum, const int x) { return sum + x * cnt[x]; }
    );
    std::cout << "Part 2: " << score << std::endl;
}

////////////////////////////////////////////////////////////////////////////////
// Supporting functions
std::pair<std::vector<int>, std::vector<int>> read_data(const fs::path &filepath) {
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

        // std::string remainder;
        // if (iss >> remainder) {
        //     throw aoc::FileParseException("Extra data: " + line, line_num);
        // }

        left.push_back(val1);
        right.push_back(val2);
    }

    return {left, right};
}
