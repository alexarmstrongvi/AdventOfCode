// Local
#include "my_utils.h"

// Standard library
#include <math.h>
#include <string.h>
#include <stdlib.h>

////////////////////////////////////////////////////////////////////////////////
int sign(int n) {
    return (n > 0) - (n < 0);
}
/* Round up (away from zero) to nearest power of 2, preserving sign */
int ceil_power_of_2(int n) {
    if (n == 0) {
        return 2;
    }
    return pow(2, floor(log2(abs(n)))+1) * sign(n);
}

DEFINE_VECTOR(char, vector_char_t, vector_char)
DEFINE_VECTOR(int, vector_int_t, vector_int)


int vector_int_sum(const vector_int_t *vec) {
    int sum = 0;
    for (size_t i = 0; i < vec->size; i++) {
        sum += vec->data[i];
    }
    return sum;
}

enum {
    INT_MAX_CHARS = 1+10+1 // "-" + "2147483648" + "\0"
};
vector_char_t * vector_int_to_str(const vector_int_t *vec) {
    size_t capacity = vec->size > 0 ? vec->size * 3 - 1 : 3;
    vector_char_t *str = vector_char_new(capacity);
    vector_char_push_back(str, '[');
    for (size_t i = 0; i < vec->size; i++) {
        char int_str[INT_MAX_CHARS];
        sprintf(int_str, "%i", vec->data[i]);

        char *p = int_str;
        for (char c = *p; c != '\0'; c = *++p) {
            vector_char_push_back(str, c);
        }

        if (i < vec->size -1) {
            vector_char_push_back(str, ',');
            vector_char_push_back(str, ' ');
        }
    }
    vector_char_push_back(str, ']');
    return str;
}
