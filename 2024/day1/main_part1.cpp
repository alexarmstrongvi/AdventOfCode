// Are there python/cpp tools to sort inputs
// What neovim tools are there for navigating C/C++ code?
//  - Knowing what objects are being used from which headers?
//  - Knowing which header an object is included from?
// Are there better exceptions to raise than runtime errors?
// Does C++ have something like a csv-reader to handle common read cases
// Debug mode and breakpoints
// printing collections
// Logging levels
// Benchmarking

#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <ranges>
namespace fs = std::filesystem;

////////////////////////////////////////////////////////////////////////////////
std::pair<std::vector<int>, std::vector<int>> read_data(fs::path filepath);

////////////////////////////////////////////////////////////////////////////////
int main(int argc, char* argv[]) {
    // Checks
    if (argc == 1) {
        throw std::runtime_error("Error: No filename provided");
    } else if (argc > 2) {
        throw std::runtime_error("Error: Too many arguments");
    }
    fs::path filepath{argv[1]};
    if (!fs::exists(filepath)) {
        throw std::runtime_error("Error: File does not exist " + filepath.string());
    }

    std::cout << "Info: Reading file " << filepath << '\n';

    auto [left, right] = read_data(filepath);
    sort(left.begin(), left.end());
    sort(right.begin(), right.end());

    std::cout << "Info: Vectors " << left.size() << ", " << left[0] << '\n';
    std::cout << "Info: Vectors " << right.size() << ", " << right[0] << '\n';


    // Option 1: Procedural
    // int total_diff = 0;
    // for (size_t i = 0; i < left.size(); i++) {
    //     total_diff += abs(left[i] - right[i]);
    // }

    // Option 2: Functional
    int total_diff = std::transform_reduce(
        left.begin(), left.end(),
        right.begin(),
        0,
        std::plus<>(),
        [](int a, int b) { return std::abs(a - b); }
    );

    std::cout << total_diff << std::endl;
}

////////////////////////////////////////////////////////////////////////////////
std::pair<std::vector<int>, std::vector<int>> read_data(fs::path filepath) {
    std::ifstream file(filepath);
    if (!file) {
        throw std::runtime_error("Could not open file: " + filepath.string());
    };

    std::vector<int> left, right;

    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        int val1, val2;
        if (!(iss >> val1 >> val2)) {
            throw std::runtime_error("Invalid line format: " + line);
        }
        left.push_back(val1);
        right.push_back(val2);
    }

    return {left, right};
}
