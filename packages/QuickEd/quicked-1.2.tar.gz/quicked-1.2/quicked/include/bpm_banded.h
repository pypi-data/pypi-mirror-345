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

#ifndef BPM_BANDED_H_
#define BPM_BANDED_H_

#include "quicked_utils/include/commons.h"
#include "quicked_utils/include/mm_allocator.h"
#include "quicked_utils/include/cigar.h"

typedef struct {
    /* BMP Pattern */
    const char *pattern;           // Raw pattern
    uint64_t *PEQ;                // Pattern equalities (Bit vector for Myers-DP)
    uint64_t pattern_length;      // Length
    uint64_t pattern_num_words64; // ceil(Length / |w|)
    uint64_t pattern_mod;         // Length % |w|
    /* BPM Auxiliary data */
    uint64_t *P;
    uint64_t *M;
    uint64_t *level_mask;
} banded_pattern_t;

typedef struct {
    // Bit-encoded Matrix
    uint64_t *Pv;
    uint64_t *Mv;
    int64_t *scores;
    // Lower and upper bounds
    uint64_t effective_bandwidth_blocks;
    uint64_t effective_bandwidth;
    int64_t cutoff_score;
    int64_t sequence_length_diff;
    int64_t relative_cutoff_score;
    int64_t prolog_column_blocks;
    int *lo;
    int *hi;
    uint64_t higher_block;
    uint64_t lower_block;
    // CIGAR
    cigar_t *cigar;
} banded_matrix_t;

void banded_pattern_compile(
    banded_pattern_t *const banded_pattern,
    const char* pattern,
    const uint64_t pattern_length,
    mm_allocator_t *const mm_allocator);

void banded_pattern_free(
    banded_pattern_t *const banded_pattern,
    mm_allocator_t *const mm_allocator);

void banded_matrix_allocate(
    banded_matrix_t *const banded_matrix,
    const int64_t pattern_length,
    const int64_t text_length,
    const int64_t cutoff_score,
    bool only_score,
    mm_allocator_t *const mm_allocator);

void banded_matrix_free(
    banded_matrix_t *const banded_matrix,
    mm_allocator_t *const mm_allocator);

void banded_compute(
    banded_matrix_t *const banded_matrix,
    banded_pattern_t *const banded_pattern,
    const char* text,
    const int64_t text_length,
    const int64_t text_finish_pos,
    const bool only_score,
    const bool force_scalar);

#endif /* BPM_BANDED_H_ */
