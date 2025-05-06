# Tests for the QuickEd Library
add_custom_target(tests)

# Compile the test harness
add_executable(quicked_harness quicked_harness.c)
target_link_libraries(quicked_harness quicked)
add_dependencies(tests quicked_harness)

# Add the tests
add_test(NAME test_empty COMMAND $<TARGET_FILE:quicked_harness> "" "")
set_tests_properties(test_empty PROPERTIES PASS_REGULAR_EXPRESSION "ERROR: Tried to align an empty sequence")

add_test(NAME test_nonDNA COMMAND $<TARGET_FILE:quicked_harness> "GATC" "GATO" 1)

if(UNIX)
    set(RANDOM_TEST_SCRIPT ${CMAKE_CURRENT_SOURCE_DIR}/random_test.sh)

    add_test(NAME test_l1000_n10000_e10 COMMAND ${RANDOM_TEST_SCRIPT} 1000 10000 10 quicked_harness)
    set_tests_properties(test_l1000_n10000_e10 PROPERTIES
        ENVIRONMENT "BIN_DIR=${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")

    add_test(NAME test_l10000_n1000_e10 COMMAND ${RANDOM_TEST_SCRIPT} 10000 1000 10 quicked_harness)
    set_tests_properties(test_l10000_n1000_e10 PROPERTIES
        ENVIRONMENT "BIN_DIR=${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")

    add_test(NAME test_l100000_n100_e10 COMMAND ${RANDOM_TEST_SCRIPT} 100000 100 10 align_benchmark)
    set_tests_properties(test_l100000_n100_e10 PROPERTIES
        ENVIRONMENT "BIN_DIR=${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")

    add_test(NAME test_l1000000_n10_e10 COMMAND ${RANDOM_TEST_SCRIPT} 1000000 10 10 align_benchmark)
    set_tests_properties(test_l1000000_n10_e10 PROPERTIES FAIL_REGULAR_EXPRESSION "INACCURATE SCORE")
    set_tests_properties(test_l1000000_n10_e10 PROPERTIES
        ENVIRONMENT "BIN_DIR=${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
endif()

add_test(NAME test_MiniION_align_benchmark COMMAND $<TARGET_FILE:align_benchmark> -i ${CMAKE_CURRENT_SOURCE_DIR}/test_data/ONT.MiniION.1.seq -c "score" -v)
set_tests_properties(test_MiniION_align_benchmark PROPERTIES FAIL_REGULAR_EXPRESSION "INACCURATE SCORE")