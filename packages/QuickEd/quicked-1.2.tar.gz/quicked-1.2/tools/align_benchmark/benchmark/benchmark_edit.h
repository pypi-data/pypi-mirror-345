/*
 *                             The MIT License
 *
 * This file is part of QuickEd library.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#ifndef BENCHMARK_EDIT_H_
#define BENCHMARK_EDIT_H_

#include "benchmark/benchmark_utils.h"

/*
 * Benchmark Edit
 */
void benchmark_banded(
    align_input_t* const align_input, 
    const int bandwidth, 
    const int only_score);

void benchmark_hirschberg(
    align_input_t* const align_input, 
    const int bandwidth);


void benchmark_quicked(
    align_input_t* const align_input, 
    const int window_size, 
    const int overlap_size, 
    const int bandwidth, 
    const int force_scalar, 
    const int hew_threshold, 
    const int hew_percentage);

void benchmark_windowed(
    align_input_t* const align_input, 
    const int window_size, 
    const int overlap_size, 
    const int force_scalar, 
    const int only_score);

void benchmark_edit_bpm(
    align_input_t* const align_input);

void benchmark_edit_dp(
    align_input_t* const align_input);
void benchmark_edit_dp_banded(
    align_input_t* const align_input,
    const int bandwidth);

// External

void benchmark_edlib(
    align_input_t* const align_input,
    const int bandwidth);

#endif /* BENCHMARK_EDIT_H_ */
