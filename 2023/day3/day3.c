// Local
#include "my_utils.h"

// Standard library
#include <stdio.h> // FILE, fopen, getline, fclose
#include <stdbool.h> // bool, true, false
#include <stdlib.h> // EXIT_SUCCESS, EXIT_FAILURE
#include <ctype.h> // isdigit
#include <math.h> // ceil, log10
#include <string.h>

////////////////////////////////////////////////////////////////////////////////
// Day 3 data types
typedef struct {
    int i;
    int j;
    char val;
} point2d_char_t;

DECLARE_VECTOR(point2d_char_t, vector_point2d_char_t, vector_point2d_char)
DEFINE_VECTOR(point2d_char_t, vector_point2d_char_t, vector_point2d_char)

typedef struct {
    int first;
    int second;
} pair_int_int_t;

typedef struct {
    pair_int_int_t first;
    vector_int_t second;
} pair_pair_int_int_vector_int_t;
void pair_pair_int_int_vector_int_destroy(pair_pair_int_int_vector_int_t *this) {
    vector_int_destroy(&this->second);
}

DECLARE_VECTOR(
    pair_pair_int_int_vector_int_t,
    vector_pair_pair_int_int_vector_int_t,
    vector_pair_pair_int_int_vector_int
)
DEFINE_VECTOR_USERTYPE(
    pair_pair_int_int_vector_int_t,
    pair_pair_int_int_vector_int,
    vector_pair_pair_int_int_vector_int_t,
    vector_pair_pair_int_int_vector_int
)

////////////////////////////////////////////////////////////////////////////////
// Day 3 supporting functions
bool is_symbol(char c) {
    return (c != '.') && (!isdigit(c));
}
/* Get number of digits in decimal representation of integer */
int n_digits(int n) {
    if (n == 0 || n == 1) {
        return 1;
    }
    return (int) ceil(log10(abs(n))) + (n<0);
}
char * getnum(int *num, char *str) {
    int n_digits = 0;
    for (char c = *str; c != '\0'; c = *++str) {
        if (isdigit(c)) {
            sscanf(str, "%i%n", num, &n_digits);
            str += n_digits;
            return str;
        }
    }
    return NULL;
}
ssize_t getline_laglead(
    vector_char_t *curr,
    vector_char_t *prev,
    vector_char_t *next,
    FILE *fp
){
    ssize_t line_size;
    if (ftell(fp) == 0) { // Reading first line
        line_size = getline(&curr->data, &curr->capacity, fp);
        if (line_size == EOF) {
            vector_char_clear(curr);
            return EOF; // No lines to read
        } else {
            // Remove newline char
            curr->data[line_size-1] = '\0';
            curr->size = (size_t) line_size-1;
        }
        line_size = getline(&next->data, &next->capacity, fp);
        if (line_size == EOF) { // 1 line to read
            vector_char_clear(next);
        } else { // 2+ lines to read
            next->data[line_size-1] = '\0';
            next->size = (size_t) line_size-1;
        }
        return curr->size; // 1+ lines to read
    }
    if (feof(fp)) { // No more lines to read
        vector_char_clear(curr);
        vector_char_clear(prev);
        return EOF;
    }
    // Shift line info to struct for previous line
    // Shift "next" line to "prev" line to be overwritten by getline
    vector_char_t tmp = *prev;
    *prev = *curr;
    *curr = *next;
    *next = tmp;
    vector_char_nullify(&tmp);

    // Store new line info in next
    line_size = getline(&next->data, &next->capacity, fp);
    if (line_size == EOF) {
        vector_char_clear(next);
    } else {
        next->data[line_size-1] = '\0';
        next->size = (size_t) line_size-1;
    }
    return curr->size;
}

vector_point2d_char_t * get_border(
    const vector_char_t *curr,
    size_t start,
    size_t end,
    const vector_char_t *prev,
    const vector_char_t *next
) {
    size_t capacity = (end-start) * 2 + 2;
    vector_point2d_char_t *border = vector_point2d_char_new(capacity);

    bool at_top    = prev->size == 0;
    bool at_left   = start == 0;
    bool at_right  = end == curr->size;
    bool at_bottom = next->size == 0;
    /* printf("DEBUG | [L,B,T,R] = [%i,%i,%i,%i]\n", at_left, at_bottom, at_top, at_right); */

    if (!at_left) {
        start -= 1;
    }
    if (at_right) {
        end = curr->size-1;
    }

    char c = '\0';
    // Process previous row
    if (!at_top) {
        for (size_t j = start; j < end+1; j++) {
            point2d_char_t pnt = {
                .i   = -1,
                .j   = j,
                .val = prev->data[j]
            };
            vector_point2d_char_push_back(border, pnt);
        }
    }

    // Process current row
    if (!at_left) {
        point2d_char_t pnt = {
            .i   = 0,
            .j   = start,
            .val = curr->data[start]
        };
        vector_point2d_char_push_back(border, pnt);
    }
    if (!at_right) {
        point2d_char_t pnt = {
            .i   = 0,
            .j   = end,
            .val = curr->data[end]
        };
        vector_point2d_char_push_back(border, pnt);
    }

    // Process next row
    if (!at_bottom) {
        for (size_t j = start; j < end+1; j++) {
            point2d_char_t pnt = {
                .i   = 1,
                .j   = j,
                .val = next->data[j]
            };
            vector_point2d_char_push_back(border, pnt);
        }
    }
    return border;
}

pair_pair_int_int_vector_int_t * find_gear(
    const vector_pair_pair_int_int_vector_int_t *gears,
    pair_int_int_t coord
) {
    for (size_t i = 0; i < gears->size; i++) {
        pair_int_int_t gear_coord = gears->data[i].first;
        if (coord.first == gear_coord.first && coord.second == gear_coord.second) {
            return &gears->data[i];
        }
    }
    return NULL;
}

void update_gear(
    vector_pair_pair_int_int_vector_int_t *possible_gears,
    pair_int_int_t coords,
    int num
) {
    pair_pair_int_int_vector_int_t *possible_gear = \
        find_gear(possible_gears, coords);
    if (possible_gear == NULL) {
        pair_pair_int_int_vector_int_t new_gear = {
            .first = coords,
            .second = vector_int_construct(2),
        };
        vector_pair_pair_int_int_vector_int_push_back(possible_gears, new_gear);
        possible_gear = &possible_gears->data[possible_gears->size-1];
    }
    vector_int_t *gear_nums = &possible_gear->second;
    vector_int_push_back(gear_nums, num);
}

int compute_gear_ratio_sum(const vector_pair_pair_int_int_vector_int_t *possible_gears) {
    int sum = 0;
    for (size_t i = 0; i < possible_gears->size; i++) {
        pair_pair_int_int_vector_int_t possible_gear = possible_gears->data[i];
        vector_int_t gear_nums = possible_gear.second;
        if (gear_nums.size != 2) {
            continue;
        }
        pair_int_int_t gear_coord = possible_gear.first;
        int gear_ratio = gear_nums.data[0] * gear_nums.data[1];
        printf("INFO | Gear [R%i,C%i] : [%i, %i] -> %i\n",
            gear_coord.first,
            gear_coord.second,
            gear_nums.data[0],
            gear_nums.data[1],
            gear_ratio
        );
        sum += gear_ratio;
    }
    return sum;
}
////////////////////////////////////////////////////////////////////////////////
int main(int argc, char *argv[]) {
    UNUSED_PARAMETER(argc);

    // Setup
    char* input_path = argv[1];
    FILE *fp = fopen(argv[1], "r");
    if (fp == NULL) {
        printf("ERROR | Failed to find/read input file: %s\n", input_path);
        return EXIT_FAILURE;
    }

    // Computations
    vector_int_t *part_numbers = vector_int_new(2);
    vector_pair_pair_int_int_vector_int_t *possible_gears = vector_pair_pair_int_int_vector_int_new(2);
    vector_char_t *prev = vector_char_new(0);
    vector_char_t *curr = vector_char_new(0);
    vector_char_t *next = vector_char_new(0);
    vector_int_t *curr_part_numbers = vector_int_new(2);
    int row_idx = -1;
    while (getline_laglead(curr, prev, next, fp) != EOF) {
        row_idx++;
        /* printf("DEBUG | \n"); */
        /* printf("DEBUG |     %s\n",    prev->data != NULL ? prev->data : "\n"); */
        /* printf("DEBUG | R%i) %s\n", row_idx, curr->data != NULL ? curr->data  : "\n"); */
        /* printf("DEBUG |     %s\n",    next->data != NULL ? next->data : "\n"); */
        int num = 0;
        char* head = curr->data;
        while ((head = getnum(&num, head)) != NULL) {
            size_t end = head - curr->data;
            size_t start = end - n_digits(num);
            /* printf("DEBUG | Parsed number: curr[%zu:%zu]=%i\n", start,end,num); */
            bool symbol_found = false;
            vector_point2d_char_t *border = get_border(curr, start, end, prev, next);
            for (size_t i = 0; i < border->size; i++) {
                point2d_char_t pnt = border->data[i];
                /* printf("DEBUG | border R%i C%i = %c\n", row_idx + pnt.i, pnt.j, pnt.val); */
                if (!is_symbol(pnt.val)) {
                    continue;
                }
                symbol_found = true;
                if (pnt.val == '*') {
                    pair_int_int_t coords = {
                        .first  = pnt.i + row_idx,
                        .second = pnt.j
                    };
                    update_gear(possible_gears, coords, num);
                }
            }
            vector_point2d_char_free(&border);
            border = NULL;

            if (symbol_found) {
                vector_int_push_back(curr_part_numbers, num);
            }
        }
        vector_char_t *print_str = vector_int_to_str(curr_part_numbers);
        printf("INFO | R%d part #s: %s\n", row_idx, print_str->data);
        vector_char_free(&print_str);
        print_str = NULL;

        vector_int_extend(part_numbers, curr_part_numbers);
        vector_int_clear(curr_part_numbers);
    }
    vector_int_free(&curr_part_numbers);
    curr_part_numbers = NULL;

    int gear_ratio_sum = compute_gear_ratio_sum(possible_gears);

    printf("INFO | Part 1 solution: %i\n", vector_int_sum(part_numbers));
    printf("INFO | Part 2 solution: %i\n", gear_ratio_sum);

    // Tear down
    fclose(fp);
    vector_int_free(&part_numbers);
    vector_pair_pair_int_int_vector_int_free(&possible_gears);
    vector_char_free(&prev);
    vector_char_free(&curr);
    vector_char_free(&next);

    return EXIT_SUCCESS;
}
