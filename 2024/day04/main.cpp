
// 1st party
#include "run.hpp"
#include "aoc_utils.hpp"

// Standard library
#include <concepts>
#include <fstream>
#include <filesystem>
#include <mdspan>
#include <print>
#include <utility>
#include <ranges>
#include <algorithm>


namespace {
// Aliases
namespace aoc    = aoc_utils;
namespace fs     = std::filesystem;
// namespace ranges = std::ranges;
namespace views  = std::views;

// using InputType = std::mdspan<char, std::dextents<int, 2>>;
using ext2d = std::dextents<ssize_t, 2>;
template <typename T>
using mdspan2d = std::mdspan<T, ext2d>;
template <class T>
using mdspan2d_c = mdspan2d<std::add_const_t<std::remove_const_t<T>>>;
template <class T>
inline auto as_read_only(mdspan2d<T> m) { return mdspan2d_c<T>(m); }

template <typename T>
struct array2d {
    std::vector<T> data;
    ext2d extents;

    mdspan2d<T> mdspan() {
        return std::mdspan(data.data(), extents);
    }
};
using InputType = array2d<char>;

////////////////////////////////////////////////////////////////////////////////
// Part 1
constexpr std::array<std::pair<int8_t, int8_t>, 8> directions {{
    { 1,  0},  // E
    { 1,  1},  // SE
    { 0,  1},  // S
    {-1,  1},  // SW
    {-1,  0},  // W
    {-1, -1},  // NW
    { 0, -1},  // N
    { 1, -1}   // NE
}};

template <typename T>
auto md_indexes(mdspan2d<T> arr_) {
    auto arr = as_read_only(arr_);
    // views::cartesian_product(
    //     views::iota(ssize_t{0}, arr.extent(0)),
    //     views::iota(ssize_t{0}, arr.extent(1))
    // )
    const auto n_cols = arr.extent(1);
    return
      views::iota(ssize_t{0}, std::ssize(arr))
    | views::transform(
        [n_cols](const auto i){return std::array{i/n_cols, i%n_cols};}
    );
}

template <typename T, std::predicate<char> F>
auto md_where(mdspan2d<T> arr_, F pred) {
    auto arr = as_read_only(arr_);
    return md_indexes(arr) 
        | views::filter([arr, pred](const auto& idx) {return pred(arr[idx]);});
}

template <typename T>
inline bool in_bounds(mdspan2d<T> arr_, const ssize_t i, const ssize_t j) {
    auto arr = as_read_only(arr_);
    return 0 <= i && i < arr.extent(0) 
        && 0 <= j && j < arr.extent(1);
}

template <std::ranges::input_range R1, std::ranges::input_range R2>
auto cartesian_product(R1&& r1, R2&& r2) {
    // NB: Be careful to avoid passing/returning dangling references
    return std::forward<R1>(r1) | std::views::transform([r2](auto&& x) {
       return std::forward<R2>(r2) | std::views::transform([x](auto&& y) {
          return std::pair{x, y};
      });
    }) 
    | std::views::join;
}

int64_t part1(InputType& arr2d) {
    auto arr {arr2d.mdspan()};

    // Option 1: Functional
    auto x_idxs = md_where(arr, [](char c){return c == 'X';});
    return aoc::sum(
        cartesian_product(x_idxs, directions) 
        | views::transform(
            [arr](const auto idx_dir) {
                const auto& [idx, dir] = idx_dir;
                const auto& [i, j] = idx;
                const auto& [x, y] = dir;
                return static_cast<int64_t>(
                   in_bounds(arr, i + 3*x, j + 3*y)
                   && (arr[i + 1*x, j + 1*y] == 'M')
                   && (arr[i + 2*x, j + 2*y] == 'A')
                   && (arr[i + 3*x, j + 3*y] == 'S')
                );
            }
        )
    );

    // Option 2: Procedural
    // ssize_t count = 0;
    // for (ssize_t i = 0; i < arr.extent(0); ++i) {
    //     for (ssize_t j = 0; j < arr.extent(1); ++j) {
    //         if (arr[i, j] != 'X') {
    //             continue;
    //         }
    //         for (const auto [x, y] : directions) {
    //             if (
    //                    i+3*x < 0 || arr.extent(0) <= i+3*x
    //                 || j+3*y < 0 || arr.extent(1) <= j+3*y
    //             ) {
    //                 continue;
    //             }
    //             count += (
    //                    arr[i + 1*x, j + 1*y] == 'M'
    //                 && arr[i + 2*x, j + 2*y] == 'A'
    //                 && arr[i + 3*x, j + 3*y] == 'S'
    //             );
    //         }
    //     }
    // }
    // return count;
}

////////////////////////////////////////////////////////////////////////////////
// Part 2
int64_t part2(InputType& arr2d) {
    auto arr {arr2d.mdspan()};

    // Option 1: Procedural
    ssize_t count = 0;
    for (ssize_t i = 1; i < arr.extent(0)-1; ++i) {
        for (ssize_t j = 1; j < arr.extent(1)-1; ++j) {
            if (arr[i, j] != 'A') {
                continue;
            }
            count += (
                (
                       (arr[i-1, j-1] == 'M' && arr[i+1, j+1] == 'S')
                    || (arr[i-1, j-1] == 'S' && arr[i+1, j+1] == 'M')
                )
                &&
                (
                       (arr[i+1, j-1] == 'M' && arr[i-1, j+1] == 'S')
                    || (arr[i+1, j-1] == 'S' && arr[i-1, j+1] == 'M')
                )
            );
        }
    }
    return count;
}

////////////////////////////////////////////////////////////////////////////////
InputType read_matrix(const fs::path& filepath) {
    std::ifstream file(filepath);
    if (!file) {
        throw aoc::FileReadException(filepath);
    }

    std::vector<char> data;
    ssize_t n_rows = 0, n_cols = 0, i_col = 0;

    // ASSUMPTION: no CRLF and no empty lines
    char c;
    while(file.get(c)) {
        if (c != '\n') {
            ++i_col;
            data.push_back(c);
            continue;
        }
        ++n_rows;
        n_cols = std::exchange(i_col, 0);
    }

    return array2d<char>{data, std::dextents<int, 2>{n_rows, n_cols}};

}
}
////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    const aoc::InputPathArgs args = aoc::parse_args(argc, argv);
    aoc::run<InputType>(args.input_path, read_matrix, part1, part2);
}

