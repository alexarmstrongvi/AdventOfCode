include(CheckCXXCompilerFlag)

# Feature flags
set(USING_CLANG FALSE)
set(USING_GNU   FALSE)
set(USING_MSVC  FALSE)

set(SUPPORTS_UBSAN OFF)
set(SUPPORTS_ASAN OFF)
set(SUPPORTS_LSAN OFF)

macro(myproject_detect_system_features)
    ############################################################################
    # Compiler ID
    ############################################################################
    if(CMAKE_CXX_COMPILER_ID MATCHES ".*Clang")
        set(USING_CLANG TRUE)
    elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        set(USING_GNU TRUE)
    elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        set(USING_MSVC TRUE)
    endif()
    if(USING_CLANG OR USING_GNU)
        set(USING_GCC_LIKE TRUE)
    endif()

    ############################################################################
    # Sanitizers
    ############################################################################
    set(TEST_PROGRAM "int main() { return 0; }")
    if(USING_GCC_LIKE AND NOT WIN32)
        message(STATUS "Sanity checking UndefinedBehaviorSanitizer, it should be supported on this platform")
        set(CMAKE_REQUIRED_FLAGS "-fsanitize=undefined")
        set(CMAKE_REQUIRED_LINK_OPTIONS "-fsanitize=undefined")
        check_cxx_source_compiles("${TEST_PROGRAM}" HAS_UBSAN_LINK_SUPPORT)
        if(HAS_UBSAN_LINK_SUPPORT)
            set(SUPPORTS_UBSAN ON)
        endif()
    endif()
    if (USING_MSVC)
        set(SUPPORTS_ASAN ON)
    elseif (USING_GCC_LIKE)
        message(STATUS "Sanity checking AddressSanitizer, it should be supported on this platform")
        # Check if AddressSanitizer works at link time
        set(CMAKE_REQUIRED_FLAGS "-fsanitize=address")
        set(CMAKE_REQUIRED_LINK_OPTIONS "-fsanitize=address")
        check_cxx_source_compiles("${TEST_PROGRAM}" HAS_ASAN_LINK_SUPPORT)
        if(HAS_ASAN_LINK_SUPPORT)
            set(SUPPORTS_ASAN ON)
        endif()
    endif()
    if(USING_GCC_LIKE AND NOT WIN32)
        message(STATUS "Sanity checking LeakSanitizer, it should be supported on this platform")
        set(CMAKE_REQUIRED_FLAGS "-fsanitize=leak")
        set(CMAKE_REQUIRED_LINK_OPTIONS "-fsanitize=leak")
        check_cxx_source_compiles("${TEST_PROGRAM}" HAS_LSAN_LINK_SUPPORT)
        if(HAS_LSAN_LINK_SUPPORT)
            set(SUPPORTS_LSAN ON)
        endif()
    endif()
endmacro()

macro(myproject_set_SANITIZER_OPTIONS)
    set(myproject_SANITIZER_OPTIONS "")

    set(SANITIZERS "")
    if(USING_GCC_LIKE)
        if(myproject_ENABLE_SANITIZER_ADDRESS)
            list(APPEND SANITIZERS "address")
        endif()

        if(myproject_ENABLE_SANITIZER_LEAK)
            list(APPEND SANITIZERS "leak")
        endif()

        if(myproject_ENABLE_SANITIZER_UNDEFINED)
            list(APPEND SANITIZERS "undefined")
        endif()

        if(myproject_ENABLE_SANITIZER_THREAD)
            if("address" IN_LIST SANITIZERS OR "leak" IN_LIST SANITIZERS)
                message(WARNING "Thread sanitizer does not work with Address and Leak sanitizer enabled")
            else()
                list(APPEND SANITIZERS "thread")
            endif()
        endif()

        if(myproject_ENABLE_SANITIZER_MEMORY AND USING_CLANG)
            message(
                WARNING
                "Memory sanitizer requires all the code (including libc++) to be MSan-instrumented otherwise it reports false positives"
            )
            if(
                   "address" IN_LIST SANITIZERS
                OR "thread"  IN_LIST SANITIZERS
                OR "leak"    IN_LIST SANITIZERS
            )
                message(WARNING "Memory sanitizer does not work with Address, Thread or Leak sanitizer enabled")
            else()
                list(APPEND SANITIZERS "memory")
            endif()
        endif()
    elseif(MSVC)
        if(myproject_ENABLE_SANITIZER_ADDRESS)
            list(APPEND SANITIZERS "address")
        endif()
        if(
               myproject_ENABLE_SANITIZER_LEAK
            OR myproject_ENABLE_SANITIZER_UNDEFINED_BEHAVIOR
            OR myproject_ENABLE_SANITIZER_THREAD
            OR myproject_ENABLE_SANITIZER_MEMORY
        )
            message(WARNING "MSVC only supports address sanitizer")
        endif()
    endif()
    list(JOIN SANITIZERS "," LIST_OF_SANITIZERS)
    message(STATUS "Sanitizers: ${LIST_OF_SANITIZERS}")

    if(USING_GCC_LIKE)
        set(myproject_SANITIZER_OPTIONS 
            "-fsanitize=${LIST_OF_SANITIZERS}"
        )
    elseif(USING_MSVC)
        set(myproject_SANITIZER_OPTIONS 
            "/fsanitize=${LIST_OF_SANITIZERS} /Zi /INCREMENTAL:NO"
        )
    endif()
endmacro()
