#include "stdio.h" // printf, FILE, fopen, fgets, fclose
#include "stdbool.h" // bool, true, false
#include "ctype.h" // isdigit
#include "string.h" // strncmp
#include <stdlib.h> // free

// Constants
enum {
    LINE_LEN_MAX = 256,
};

////////////////////////////////////////////////////////////////////////////////
// headers

int parse_calibration_value(char*);
int parse_digit_prefix(char*);
int parse_digit_char_prefix(char);
int to_digit(char);
int parse_digit_str_prefix(char*);

const int NO_DIGIT_PARSED = -1;

////////////////////////////////////////////////////////////////////////////////
typedef struct {
    bool none;
    char* input_path;
} optionalArgs;
static const optionalArgs NO_ARGS = {
    .none = true,
    .input_path = NULL,
};
optionalArgs parse_argv(int argc, char* argv[]) {
    if (argc != 2) {
        printf("ERROR | Expected one input file. Got %d\n", argc-1);
        return NO_ARGS;
    }
    optionalArgs args = {
        .none = false,
        .input_path = argv[1],
    };
    return args;
}

int main(int argc, char* argv[]) {
    ////////////////////////////////////////////////////////////////////////////
    // Setup
    optionalArgs args = parse_argv(argc, argv);
    if (args.none) {
        return 1;
    }
    /* printf("DEBUG | Reading from file: %s\n", args.input_path); */

    FILE *fp = fopen(args.input_path, "r");
    if (!fp) {
        printf("ERROR | Unable to open file: %s\n", args.input_path);
        return 1;
    }

    ////////////////////////////////////////////////////////////////////////////
    // Main computations
    int sum = 0;
    char *line = NULL;
    size_t line_cap = 0;
    ssize_t line_len;
    while((line_len = getline(&line, &line_cap, fp)) > 0) {
        // TODO: Handle empty lines in input fp
        int calibration_val = parse_calibration_value(line);
        /* printf("DEBUG | %d <- %s", calibration_val, line); */
        sum = sum + calibration_val;
    }
    printf("INFO | sum = %d\n", sum);

    ////////////////////////////////////////////////////////////////////////////
    // Tear down
    fclose(fp);
    if (line != NULL) {
        free(line);
    }

    return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Implementations
int parse_calibration_value(char* line) {
    int first_digit = NO_DIGIT_PARSED;
    int second_digit = NO_DIGIT_PARSED;
    size_t i = 0;
    while (line[i] != '\n') {
        /* printf("DEBUG | line[%zu] = %c\n", i, line[i]); */
        int digit = parse_digit_prefix(line + i);
        i++;
        if (digit == NO_DIGIT_PARSED) {
            continue;
        }
        if (first_digit == NO_DIGIT_PARSED) {
            first_digit = digit;
        }
        second_digit = digit;
    }
    // TODO: Handle case where no calibration value is found
    return 10*first_digit + second_digit;
}

int parse_digit_prefix(char str[]) {
    int digit;
    digit = parse_digit_char_prefix(str[0]);
    if (digit != NO_DIGIT_PARSED) {
        return digit;
    }
    digit = parse_digit_str_prefix(str);
    if (digit != NO_DIGIT_PARSED) {
        return digit;
    }
    return NO_DIGIT_PARSED;
}
int parse_digit_char_prefix(char c) {
    if (!isdigit(c)){
        return NO_DIGIT_PARSED;
    }
    return to_digit(c);
}

inline int to_digit(char c){
    return c - '0';
}
static const char* DIGIT_STRINGS[] = {
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
};
static const int N_DIGITS = sizeof(DIGIT_STRINGS) / sizeof(DIGIT_STRINGS[0]);
// TODO: Make this more efficient with a Trie
int parse_digit_str_prefix(char str[]){
    /* printf("DEBUG | Checking for digit string in %s", str); */
    for (size_t digit = 0; digit < N_DIGITS; digit++) {
        /* printf("DEBUG | Checking for digit string %zu %s\n", digit, DIGIT_STRINGS[digit]); */
        if (strncmp(str, DIGIT_STRINGS[digit], strlen(DIGIT_STRINGS[digit])) == 0) {
            /* printf("DEBUG | Matched digit string %zu %s\n", digit, DIGIT_STRINGS[digit]); */
            return digit; 
        }
    }
    return NO_DIGIT_PARSED;
}
