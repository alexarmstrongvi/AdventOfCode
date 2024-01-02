#ifndef MY_UTILS_H
#define MY_UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

////////////////////////////////////////////////////////////////////////////////
#define FREE(x) do {free(x); (x) = NULL;} while (0)
#define UNUSED_PARAMETER(x) ((void)(x))

#define _STR(x) #x
#define STR(x) _STR(x)
#define _CONCAT(x,y) x##y
#define CONCAT(x,y) _CONCAT(x,y)

////////////////////////////////////////////////////////////////////////////////
// Dynamic array
// TODO: Handle failures to allocate or reallocate memory
typedef enum {
    ALLOC_SUCCESS,
    ALLOC_FAILURE,
} AllocStatus;

#define DECLARE_VECTOR(T, VEC, FUNC) \
typedef struct { \
    T *data; \
    size_t size; \
    size_t capacity; \
} VEC; \
VEC * CONCAT(FUNC,_new)(size_t capacity); \
VEC CONCAT(FUNC,_construct)(size_t capacity); \
void CONCAT(FUNC,_destroy)(VEC *this); \
/* Clear vector while retaining reference to data array */ \
void CONCAT(FUNC,_clear)(VEC *this); \
/* Reset vector, setting array pointer to NULL */ \
void CONCAT(FUNC,_nullify)(VEC *this); \
AllocStatus CONCAT(FUNC,_init)(VEC *this, size_t capacity); \
AllocStatus CONCAT(FUNC,_resize)(VEC *this); \
AllocStatus CONCAT(FUNC,_push_back)(VEC *this, T entry); \
AllocStatus CONCAT(FUNC,_extend)(VEC *this, const VEC *vec);

int sign(int n);
int ceil_power_of_2(int n);

////////////////////////////////////////
/* Dynamic array methods but leave destroy and clear to be
 * defined later in case element type requires its own destructor*/
#define _DEFINE_VECTOR_GENERIC(T, VEC, FUNC) \
VEC * CONCAT(FUNC,_new)(size_t capacity) { \
    VEC *vec = calloc(1, sizeof(VEC)); \
    CONCAT(FUNC,_init)(vec, capacity); \
    return vec; \
} \
VEC CONCAT(FUNC,_construct)(size_t capacity) { \
    VEC vec; \
    CONCAT(FUNC,_init)(&vec, capacity); \
    return vec; \
} \
AllocStatus CONCAT(FUNC,_init)(VEC *this, size_t capacity) { \
    CONCAT(FUNC,_nullify)(this); \
    if (capacity > 0) { \
        this->data = (T *) calloc(capacity, sizeof(T)); \
        this->capacity = capacity; \
        if (this->data == NULL) { \
            printf("WARNING | Failed to allocate memory for "STR(VEC)"\n"); \
            return ALLOC_FAILURE; \
        } \
    } \
    return ALLOC_SUCCESS; \
} \
void CONCAT(FUNC,_nullify)(VEC *this) { \
    this->data     = NULL; \
    this->capacity = 0; \
    this->size     = 0; \
} \
AllocStatus CONCAT(FUNC,_resize)(VEC *this) { \
    size_t capacity = (size_t) ceil_power_of_2(this->capacity); \
    T * new_data = realloc(this->data, capacity * sizeof(T)); \
    if (new_data == NULL) { \
        printf("WARNING | Failed to reallocate memory for "STR(VEC)"\n"); \
        return ALLOC_FAILURE; \
    } \
    this->data = new_data; \
    this->capacity = capacity; \
    return ALLOC_SUCCESS; \
} \
AllocStatus CONCAT(FUNC,_push_back)(VEC *this, T entry) { \
    if (this->size == this->capacity) { \
        int status = CONCAT(FUNC,_resize)(this); \
        if (status == ALLOC_FAILURE) { \
            return ALLOC_FAILURE; \
        } \
    } \
    this->data[this->size] = entry; \
    this->size += 1; \
    return ALLOC_SUCCESS; \
} \
AllocStatus CONCAT(FUNC,_extend)(VEC *this, const VEC *vec) { \
    for (size_t i = 0; i < vec->size; i++) { \
        int status = CONCAT(FUNC,_push_back)(this, vec->data[i]); \
        if (status == ALLOC_FAILURE) { \
            return ALLOC_FAILURE; \
        } \
    } \
    return ALLOC_SUCCESS; \
}


#define DEFINE_VECTOR(T, VEC, FUNC) \
_DEFINE_VECTOR_GENERIC(T, VEC, FUNC) \
void CONCAT(FUNC,_destroy)(VEC *this) { \
    FREE(this->data); \
    CONCAT(FUNC,_nullify)(this); \
} \
void CONCAT(FUNC,_clear)(VEC *this) { \
    this->data = memset(this->data, 0, this->size * sizeof(T)); \
    this->size = 0; \
}

#define DEFINE_VECTOR_USERTYPE(T, T_FUNC, VEC, VEC_FUNC) \
_DEFINE_VECTOR_GENERIC(T, VEC, VEC_FUNC)
/* user must define destroy and clear */

////////////////////////////////////////////////////////////////////////////////
DECLARE_VECTOR(char, vector_char_t, vector_char)
DECLARE_VECTOR(int, vector_int_t, vector_int)

int vector_int_sum(const vector_int_t *vec);
vector_char_t * vector_int_to_str(const vector_int_t *vec);

#endif
