
// 1st party
#include "run.hpp"
#include "aoc_utils.hpp"

// Standard library
#include <charconv> // from_chars
#include <filesystem>
#include <vector>
#include <algorithm> // std::views
#include <unordered_set>


namespace {

// Aliases
namespace aoc = aoc_utils;
namespace fs = std::filesystem;

using aoc::uz;

using PageNum = int32_t;
using Update  = std::vector<PageNum>;
using Rule    = std::pair<PageNum, PageNum>;
using Rules   = std::unordered_set<uint64_t>;
struct InputType {
    Rules rules;
    std::vector<Update> updates;
};

////////////////////////////////////////////////////////////////////////////////
inline auto key(const std::pair<int32_t, int32_t>& rule) -> uint64_t {
    return static_cast<uint64_t>(rule.first) << 32 | static_cast<uint64_t>(rule.second);
}
PageNum get_mid_item(const Update& u) { return u[std::size(u)/2]; }

auto make_comparer(const Rules& rules) {
    return [&rules](const PageNum& x, const PageNum& y) {
        return x!=y && !rules.contains(key({y,x}));
    };
}
enum class Order : bool {
    Sorted = true,
    Unsorted = false
};
constexpr auto make_order_checker(const Rules& rules, const Order sorted) {
    return [&rules, sorted](const Update& u){
        return std::ranges::is_sorted(u, make_comparer(rules)) == std::to_underlying(sorted);
    };
}

////////////////////////////////////////////////////////////////////////////////
// Part 1
int64_t part1(const InputType& input) {
    return aoc::sum(input.updates
        | std::views::filter(make_order_checker(input.rules, Order::Sorted))
        | std::views::transform(get_mid_item)
    );
}

////////////////////////////////////////////////////////////////////////////////
// Part 2
int64_t part2(InputType& input) {
    auto&& get_median = [&input](auto& v){
        std::ranges::nth_element(v, v.begin() + v.size() / 2, make_comparer(input.rules));
        return get_mid_item(v);
    };
    return aoc::sum(input.updates
        | std::views::filter(make_order_checker(input.rules, Order::Unsorted))
        | std::views::transform(get_median)
    );
}

////////////////////////////////////////////////////////////////////////////////
InputType read_data(const fs::path& filepath) {
    const std::string text = aoc::read_text(filepath);

    InputType input;
          auto start = &*std::cbegin(text);
    const auto eof   = &*std::cend(text);

    // Parse rules
    int x = 0;
    int y = 0;
    while (*start != '\n') {
        // Expected line format: "12,34\n"
        std::from_chars(start+0, start+2, x);
        std::from_chars(start+3, start+5, y);
        input.rules.emplace(key({x, y}));
        start += 6;
    }

    // Parse updates
    ++start;
    static constexpr std::string delims = ",\n";
    while (start != eof) {
        Update update;
        auto sep = start;
        while (*sep != '\n') {
            sep = std::find_first_of(
                start, eof, std::cbegin(delims), std::end(delims)
            );
            std::from_chars(start, sep, update.emplace_back());
            start = sep+1;
        }
        input.updates.push_back(std::move(update));
    }

    return input;
}

} // namespace
////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    const aoc::InputPathArgs args = aoc::parse_args(argc, argv);
    aoc::run<InputType>(args.input_path, read_data, part1, part2);
}

