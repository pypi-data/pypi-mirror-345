# Examples on how to use the QuickEd Library
add_custom_target(examples)

# Plain examples
file(GLOB FILE_LIST "${CMAKE_CURRENT_SOURCE_DIR}/*.c") # Get all .c files in this directory
foreach (FILE ${FILE_LIST})
    cmake_path(GET FILE STEM EXAMPLE) # Remove .c extension

    add_executable(${EXAMPLE} ${FILE})
    target_link_libraries(${EXAMPLE} quicked)
    set_target_properties(${EXAMPLE} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/bin/examples")

    # Add a test for each example. Although this is not proper testing, at least we can check that the example runs
    add_test(NAME test_example_${EXAMPLE} COMMAND $<TARGET_FILE:${EXAMPLE}>)
    set_tests_properties(test_example_${EXAMPLE} PROPERTIES LABELS "examples")
    add_dependencies(examples ${EXAMPLE}) # 'examples' target depends from that executable
endforeach ()

# C++ Binding Examples
file(GLOB FILE_LIST "${CMAKE_CURRENT_SOURCE_DIR}/bindings/*.cpp") # Get all *.cpp files in this directory
foreach (FILE ${FILE_LIST})
    cmake_path(GET FILE STEM EXAMPLE) # Remove .cpp extension

    add_executable(binding_${EXAMPLE}_cpp ${FILE})
    target_link_libraries(binding_${EXAMPLE}_cpp quickedcpp)
    set_target_properties(binding_${EXAMPLE}_cpp PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/bin/examples/bindings")
    target_include_directories(binding_${EXAMPLE}_cpp PRIVATE "${PROJECT_SOURCE_DIR}/bindings/cpp")

    # Add a test for each example. Although this is not proper testing, at least we can check that the example runs
    add_test(NAME test_binding_${EXAMPLE}_cpp COMMAND $<TARGET_FILE:binding_${EXAMPLE}_cpp>)
    set_tests_properties(test_binding_${EXAMPLE}_cpp PROPERTIES LABELS "examples")
    add_dependencies(examples binding_${EXAMPLE}_cpp) # 'examples' target depends from that executable
endforeach ()

# Python Binding Examples
find_package(Python3 REQUIRED COMPONENTS Interpreter)

add_test(NAME binding_install_py COMMAND ${Python3_EXECUTABLE} -m pip install --user --break-system-packages ${PROJECT_SOURCE_DIR})
set_tests_properties(binding_install_py PROPERTIES
    FIXTURES_SETUP python_setup) # Phony test to install the Python bindings

add_test(NAME test_binding_basic_py COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/bindings/basic.py)
set_tests_properties(test_binding_basic_py PROPERTIES LABELS "examples")
set_tests_properties(test_binding_basic_py PROPERTIES FIXTURES_REQUIRED python_setup)

add_test(NAME test_binding_align_benchmark_py COMMAND
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/bindings/align_benchmark.py ${PROJECT_SOURCE_DIR}/tests/test_data/ONT.MiniION.1.seq)
set_tests_properties(test_binding_align_benchmark_py PROPERTIES LABELS "examples")
set_tests_properties(test_binding_align_benchmark_py PROPERTIES PASS_REGULAR_EXPRESSION "Score: 39743")
set_tests_properties(test_binding_align_benchmark_py PROPERTIES FIXTURES_REQUIRED python_setup)