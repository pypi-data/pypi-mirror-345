# QuickEd library C++ binding
add_library(quickedcpp STATIC cpp/quicked.cpp)
target_include_directories(quickedcpp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/cpp)
target_link_libraries(quickedcpp PRIVATE quicked)

# QuickEd library Python binding (based on C++ binding)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
add_subdirectory(python/pybind11)

pybind11_add_module(pyquicked_scalar python/quicked.cpp cpp/quicked.cpp)
target_compile_definitions(pyquicked_scalar PRIVATE PY_MODULE_NAME=_quicked_scalar)
set_target_properties(pyquicked_scalar PROPERTIES OUTPUT_NAME _quicked_scalar ARCHIVE_OUTPUT_NAME pyquicked_scalar)
target_include_directories(pyquicked_scalar PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/cpp)
target_link_libraries(pyquicked_scalar PRIVATE quicked_scalar)
if (NOT MSVC)
    target_compile_options(pyquicked_scalar PRIVATE -fvisibility=hidden)
    target_compile_options(pyquicked_scalar PRIVATE -mno-sse4.1 -mno-avx2) # Disable SSE4.1 and AVX2 for the scalar Python binding
else()
    target_compile_options(pyquicked_scalar PRIVATE /arch:SSE2)  # Disable SSE4.1 and AVX2 for the scalar Python binding (SSE2 is the minimum supported by MSVC)
endif()


pybind11_add_module(pyquicked_simd python/quicked.cpp cpp/quicked.cpp)
target_compile_definitions(pyquicked_simd PRIVATE PY_MODULE_NAME=_quicked_simd)
set_target_properties(pyquicked_simd PROPERTIES OUTPUT_NAME _quicked_simd ARCHIVE_OUTPUT_NAME pyquicked_simd)
target_include_directories(pyquicked_simd PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/cpp)
target_link_libraries(pyquicked_simd PRIVATE quicked_simd)
if (NOT MSVC)
    target_compile_options(pyquicked_simd PRIVATE -fvisibility=hidden)
    target_compile_options(pyquicked_simd PRIVATE -mno-sse4.1 -mno-avx2) # Enable SSE4.1 and AVX2 for the SIMD Python binding
else()
    target_compile_options(pyquicked_simd PRIVATE /arch:AVX) # Enable SSE4.1 and AVX2 for the SIMD Python binding
endif()

add_custom_target(pyquicked ALL
    DEPENDS pyquicked_scalar pyquicked_simd
)

install(TARGETS pyquicked_scalar DESTINATION quicked/backend COMPONENT pyquicked EXCLUDE_FROM_ALL)
install(TARGETS pyquicked_simd DESTINATION quicked/backend COMPONENT pyquicked EXCLUDE_FROM_ALL)
install(FILES python/__init__.py DESTINATION quicked COMPONENT pyquicked EXCLUDE_FROM_ALL)
install(FILES python/quicked.pyi DESTINATION quicked COMPONENT pyquicked EXCLUDE_FROM_ALL)