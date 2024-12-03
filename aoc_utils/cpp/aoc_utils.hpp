#include <filesystem>
#include <optional>
#include <stdexcept>

namespace aoc_utils {
////////////////////////////////////////////////////////////////////////////////

class MissingArgsException : public std::runtime_error {
  public:
    explicit MissingArgsException(const std::string &msg) : std::runtime_error(msg) {}
};
class ExtraArgsException : public std::runtime_error {
  public:
    explicit ExtraArgsException(const std::string &msg) : std::runtime_error(msg) {}
};
class FileNotFoundException : public std::runtime_error {
  public:
    explicit FileNotFoundException(const std::string &msg) : std::runtime_error(msg) {}
    explicit FileNotFoundException(const std::filesystem::path &path)
        : std::runtime_error("File not found: " + path.string()) {}
};
class FileReadException : public std::runtime_error {
  public:
    explicit FileReadException(const std::string &msg) : std::runtime_error(msg) {}
    explicit FileReadException(const std::filesystem::path &path)
        : std::runtime_error("Failed to read file: " + path.string()) {}
};
class FileParseException : public std::runtime_error {
  public:
    explicit FileParseException(const std::string &line, const size_t line_num)
        : std::runtime_error(
              "Failed to parse line " + std::to_string(line_num) + ": '" + line + "'"
          ) {}
};
class ArgvParseException : public std::runtime_error {
  public:
    explicit ArgvParseException(const std::string &msg) : std::runtime_error(msg) {}
};

struct InputPathArgs {
    std::string input_path;
    bool verbose = false;
    std::optional<size_t> max_lines;
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

////////////////////////////////////////////////////////////////////////////////
// end AoC_Utils
} 

#include "aoc_utils.tpp"
