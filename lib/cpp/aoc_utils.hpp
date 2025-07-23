#pragma once
#include <filesystem>
#include <optional>
#include <stdexcept>

namespace aoc_utils {
////////////////////////////////////////////////////////////////////////////////

class MissingArgsException : public std::runtime_error {
  public:
    explicit MissingArgsException(const std::string &msg);
};
class ExtraArgsException : public std::runtime_error {
  public:
    explicit ExtraArgsException(const std::string &msg);
};
class FileNotFoundException : public std::runtime_error {
  public:
    explicit FileNotFoundException(const std::string &msg);
    explicit FileNotFoundException(const std::filesystem::path &path);
};
class FileReadException : public std::runtime_error {
  public:
    explicit FileReadException(const std::string &msg);
    explicit FileReadException(const std::filesystem::path &path);
};
class FileParseException : public std::runtime_error {
  public:
    explicit FileParseException(const std::string &line);
    explicit FileParseException(const std::string &line, const int64_t line_num);
};
class ArgvParseException : public std::runtime_error {
  public:
    explicit ArgvParseException(const std::string &msg);
};

struct InputPathArgs {
    std::filesystem::path input_path;
    bool verbose = false;
    std::optional<int64_t> max_lines;
    // Help
    bool help = false;
    const std::string help_msg = 
        "Usage: "
        "[-v|--verbose] "
        "[-n|--max-lines NUM] "
        "<input_path>"
        "\n";
};

InputPathArgs parse_args(int argc, char *argv[]);

}

#include "aoc_utils.tpp"
