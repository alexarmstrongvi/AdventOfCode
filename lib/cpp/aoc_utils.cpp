////////////////////////////////////////////////////////////////////////////////
// Utilities for Advent of Code C++ solutions
////////////////////////////////////////////////////////////////////////////////

// Questions:
// Does C++ have something like a csv-reader to handle common read cases
// printing collections
// Logging levels
// Benchmarking
// Suggestions to speed it up

// 1st party
#include "aoc_utils.hpp"

// Standard library
#include <filesystem>
#include <vector>

// Aliases
namespace fs = std::filesystem;

////////////////////////////////////////////////////////////////////////////////
namespace aoc_utils {
////////////////////////////////////////////////////////////////////////////////

InputPathArgs parse_args(int argc, char *argv[]) {
    InputPathArgs options;
    std::vector<std::string> args(argv + 1, argv + argc);

    // Check if help requested
    auto help_it = std::find_if(args.cbegin(), args.cend(), [](const std::string &s) {
        return s == "-h" || s == "--help";
    });
    if (help_it != args.cend()) {
        options.help = true;
        return options;
    }

    // Parse keyword arguments
    for (auto it = args.begin(); it != args.end();) {
        if (*it == "-v" || *it == "--verbose") {
            options.verbose = true;
            it = args.erase(it);
        } else if (*it == "-n" || *it == "--max-lines") {
            it++;
            if (it == args.end() || (*it).starts_with('-')) {
                throw ArgvParseException("--max-lines requires a parameter");
            }
            try {
                options.max_lines = std::stoi(*it);
            } catch (const std::exception &) {
                throw ArgvParseException("Failed to parse --max-lines parameter: " + *it);
            }
            it = args.erase(args.begin() + (it - args.begin() - 1), it + 1);
        } else if ((*it).starts_with('-')) {
            throw ExtraArgsException("Unexpected keyword argument: '" + (*it) + "'");
        } else {
            ++it;
        }
    }

    // Parse positional arguments
    if (args.size() == 0) {
        throw MissingArgsException("No filename provided");
    } else if (args.size() > 1) {
        throw ExtraArgsException("Extra arguments provided");
    }
    options.input_path = fs::path{args[0]};

    // Checks
    if (!fs::exists(options.input_path)) {
        throw FileNotFoundException(options.input_path);
    }

    return options;
}

////////////////////////////////////////////////////////////////////////////////
// end AoC_Utils
} 
