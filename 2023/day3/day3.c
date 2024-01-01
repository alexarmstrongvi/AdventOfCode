#include "my_utils.h"

#include <stdio.h> // FILE, fopen, getline, fclose
#include <stdbool.h> // bool, true, false
#include <stdlib.h> // calloc, free, EXIT_SUCCESS, EXIT_FAILURE
#include <ctype.h> // isdigit
#include <math.h> // ceil, log10
#include <limits.h> // INT_MAX
#include <string.h>

// TODO: Update to using pointers where there is unecessary copying

////////////////////////////////////////////////////////////////////////////////
typedef struct {
    int i;
    int j;
    char val;
} point2d_char_t;
typedef struct {
    int first;
    int second;
} pair_int_int_t;

DECLARE_VECTOR(point2d_char_t, vector_point2d_char_t, vector_point2d_char)
DEFINE_VECTOR(point2d_char_t, vector_point2d_char_t, vector_point2d_char)

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
void vector_pair_pair_int_int_vector_int_destroy(
    vector_pair_pair_int_int_vector_int_t *this
) {
    for (size_t i = 0; i < this->size; i++) {
        pair_pair_int_int_vector_int_destroy(&this->data[i]);
    }
    free(this->data);
    vector_pair_pair_int_int_vector_int_nullify(this);
}

int vector_int_sum(vector_int_t vec) {
    int sum = 0;
    for (size_t i = 0; i < vec.size; i++) {
        sum += vec.data[i];
    }
    return sum;
}

enum {
    MAX_INT_CHARS = 1+10+1 // "-" + "2147483648" + "\0"
};
vector_char_t vector_int_to_str(vector_int_t vec) {
    size_t capacity = vec.size > 0 ? vec.size * 3 - 1 : 3;
    vector_char_t str = vector_char_construct(capacity);
    vector_char_push_back(&str, '[');
    for (size_t i = 0; i < vec.size; i++) {
        char int_str[MAX_INT_CHARS];
        sprintf(int_str, "%i", vec.data[i]);

        char *p = int_str;
        for (char c = *p; c != '\0'; c = *++p) {
            vector_char_push_back(&str, c);
        }

        if (i < vec.size -1) {
            vector_char_push_back(&str, ',');
            vector_char_push_back(&str, ' ');
        }
    }
    vector_char_push_back(&str, ']');
    return str;
}

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
    vector_char_t *p_curr,
    vector_char_t *p_prev,
    vector_char_t *p_next,
    FILE *fp
){
    ssize_t line_size;
    if (ftell(fp) == 0) { // Reading first line
        line_size = getline(&p_curr->data, &p_curr->capacity, fp);
        if (line_size == EOF) {
            vector_char_clear(p_curr);
            return EOF; // No lines to read
        } else {
            // Remove newline char
            p_curr->data[line_size-1] = '\0';
            p_curr->size = (size_t) line_size-1;
        }
        line_size = getline(&p_next->data, &p_next->capacity, fp);
        if (line_size == EOF) { // 1 line to read
            vector_char_clear(p_next);
        } else { // 2+ lines to read
            p_next->data[line_size-1] = '\0';
            p_next->size = (size_t) line_size-1;
        }
        return p_curr->size; // 1+ lines to read
    }
    if (feof(fp)) { // No more lines to read
        vector_char_clear(p_curr);
        vector_char_clear(p_prev);
        return EOF;
    }
    // Shift line info to struct for previous line
    // Shift "next" line to "prev" line to be overwritten by getline
    vector_char_t tmp = *p_prev;
    *p_prev = *p_curr;
    *p_curr = *p_next;
    *p_next = tmp;
    vector_char_nullify(&tmp);

    // Store new line info in p_next
    line_size = getline(&p_next->data, &p_next->capacity, fp);
    if (line_size == EOF) {
        vector_char_clear(p_next);
    } else {
        p_next->data[line_size-1] = '\0';
        p_next->size = (size_t) line_size-1;
    }
    return p_curr->size;
}

vector_point2d_char_t get_border(
    vector_char_t curr,
    size_t start,
    size_t end,
    vector_char_t prev,
    vector_char_t next
) {
    size_t capacity = (end-start) * 2 + 2;
    vector_point2d_char_t border = vector_point2d_char_construct(capacity);

    bool at_top    = prev.size == 0;
    bool at_left   = start == 0;
    bool at_right  = end == curr.size;
    bool at_bottom = next.size == 0;
    /* printf("DEBUG | [L,B,T,R] = [%i,%i,%i,%i]\n", at_left, at_bottom, at_top, at_right); */

    if (!at_left) {
        start -= 1;
    }
    if (at_right) {
        end = curr.size-1;
    }

    char c = '\0';
    // Process previous row
    if (!at_top) {
        for (size_t j = start; j < end+1; j++) {
            point2d_char_t pnt = {
                .i   = -1,
                .j   = j,
                .val = prev.data[j]
            };
            vector_point2d_char_push_back(&border, pnt);
        }
    }

    // Process current row
    if (!at_left) {
        point2d_char_t pnt = {
            .i   = 0,
            .j   = start,
            .val = curr.data[start]
        };
        vector_point2d_char_push_back(&border, pnt);
    }
    if (!at_right) {
        point2d_char_t pnt = {
            .i   = 0,
            .j   = end,
            .val = curr.data[end]
        };
        vector_point2d_char_push_back(&border, pnt);
    }

    // Process next row
    if (!at_bottom) {
        for (size_t j = start; j < end+1; j++) {
            point2d_char_t pnt = {
                .i   = 1,
                .j   = j,
                .val = next.data[j]
            };
            vector_point2d_char_push_back(&border, pnt);
        }
    }
    return border;
}

pair_pair_int_int_vector_int_t * find_gear(
    vector_pair_pair_int_int_vector_int_t gears,
    pair_int_int_t coord
) {
    for (size_t i = 0; i < gears.size; i++) {
        pair_int_int_t gear_coord = gears.data[i].first;
        if (coord.first == gear_coord.first && coord.second == gear_coord.second) {
            return &gears.data[i];
        }
    }
    return NULL;
}

void update_gear(
    vector_pair_pair_int_int_vector_int_t *p_possible_gears,
    pair_int_int_t coords,
    int num
) {
    pair_pair_int_int_vector_int_t *p_possible_gear = \
        find_gear(*p_possible_gears, coords);
    if (p_possible_gear == NULL) {
        pair_pair_int_int_vector_int_t new_gear = {
            .first = coords,
            .second = vector_int_construct(2),
        };
        vector_pair_pair_int_int_vector_int_push_back(p_possible_gears, new_gear);
        p_possible_gear = &p_possible_gears->data[p_possible_gears->size-1];
    }
    vector_int_t *gear_nums = &p_possible_gear->second;
    vector_int_push_back(gear_nums, num);
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
    vector_int_t part_numbers = vector_int_construct(2);
    vector_pair_pair_int_int_vector_int_t possible_gears = vector_pair_pair_int_int_vector_int_construct(2);
    vector_char_t prev = vector_char_construct(0);
    vector_char_t curr = vector_char_construct(0);
    vector_char_t next = vector_char_construct(0);
    int row_idx = -1;
    while (getline_laglead(&curr, &prev, &next, fp) != EOF) {
        row_idx++;
        /* printf("DEBUG | \n"); */
        /* printf("DEBUG |     %s\n",    prev.data != NULL ? prev.data : "\n"); */
        /* printf("DEBUG | R%i) %s\n", row_idx, curr.data != NULL ? curr.data  : "\n"); */
        /* printf("DEBUG |     %s\n",    next.data != NULL ? next.data : "\n"); */
        vector_int_t curr_part_numbers = vector_int_construct(2);
        int num = 0;
        char* p_head = curr.data;
        while ((p_head = getnum(&num, p_head)) != NULL) {
            size_t end = p_head - curr.data;
            size_t start = end - n_digits(num);
            /* printf("DEBUG | Parsed number: curr[%zu:%zu]=%i\n", start,end,num); */
            bool symbol_found = false;
            vector_point2d_char_t border = get_border(curr, start, end, prev, next);
            for (size_t i = 0; i < border.size; i++) {
                point2d_char_t pnt = border.data[i];
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
                    update_gear(&possible_gears, coords, num);
                }
            }
            vector_point2d_char_destroy(&border);

            if (symbol_found) {
                vector_int_push_back(&curr_part_numbers, num);
            }
        }
        vector_char_t print_str = vector_int_to_str(curr_part_numbers);
        printf("INFO | R%d part #s: %s\n", row_idx, print_str.data);
        vector_char_destroy(&print_str);

        vector_int_extend(&part_numbers, curr_part_numbers);
        vector_int_destroy(&curr_part_numbers);
    }

    // Compute gear ratio sum for part 2
    int gear_ratio_sum = 0;
    for (size_t i = 0; i < possible_gears.size; i++) {
        pair_pair_int_int_vector_int_t possible_gear = possible_gears.data[i];
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
        gear_ratio_sum += gear_ratio;
    }

    printf("INFO | Part 1 solution: %i\n", vector_int_sum(part_numbers));
    printf("INFO | Part 2 solution: %i\n", gear_ratio_sum);

    // Tear down
    fclose(fp);
    vector_int_destroy(&part_numbers);
    vector_pair_pair_int_int_vector_int_destroy(&possible_gears);
    vector_char_destroy(&prev);
    vector_char_destroy(&curr);
    vector_char_destroy(&next);

    return EXIT_SUCCESS;
}
