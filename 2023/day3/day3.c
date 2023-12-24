#include <stdio.h> // FILE, fopen, getline, fclose
#include <stdbool.h> // bool, true, false
#include <stdlib.h> // calloc, free, EXIT_SUCCESS, EXIT_FAILURE
#include <ctype.h> // isdigit
#include <math.h> // ceil, log10
#include <limits.h> // INT_MAX
#include <string.h>

// TODO: Function overloading in C
#define FREE(x) do {free(x); (x) = NULL;} while (0)
#define UNUSED_PARAMETER(x) ((void)(x))

// TODO: How to inline (getting linker errors)
// TODO: Create hash map
////////////////////////////////////////////////////////////////////////////////
int sign(int n) {
    return (n > 0) - (n < 0);
}
int ceil_power_of_2(int n) {
    if (n == 0) {
        return 2;
    }
    return pow(2, floor(log2(abs(n)))+1) * sign(n);
}
int n_digits(int n) {
    if (n == 0 || n == 1) {
        return 1;
    } 
    return (int) ceil(log10(abs(n))) + (n<0);
}
////////////////////////////////////////////////////////////////////////////////
// TODO: #define VECTOR(T) ... define struct, constructor, destructor, realloc
typedef struct {
    char *data;
    size_t size;
    size_t capacity;
} vector_char_t;

void vector_char_clear(vector_char_t *this) {
    this->data     = NULL;
    this->capacity = 0;
    this->size     = 0;
}
void vector_char_init(vector_char_t *this, size_t capacity) {
    vector_char_clear(this);
    if (capacity > 0) {
        this->data = (char *) calloc(capacity, sizeof(char));
        if (this->data == NULL) {
            printf("WARNING | Failed to allocate memory for vector_char_t\n");
        }
        this->capacity = capacity;
    }
}
vector_char_t vector_char_construct(size_t capacity) {
    vector_char_t vec;
    vector_char_init(&vec, capacity);
    return vec;
}
void vector_char_destroy(vector_char_t *this) {
    free(this->data);
    vector_char_clear(this);
}
void vector_char_resize(vector_char_t *this) {
    size_t capacity = (size_t) ceil_power_of_2(this->capacity);
    this->data = (char *) realloc(this->data, capacity * sizeof(char));
    if (this->data == NULL) {
        printf("WARNING | Failed to realloc more memory for vector_char\n");
    } else {
        this->capacity = capacity;
        /* printf("DEBUG | Reallocated %zu elements to vector_char_t\n", this->capacity); */
    }
}
void vector_char_push_back(vector_char_t *this, char entry) {
    if (this->size == this->capacity) {
        /* printf("DEBUG | Before resizing:[%p, %p) [%zu]\n", (void *)this->data, (void *)(this->data + this->capacity), this->capacity); */
        vector_char_resize(this);
        /* printf("DEBUG | After resizing :[%p, %p) [%zu]\n", (void *)this->data, (void *)(this->data + this->capacity), this->capacity); */
    }
    this->data[this->size] = entry;
    this->size += 1;
}
void vector_char_extend(vector_char_t *this, vector_char_t vec) {
    for (size_t i = 0; i < vec.size; i++) {
        vector_char_push_back(this, vec.data[i]);
    }
}

////////////////////////////////////////////////////////////////////////////////
typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} vector_int_t;

void vector_int_clear(vector_int_t *this) {
    this->data     = NULL;
    this->capacity = 0;
    this->size     = 0;
}
void vector_int_init(vector_int_t *this, int capacity) {
    vector_int_clear(this);
    if (capacity > 0) {
        this->data = (int *) calloc(capacity, sizeof(int));
        if (this->data == NULL) {
            printf("WARNING | Failed to allocate memory for vector_int_t\n");
        }
        this->capacity = capacity;
    }
}
vector_int_t vector_int_construct(int capacity) {
    vector_int_t vec;
    vector_int_init(&vec, capacity);
    return vec;
}
void vector_int_destroy(vector_int_t *this) {
    free(this->data);
    vector_int_clear(this);
}
void vector_int_resize(vector_int_t *this) {
    size_t capacity = (size_t) ceil_power_of_2(this->capacity);
    this->data = (int *) realloc(this->data, capacity * sizeof(int));
    if (this->data == NULL) {
        printf("WARNING | Failed to realloc more memory for vector_int\n");
    } else {
        this->capacity = capacity;
        /* printf("DEBUG | Reallocated %zu elements to vector_int_t\n", this->capacity); */
    }
}
void vector_int_push_back(vector_int_t *this, int entry) {
    if (this->size == this->capacity) {
        /* printf("DEBUG | Before resizing:[%p, %p) [%zu]\n", (void *)this->data, (void *)(this->data + this->capacity), this->capacity); */
        vector_int_resize(this);
        /* printf("DEBUG | After resizing :[%p, %p) [%zu]\n", (void *)this->data, (void *)(this->data + this->capacity), this->capacity); */
    }
    this->data[this->size] = entry;
    this->size += 1;
}
void vector_int_extend(vector_int_t *this, vector_int_t vec) {
    for (size_t i = 0; i < vec.size; i++) {
        vector_int_push_back(this, vec.data[i]);
    }
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
typedef struct {
    int i;
    int j;
    char val;
} point2d_char_t;

typedef struct {
    point2d_char_t *data;
    size_t size;
    size_t capacity;
} vector_point2d_char_t;

void vector_point2d_char_clear(vector_point2d_char_t *this) {
    this->data     = NULL;
    this->capacity = 0;
    this->size     = 0;
}
void vector_point2d_char_init(vector_point2d_char_t *this, size_t capacity) {
    vector_point2d_char_clear(this);
    if (capacity > 0) {
        this->data = (point2d_char_t *) calloc(capacity, sizeof(point2d_char_t));
        if (this->data == NULL) {
            printf("WARNING | Failed to allocate memory for vector_point2d_char_t\n");
        }
        this->capacity = capacity;
    }
}
vector_point2d_char_t vector_point2d_char_construct(size_t capacity) {
    vector_point2d_char_t vec;
    vector_point2d_char_init(&vec, capacity);
    return vec;
}
void vector_point2d_char_destroy(vector_point2d_char_t *this) {
    free(this->data);
    vector_point2d_char_clear(this);
}
void vector_point2d_char_resize(vector_point2d_char_t *this) {
    size_t capacity = (size_t) ceil_power_of_2(this->capacity);
    this->data = (point2d_char_t *) realloc(this->data, capacity * sizeof(point2d_char_t));
    if (this->data == NULL) {
        printf("WARNING | Failed to realloc more memory for vector_point2d_char\n");
    } else {
        this->capacity = capacity;
        /* printf("DEBUG | Reallocated %zu elements to vector_point2d_char_t\n", this->capacity); */
    }
}
void vector_point2d_char_push_back(vector_point2d_char_t *this, point2d_char_t entry) {
    if (this->size == this->capacity) {
        /* printf("DEBUG | Before resizing:[%p, %p) [%zu]\n", (void *)this->data, (void *)(this->data + this->capacity), this->capacity); */
        vector_point2d_char_resize(this);
        /* printf("DEBUG | After resizing :[%p, %p) [%zu]\n", (void *)this->data, (void *)(this->data + this->capacity), this->capacity); */
    }
    this->data[this->size] = entry;
    this->size += 1;
}

////////////////////////////////////////////////////////////////////////////////
bool is_symbol(char c) {
    return (c != '.') && (!isdigit(c));
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
    vector_char_t *p_line,
    vector_char_t *p_prev, 
    vector_char_t *p_next,
    FILE *fp
){
    ssize_t line_size;
    bool at_top = p_line->data == NULL;
    if (at_top) { // Reading first line
        line_size = getline(&p_line->data, &p_line->capacity, fp);
        if (line_size == EOF) { 
            vector_char_clear(p_line);
            return EOF; // No lines to read
        } else {
            // Remove newline char
            p_line->data[line_size-1] = '\0';
            p_line->size = (size_t) line_size-1;
        }
        line_size = getline(&p_next->data, &p_next->capacity, fp);
        if (line_size == EOF) { // 2+ lines to read
            vector_char_clear(p_next);
        } else {
            p_next->data[line_size-1] = '\0';
            p_next->size = (size_t) line_size-1;
        }
        return p_line->size; // 1-2 lines to read
    }
    bool at_bottom = p_next->data == NULL && p_line->data != NULL;
    if (at_bottom) {
        vector_char_clear(p_line);
        vector_char_clear(p_prev);
        return EOF; // No more lines to read
    }
    // Shift line info to struct for previous line
    // Shift "next" line to "prev" line to be overwritten by getline
    vector_char_t tmp = *p_prev;
    *p_prev = *p_line;
    *p_line  = *p_next;
    *p_next = tmp;
    vector_char_clear(&tmp);
    
    // Store new line info in p_next
    line_size = getline(&p_next->data, &p_next->capacity, fp);
    if (line_size == EOF) { 
        vector_char_clear(p_next);
    } else {
        p_next->data[line_size-1] = '\0';
        p_next->size = (size_t) line_size-1;
    }
    return p_line->size;
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

    bool at_top    = prev.data == NULL;
    bool at_left   = start == 0;
    bool at_right  = end == curr.size;
    bool at_bottom = next.data == NULL;
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
                .i   = -1,
                .j   = j,
                .val = next.data[j]
            };
            vector_point2d_char_push_back(&border, pnt);
        }
    }
    return border;
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
    vector_char_t curr, prev, next;
    vector_char_clear(&prev);
    vector_char_clear(&curr);
    vector_char_clear(&next);
    int row_idx = -1;
    while (getline_laglead(&curr, &prev, &next, fp) != EOF) {
        row_idx++;
        /* if (row_idx != 9) {continue;} // TESTING */
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
                /* if (pnt.val == '*') { */
                /*     pair_int_t coords = { */
                /*         .i = pnt.i + row_idx, */ 
                /*         .j = pnt.j */
                /*     } */
                /*     list_int_t *val = map_pair_int_get(&possible_gears, coords); */
                /*     list_int_push_back(&gear_nums, num); */
                /* } */
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
    /* vector_char_t print_str = vector_int_to_str(part_numbers); */
    /* printf("DEBUG | Part numbers: %s\n", print_str.data); */
    /* vector_char_destroy(&print_str); */

    printf("INFO | Part 1 solution: %i\n", vector_int_sum(part_numbers));

    // Tear down
    fclose(fp);
    vector_char_destroy(&curr);
    vector_char_destroy(&next);
    vector_char_destroy(&prev);
    vector_int_destroy(&part_numbers);
    return EXIT_SUCCESS;
}
