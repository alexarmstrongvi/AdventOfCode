#include "stdio.h" // printf, FILE, fopen, fgets, fclose
#include "string.h" // strcmp
#include "ctype.h" // isdigit
#include "stdbool.h" // bool, true, false

// Constants
static const int LINE_LEN_MAX = 256;

////////////////////////////////////////////////////////////////////////////////
// headers
typedef struct {
    bool none;
    int val;
} optionalDigit;

const optionalDigit NO_DIGIT = {
    .none = true,
    .val  = -1,
};

int parse_calibration_value(char*);
optionalDigit parse_digit_prefix(char*);
optionalDigit parse_digit_char_prefix(char);
int to_digit(char);
optionalDigit parse_digit_str_prefix(char*);

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

    FILE *file = fopen(args.input_path, "r");
    if (!file) {
        printf("ERROR | Unable to open file: %s\n", args.input_path);
        return 1;
    }
    
    //////////////////////////////////////////////////////////////////////////// 
    // Main computations
    int sum = 0;
    char line[LINE_LEN_MAX];
    while (fgets(line, sizeof(line), file) != NULL) {
        // TODO: Handle empty lines in input file
        int calibration_val = parse_calibration_value(line);
        /* printf("DEBUG | %d <- %s", calibration_val, line); */        
        sum = sum + calibration_val;
    }
    printf("INFO | sum = %d\n", sum);
    
    //////////////////////////////////////////////////////////////////////////// 
    // Tear down
    fclose(file);

    return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Implementations
int parse_calibration_value(char line[]) {
    bool first_digit_unset = true;
    int first_digit = -1;
    int second_digit = -1;
    size_t i = 0;
    while (line[i] != '\n') {
        /* printf("DEBUG | line[%zu] = %c\n", i, line[i]); */
        optionalDigit digit = parse_digit_prefix(line + i);
        i++;
        if (digit.none) {
            continue;
        }
        if (first_digit_unset) {
            first_digit_unset = false;
            first_digit = digit.val;
        }
        second_digit = digit.val;
    }
    // TODO: Handle case where no calibration value is found
    return 10*first_digit + second_digit;
}

optionalDigit parse_digit_prefix(char str[]) {
    optionalDigit digit; 
    digit = parse_digit_char_prefix(str[0]);
    if (!digit.none) {
        return digit;
    }
    digit = parse_digit_str_prefix(str);
    if (!digit.none) {
        return digit;
    }
    return NO_DIGIT;
}
optionalDigit parse_digit_char_prefix(char c) {
    if (!isdigit(c)){
        return NO_DIGIT;
    }
    optionalDigit digit = {
        .none = false,
        .val    = to_digit(c),
    };
    return digit;
}

inline int to_digit(char c){
    return c - '0';
}
const int N_DIGITS = 10;
const int MAX_LEN_DIGIT_STR = 6;
const char digit_strings[N_DIGITS][MAX_LEN_DIGIT_STR] = {
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
// TODO: Make this more efficient with a Trie
optionalDigit parse_digit_str_prefix(char str[]){
    /* printf("DEBUG | Checking for digit string in %s", str); */
    for (size_t i = 0; i < N_DIGITS; i++) {
        /* printf("DEBUG | Checking for digit string %zu %s\n", i, digit_strings[i]); */
        if (strncmp(str, digit_strings[i], strlen(digit_strings[i])) == 0) {
            /* printf("DEBUG | Matched digit string %zu %s\n", i, digit_strings[i]); */
            optionalDigit digit = {
                .none = false,
                .val    = i,
            };
            return digit;
        }
    }
    return NO_DIGIT;
}
