# Tools using the QuickEd Library

add_custom_target(tools)

# Generate Dataset Tool
add_executable(generate_dataset ${CMAKE_CURRENT_SOURCE_DIR}/generate_dataset/generate_dataset.c)
if(NOT (WIN_CLANG OR MSVC))
    target_link_libraries(generate_dataset PRIVATE m) # Link math library
endif()
target_sources(generate_dataset PRIVATE ${CMAKE_SOURCE_DIR}/quicked_utils/src/commons.c ${CMAKE_SOURCE_DIR}/quicked_utils/src/getopt.c)
add_dependencies(tools generate_dataset)

# Align Benchmark Tool
add_executable(align_benchmark)
target_include_directories(align_benchmark PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark)
if(NOT (WIN_CLANG OR MSVC))
    target_link_libraries(align_benchmark PRIVATE m) # Link math library
endif()
target_link_libraries(align_benchmark PRIVATE quicked)

# Add OpenMP lib
find_package(OpenMP)
if(OpenMP_FOUND)
    if(WIN_CLANG AND MSVC) # Clang with MSVC-like CLI
        target_compile_options(align_benchmark PRIVATE /openmp)
        target_link_libraries(align_benchmark PRIVATE libomp)
    else()
        if(OpenMP_CXX_FOUND)
            target_compile_options(align_benchmark PRIVATE ${OpenMP_CXX_FLAGS})
            target_link_options(align_benchmark PRIVATE ${OpenMP_CXX_FLAGS})
        endif()
        if(OpenMP_C_FOUND)
            target_compile_options(align_benchmark PRIVATE ${OpenMP_C_FLAGS})
            target_link_options(align_benchmark PRIVATE ${OpenMP_C_FLAGS})
        endif()
    endif()
endif()

add_subdirectory(align_benchmark/external/edlib EXCLUDE_FROM_ALL)
target_link_libraries(align_benchmark PRIVATE edlib)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    # For debug builds, disable the warnings, as we don't have control over Edlib
    if(MSVC)
        target_compile_options(edlib PRIVATE /w)
    else()
        target_compile_options(edlib PRIVATE -w)
    endif()
endif()

file(GLOB ALIGN_BENCH_SRCS
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/edit/edit_bpm.c
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/edit/edit_dp.c
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/benchmark/benchmark_edit.c
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/benchmark/benchmark_check.c
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/benchmark/benchmark_utils.c
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/align_benchmark_params.c
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/align_benchmark.c
    ${CMAKE_CURRENT_SOURCE_DIR}/align_benchmark/score_matrix.c)

file(GLOB UTILS_SRCS
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/commons.c
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/mm_allocator.c
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/vector.c
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/dna_text.c
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/cigar.c
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/profiler_counter.c
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/profiler_timer.c
    ${PROJECT_SOURCE_DIR}/quicked_utils/src/sequence_buffer.c
)
if(MSVC OR WIN_CLANG)
    list(APPEND UTILS_SRCS ${PROJECT_SOURCE_DIR}/quicked_utils/src/getopt.c)
endif()

target_sources(align_benchmark PRIVATE ${ALIGN_BMRK_SRCS} ${UTILS_SRCS} ${ALIGN_BENCH_SRCS})
add_dependencies(tools align_benchmark) # TODO: Uncomment when ready