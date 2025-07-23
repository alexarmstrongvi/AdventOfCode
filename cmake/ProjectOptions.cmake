
include(cmake/SystemFeatureChecks.cmake)
myproject_detect_system_features()

################################################################################
# Manually set options
################################################################################
# sanitizer combinations
# - address,leak,undefined (address implies leak on Linux/MacOS)
# - memory,undefined
# - thread,undefined
option(myproject_ENABLE_IPO "Enable IPO/LTO" ON)
option(myproject_WARNINGS_AS_ERRORS "Treat Warnings As Errors" OFF)
option(myproject_ENABLE_USER_LINKER "Enable user-selected linker" OFF)
option(myproject_ENABLE_SANITIZER_ADDRESS "Enable address sanitizer" ${SUPPORTS_ASAN})
option(myproject_ENABLE_SANITIZER_LEAK "Enable leak sanitizer" ${SUPPORTS_LSAN})
option(myproject_ENABLE_SANITIZER_UNDEFINED "Enable undefined sanitizer" ${SUPPORTS_UBSAN})
option(myproject_ENABLE_SANITIZER_THREAD "Enable thread sanitizer" OFF)
option(myproject_ENABLE_SANITIZER_MEMORY "Enable memory sanitizer" OFF)
option(myproject_ENABLE_UNITY_BUILD "Enable unity builds" OFF)
option(myproject_ENABLE_CLANG_TIDY "Enable clang-tidy" ON)
option(myproject_ENABLE_CPPCHECK "Enable cpp-check analysis" ON)
option(myproject_ENABLE_PCH "Enable precompiled headers" OFF)
option(myproject_ENABLE_CACHE "Enable ccache" ON)


# Generate compile_commands.json to make it easier to work with clang based tools
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

################################################################################
# Compiler Options
################################################################################
myproject_set_SANITIZER_OPTIONS()

set(myproject_COMPILE_OPTIONS ${myproject_SANITIZER_OPTIONS})
set(myproject_LINK_OPTIONS ${myproject_COMPILE_OPTIONS})

################################################################################
# WARNINGS
################################################################################

# Warnings depend on
# * Compiler ID: MSVC, Clang, GNU, etc
# * Language: C++, C, Cuda
# * Warnings as errors
# * Build vs Install


set(WARNINGS_CLANG 
    -Weverything
    # Not trying to cross-compile
    # "include location '/usr/local/include' is unsafe for cross-compilation"
    -Wno-poison-system-directories
    # Not trying to be backwards compatible with C++98
    -Wno-c++98-compat
    # Not trying to optimize memory layout to this extent
    # "padding B with N bytes to align C"
    -Wno-padded
)

set(WARNINGS_GNU
    # GCC and Clang options
    -Wall
    -Wextra # reasonable and standard
    -Wshadow # warn the user if a variable declaration shadows one from a parent context
    -Wnon-virtual-dtor # warn the user if a class with virtual functions has a non-virtual destructor. This helps catch hard to track down memory errors
    -Wold-style-cast # warn for c-style casts
    -Wcast-align # warn for potential performance problem casts
    -Wunused # warn on anything being unused
    -Woverloaded-virtual # warn if you overload (not override) a virtual function
    -Wpedantic # warn if non-standard C++ is used
    -Wconversion # warn on type conversions that may lose data
    -Wsign-conversion # warn on sign conversions
    -Wnull-dereference # warn if a null dereference is detected
    -Wdouble-promotion # warn if float is implicit promoted to double
    -Wformat=2 # warn on security issues around functions that format output (ie printf)
    -Wimplicit-fallthrough # warn on statements that fallthrough without an explicit annotation
    # GCC only
    -Wmisleading-indentation # warn if indentation implies blocks where blocks do not exist
    -Wduplicated-cond # warn if if / else chain has duplicated conditions
    -Wduplicated-branches # warn if if / else branches have duplicated code
    -Wlogical-op # warn about logical operations being used where bitwise were probably wanted
    -Wuseless-cast # warn if you perform a cast to the same type
    -Wsuggest-override # warn if an overridden member function is not marked 'override' or 'final'
)
set(WARNINGS_MSVC
    /W4 # Baseline reasonable warnings
    /w14242 # 'identifier': conversion from 'type1' to 'type2', possible loss of data
    /w14254 # 'operator': conversion from 'type1:field_bits' to 'type2:field_bits', possible loss of data
    /w14263 # 'function': member function does not override any base class virtual member function
    /w14265 # 'classname': class has virtual functions, but destructor is not virtual instances of this class may not
            # be destructed correctly
    /w14287 # 'operator': unsigned/negative constant mismatch
    /we4289 # nonstandard extension used: 'variable': loop control variable declared in the for-loop is used outside
            # the for-loop scope
    /w14296 # 'operator': expression is always 'boolean_value'
    /w14311 # 'variable': pointer truncation from 'type1' to 'type2'
    /w14545 # expression before comma evaluates to a function which is missing an argument list
    /w14546 # function call before comma missing argument list
    /w14547 # 'operator': operator before comma has no effect; expected operator with side-effect
    /w14549 # 'operator': operator before comma has no effect; did you intend 'operator'?
    /w14555 # expression has no effect; expected expression with side- effect
    /w14619 # pragma warning: there is no warning number 'number'
    /w14640 # Enable warning on thread un-safe static member initialization
    /w14826 # Conversion from 'type1' to 'type2' is sign-extended. This may cause unexpected runtime behavior.
    /w14905 # wide string literal cast to 'LPSTR'
    /w14906 # string literal cast to 'LPWSTR'
    /w14928 # illegal copy-initialization; more than one user-defined conversion has been implicitly applied
    /permissive- # standards conformance mode for MSVC compiler.
)

if (myproject_WARNINGS_AS_ERRORS)
    list(APPEND WARNINGS_CLANG -Werror)
    list(APPEND WARNINGS_GCC -Werror)
    list(APPEND WARNINGS_MSVC /WX)
endif()

if(USING_CLANG)
    set(WARNINGS_CXX ${WARNINGS_CLANG})
elseif(USING_GNU)
    set(WARNINGS_CXX ${WARNINGS_GNU})
elseif(USING_GNU)
    set(WARNINGS_CXX ${WARNINGS_GNU})
endif()

# TODO: support warnings for multiple languages
set(myproject_WARNINGS
    "$<$<COMPILE_LANGUAGE:CXX>:${WARNINGS_CXX}>"
    "$<$<COMPILE_LANGUAGE:C>:${WARNINGS_C}>"
    "$<$<COMPILE_LANGUAGE:CUDA>:${WARNINGS_CUDA}>"
)
