// Does C++ have something like a csv-reader to handle common read cases
// printing collections
// Logging levels
// Benchmarking
// Suggestions to speed it up

#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <vector>
namespace fs = std::filesystem;

////////////////////////////////////////////////////////////////////////////////
// TODO: Refactor into utils library
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
    explicit FileNotFoundException(const fs::path &path)
        : std::runtime_error("File not found: " + path.string()) {}
};
class FileReadException : public std::runtime_error {
  public:
    explicit FileReadException(const std::string &msg) : std::runtime_error(msg) {}
    explicit FileReadException(const fs::path &path)
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

////////////////////////////////////////////////////////////////////////////////
// Declarations
struct ProgramOptions {
    std::string input_path;
    bool verbose = false;
    // TODO: Use optional dtype instead of sentinal value
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

ProgramOptions parse_args(int argc, char *argv[]);
std::pair<std::vector<int>, std::vector<int>> read_data(const fs::path &filepath);

////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    const ProgramOptions args = parse_args(argc, argv);
    if (args.help) {
        std::cerr << args.help_msg << std::endl;
        return 1;
    }

    if (args.verbose) {
        std::cout << "INFO | Reading file " << args.input_path << '\n';
    }

    // Read inputs
    auto [left, right] = read_data(args.input_path);

    ////////////////////////////////////////
    // Solution
    ////////////////////////////////////////
    sort(left.begin(), left.end());
    sort(right.begin(), right.end());

    if (args.verbose) {
        std::cout << "INFO | Vectors " << left.size() << ", " << left[0] << '\n';
        std::cout << "INFO | Vectors " << right.size() << ", " << right[0] << '\n';
    }

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

    std::cout << total_diff << std::endl;
}

ProgramOptions parse_args(int argc, char *argv[]) {
    ProgramOptions options;
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
// Supporting functions
std::pair<std::vector<int>, std::vector<int>> read_data(const fs::path &filepath) {
    std::ifstream file(filepath);
    if (!file) {
        throw FileReadException(filepath);
    };

    std::vector<int> left, right;

    std::string line;
    int line_num = -1;
    while (std::getline(file, line)) {
        line_num++;
        std::istringstream iss(line);
        int val1{}, val2{};
        if (!(iss >> val1 >> val2)) {
            throw FileParseException(line, line_num);
        }

        // std::string remainder;
        // if (iss >> remainder) {
        //     throw FileParseException("Extra data: " + line, line_num);
        // }

        left.push_back(val1);
        right.push_back(val2);
    }

    return {left, right};
}
