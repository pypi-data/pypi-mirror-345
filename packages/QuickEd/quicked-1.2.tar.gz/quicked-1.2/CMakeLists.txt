cmake_minimum_required(VERSION 3.20...3.22.1)

project(quicked LANGUAGES C CXX)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 11)

if (CMAKE_SIZEOF_VOID_P EQUAL 4)
    message(FATAL_ERROR "32-bit builds are not supported. Please use 64-bit builds.")
endif()

set(WIN_CLANG FALSE)
if (CMAKE_CXX_COMPILER_ID STREQUAL "Clang" AND WIN32)
    set(WIN_CLANG TRUE)
endif()

include(CTest)
enable_testing()

# Options
option(QUICKED_NONATIVE "Compile QuickEd for generic x86_64" OFF)
option(QUICKED_FORCESCALAR "Compile QuickEd without vector extensions (SSE,AVX)" OFF)
option(ASAN "Enable ASAN and UBSAN" OFF)

# Set build type to Release if not specified
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

# Output directories
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)

foreach(OUTPUTCONFIG IN LISTS CMAKE_CONFIGURATION_TYPES)
    string(TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG_UPPER)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER} ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER} ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG_UPPER} ${CMAKE_ARCHIVE_OUTPUT_DIRECTORY})
endforeach()

# Set compiler flags if Debug build
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    message(WARNING "Build type: ${CMAKE_BUILD_TYPE}")

    if (MSVC)
        add_compile_options(/Zi /W4 /WX /analyze)
        add_compile_options(/wd4244 /wd6001 /wd6011 /wd6262 /wd6308 /wd6326 /wd6336
                            /wd6385 /wd6386 /wd6387 /wd6993 /wd28182 /wd28183) # Ignore warnings

        # Enable address sanitizer
        if (ASAN)
            message(WARNING "ASAN and Runtime Checkers enabled")
            add_compile_options(/fsanitize=address)
            add_compile_options(/RTC1 /GS) # Enable runtime checks
        endif()
    else()
        add_compile_options(-O0 -g -Wall -Wextra -Werror)

        # Ignore known non-concerning warnings
        add_compile_options("$<$<COMPILE_LANGUAGE:C>:-Wno-override-init>")
        add_compile_options(-Wno-error=cpp) # #warning are not errors
        add_compile_options(-Wno-unused-command-line-argument) # All flags have a reason to be there, even if unused

        # Enable code coverage
        add_compile_options(--coverage)
        add_link_options(--coverage)

        # Extra debug flags
        add_compile_options(-Wfloat-equal -Wformat=2 -Wshift-overflow -Wdouble-promotion -Wunused-macros
                            -Wwrite-strings -Wswitch-default -Wcast-qual -Wswitch-enum -Wpointer-arith)

        add_compile_options("$<$<C_COMPILER_ID:GNU>:-Wduplicated-branches;-Wduplicated-cond;-Wlogical-op>")

        add_compile_options("$<$<COMPILE_LANGUAGE:C>:-Wstrict-prototypes>")
        #add_compile_options(-Wconversion) # TODO: We would like to enable this, but it's too noisy for now

        # Enable address sanitizer
        if (ASAN)
            message(WARNING "ASAN and UBSAN enabled")
            add_compile_options(-fsanitize=address -fsanitize=undefined -fno-omit-frame-pointer)
            add_link_options(-fsanitize=address -fsanitize=undefined)
        endif()

        # Enable stack protection
        add_compile_options(-fstack-protector)

        # Add runtime checkers
        add_compile_definitions(_FORTIFY_SOURCE=1)
    endif()

elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_SUPPRESS_DEVELOPER_WARNINGS ON CACHE INTERNAL "" FORCE) # Suppress CMake developer warnings

    # Enable IPO/LTO if supported
    if (NOT MINGW)
        include(CheckIPOSupported)
        check_ipo_supported(RESULT result OUTPUT output)
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ${result})
        if (NOT result)
            message(WARNING "IPO/LTO is not supported: ${output}")
        endif()
    else()
        message(WARNING "IPO/LTO has some rough edges on MinGW. It is disabled by default.")
    endif()

    if (MSVC)
        add_compile_options(/O2 /Ot /Oi)
        if (NOT WIN_CLANG)
            add_compile_options(/GL)
        else()
            # add_link_options(/LTCG)
        endif()
    else()
        add_compile_options(-O3)
    endif()
endif()

# Set global compiler flags
if (NOT (WIN_CLANG OR MSVC))
    add_compile_options(-fPIC) # PIC works on Linux (GCC and Clang), and Windows (GCC). Does not work on MSVC or Clang on Windows.
endif()

if (WIN_CLANG)
    add_compile_options(-Wno-initializer-overrides -Wno-format-nonliteral) # False positive
endif()

if (WIN32)
    add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
endif()

if (NOT QUICKED_NONATIVE)
    if (MSVC)
        message(WARNING "MSVC lacks '-march=native'. Set flags manually for optimal SSE4.2 and AVX2 performance.")
        # add_compile_options(/arch:SSE4.2 /arch:AVX2) # Suggested flags if supported
        # add_compile_definitions(USE_SSE) # If you enable /arch:SSE4.2, uncomment this line
    else()
        add_compile_options(-march=native)
    endif()
else()
    if (MSVC)
        if (NOT QUICKED_FORCESCALAR)
            add_compile_options(/arch:SSE4.2 /arch:AVX2) # Strictly speaking, it should be SSE4.1. But MSVC lacks this flag.
            add_compile_definitions(USE_SSE) # MSVC do not define the macro when using /arch:SSE4.2
        else()
            add_compile_options(/arch:SSE2) # Forcefully disable SSE4.1 and AVX2 (SSE2 is the minimum supported by MSVC)
        endif()
    else()
        if(NOT (CMAKE_SYSTEM_NAME STREQUAL "Darwin" AND CMAKE_APPLE_SILICON_PROCESSOR STREQUAL "arm64"))
            add_compile_options(-march=x86-64)
        endif()
        if (NOT QUICKED_FORCESCALAR)
            add_compile_options(-msse4.1 -mavx2)
        endif()
    endif()
endif()

include_directories(${PROJECT_SOURCE_DIR})
include_directories(${PROJECT_SOURCE_DIR}/quicked_utils/include) # To implcitly #include .h inside quicked_utils/src

add_subdirectory(quicked)
add_subdirectory(bindings)
add_subdirectory(examples)
add_subdirectory(tests)
add_subdirectory(tools)