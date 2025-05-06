# QuickEd library
add_library(quicked STATIC)

# Include directories
target_include_directories(quicked PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include) # Library includes
target_include_directories(quicked PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}) # Library root
if(NOT (WIN_CLANG OR MSVC))
    target_link_libraries(quicked PUBLIC m) # Link math library
endif()

# Sources
file(GLOB QUICKED_SRCS
    "${CMAKE_CURRENT_SOURCE_DIR}/src/*.c"
)
file(GLOB UTILS_SRCS
    "${PROJECT_SOURCE_DIR}/quicked_utils/src/commons.c"
    "${PROJECT_SOURCE_DIR}/quicked_utils/src/mm_allocator.c"
    "${PROJECT_SOURCE_DIR}/quicked_utils/src/profiler_timer.c"
    "${PROJECT_SOURCE_DIR}/quicked_utils/src/profiler_counter.c"
    "${PROJECT_SOURCE_DIR}/quicked_utils/src/vector.c"
    "${PROJECT_SOURCE_DIR}/quicked_utils/src/dna_text.c"
    "${PROJECT_SOURCE_DIR}/quicked_utils/src/cigar.c"
)
target_sources(quicked PRIVATE ${QUICKED_SRCS} ${UTILS_SRCS}) # Add sources to target

# Install
install(TARGETS quicked DESTINATION lib COMPONENT quicked)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/quicked.h DESTINATION include COMPONENT quicked)
install(FILES
    ${PROJECT_SOURCE_DIR}/quicked_utils/include/commons.h
    ${PROJECT_SOURCE_DIR}/quicked_utils/include/mm_allocator.h
    ${PROJECT_SOURCE_DIR}/quicked_utils/include/profiler_timer.h
    ${PROJECT_SOURCE_DIR}/quicked_utils/include/profiler_counter.h
    ${PROJECT_SOURCE_DIR}/quicked_utils/include/vector.h
    DESTINATION include/quicked_utils/include
    COMPONENT quicked
)

# Shim targets for building the Python bindings
add_library(quicked_scalar OBJECT ${QUICKED_SRCS} ${UTILS_SRCS})
target_include_directories(quicked_scalar PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include) # Library includes
target_include_directories(quicked_scalar PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}) # Library root
if(NOT (WIN_CLANG OR MSVC))
    target_link_libraries(quicked_scalar PUBLIC m) # Link math library
endif()
if (NOT MSVC)
    target_compile_options(quicked_scalar PRIVATE -mno-sse4.1 -mno-avx2) # Disable SSE4.1 and AVX2 for the scalar Python binding
else()
    target_compile_options(quicked_scalar PRIVATE /arch:SSE2) # Disable SSE4.1 and AVX2 for the scalar Python binding (SSE2 is the minimum supported by MSVC)
endif()
set_target_properties(quicked_scalar PROPERTIES EXCLUDE_FROM_ALL TRUE)


add_library(quicked_simd OBJECT ${QUICKED_SRCS} ${UTILS_SRCS})
target_include_directories(quicked_simd PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include) # Library includes
target_include_directories(quicked_simd PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}) # Library root
if(NOT (WIN_CLANG OR MSVC))
    target_link_libraries(quicked_simd PUBLIC m) # Link math library
endif()
if (NOT MSVC)
    target_compile_options(quicked_simd PRIVATE -msse4.1 -mavx2) # Enable SSE4.1 and AVX2 for the SIMD Python binding
else()
    target_compile_options(quicked_simd PRIVATE /arch:AVX) # Enable SSE4.1 and AVX2 for the SIMD Python binding
endif()
set_target_properties(quicked_simd PROPERTIES EXCLUDE_FROM_ALL TRUE)