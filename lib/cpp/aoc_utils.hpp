#pragma once
#include <filesystem>
#include <optional>
#include <stdexcept>

namespace aoc_utils {
////////////////////////////////////////////////////////////////////////////////

class MissingArgsException : public std::runtime_error {
  public:
    explicit MissingArgsException(const std::string &msg);
    ~MissingArgsException() noexcept override;
};
class ExtraArgsException : public std::runtime_error {
  public:
    explicit ExtraArgsException(const std::string &msg);
    ~ExtraArgsException() noexcept override;
};
class FileNotFoundException : public std::runtime_error {
  public:
    explicit FileNotFoundException(const std::string &msg);
    explicit FileNotFoundException(const std::filesystem::path &path);
    ~FileNotFoundException() noexcept override;
};
class FileReadException : public std::runtime_error {
  public:
    explicit FileReadException(const std::string &msg);
    explicit FileReadException(const std::filesystem::path &path);
    ~FileReadException() noexcept override;
};
class FileParseException : public std::runtime_error {
  public:
    explicit FileParseException(const std::string &line);
    explicit FileParseException(const std::string &line, const int64_t line_num);
    ~FileParseException() noexcept override;
};
class ArgvParseException : public std::runtime_error {
  public:
    explicit ArgvParseException(const std::string &msg);
    ~ArgvParseException() noexcept override;
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

auto read_text(const std::filesystem::path& filepath) -> std::string;

}

#include "aoc_utils.tpp"
