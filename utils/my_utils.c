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
