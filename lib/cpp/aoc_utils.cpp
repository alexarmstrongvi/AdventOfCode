////////////////////////////////////////////////////////////////////////////////
// Utilities for Advent of Code C++ solutions
////////////////////////////////////////////////////////////////////////////////

// Questions:
// Does C++ have something like a csv-reader to handle common read cases
// Logging levels

// 1st party
#include "aoc_utils.hpp"

// Standard library
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

// Aliases
namespace fs = std::filesystem;

////////////////////////////////////////////////////////////////////////////////
namespace aoc_utils {
////////////////////////////////////////////////////////////////////////////////
MissingArgsException::MissingArgsException(const std::string &msg) 
    : std::runtime_error(msg) {}
ExtraArgsException::ExtraArgsException(const std::string &msg) 
    : std::runtime_error(msg) {}

FileNotFoundException::FileNotFoundException(const std::string &msg) 
    : std::runtime_error(msg) {}
FileNotFoundException::FileNotFoundException(const std::filesystem::path &path)
    : std::runtime_error("File not found: " + path.string()) {}

FileReadException::FileReadException(const std::string &msg) 
    : std::runtime_error(msg) {}
FileReadException::FileReadException(const std::filesystem::path &path)
    : std::runtime_error("Failed to read file: " + path.string()) {}

FileParseException::FileParseException(const std::string &line)
    : std::runtime_error(std::format("Failed to parse line: '{}'", line)) {}
FileParseException::FileParseException(const std::string &line, const int64_t line_num)
    : std::runtime_error(std::format("Failed to parse line {}: '{}'", line_num, line)) {}

ArgvParseException::ArgvParseException(const std::string &msg) : std::runtime_error(msg) {}

InputPathArgs parse_args(int argc, char *argv[]) {
    InputPathArgs options;
    std::vector<std::string> args(argv + 1, argv + argc);

    // Check if help requested
    auto help_it = std::find_if(args.cbegin(), args.cend(), [](const std::string &s) {
        return s == "-h" || s == "--help";
    });
    if (help_it != args.cend()) {
        std::cerr << options.help_msg << std::endl;
        std::exit(1);
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

auto read_text(const fs::path &filepath) -> std::string {
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (!file) {
        throw FileReadException(filepath);
    };

    const int64_t file_ssize { file.tellg() };
    if (file_ssize == -1) {
        std::runtime_error(
            std::format("Failed to determine filesize: {}", filepath.string())
        );
    }

    std::string text;
    text.resize(uz(file_ssize));

    file.seekg(0);
    file.read(text.data(), file_ssize);
    file.close();

    return text;
}

} // namespace aoc_utils
