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

#ifndef CIGAR_H_
#define CIGAR_H_

#include "quicked_utils/include/mm_allocator.h"

/*
 * CIGAR
 */
typedef struct {
  // Alignment operations
  char* operations;        // Raw alignment operations
  // CIGAR (SAM compliant)
  uint32_t* cigar_buffer;  // CIGAR-operations (max_operations length)
  int cigar_length;        // Total CIGAR-operations
  int max_operations;      // Maximum buffer size
  int begin_offset;        // Begin offset
  int end_offset;          // End offset
  // Score and end position (useful for partial alignments like Z-dropped)
  int score;               // Computed scored
  int end_v;               // Alignment-end vertical coordinate (pattern characters aligned)
  int end_h;               // Alignment-end horizontal coordinate (text characters aligned)
} cigar_t;

/*
 * Setup
 */
cigar_t* cigar_new(
    const int max_operations,
    mm_allocator_t *const mm_allocator);
void cigar_clear(
    cigar_t* const cigar);
void cigar_resize(
    cigar_t* const cigar,
    const int max_operations,
    mm_allocator_t *const mm_allocator);
void cigar_free(
    cigar_t* const cigar,
    mm_allocator_t *const mm_allocator);

/*
 * Accessors
 */
bool cigar_is_null(
    cigar_t* const cigar);

int cigar_count_matches(
    cigar_t* const cigar);

void cigar_prepend_forward(
    cigar_t* const cigar_dst,
    cigar_t* const cigar_src);
void cigar_append_forward(
    cigar_t* const cigar_dst,
    cigar_t* const cigar_src);
void cigar_append_reverse(
    cigar_t* const cigar_dst,
    cigar_t* const cigar_src);

void cigar_append_deletion(
    cigar_t* const cigar,
    const int length);
void cigar_append_insertion(
    cigar_t* const cigar,
    const int length);

/*
 * SAM-compliant CIGAR
 */
void cigar_get_CIGAR(
    cigar_t* const cigar,
    const bool show_mismatches,
    uint32_t** const cigar_buffer,
    int* const cigar_length);

void cigar_to_operations(
    cigar_t* const cigar,
    const char* const cigar_str,
    const uint64_t cigar_length);
/*
 * Score
 */
int cigar_score_edit(
    cigar_t* const cigar);

/*
 * Utils
 */
int cigar_cmp(
    cigar_t* const cigar_a,
    cigar_t* const cigar_b);
void cigar_copy(
    cigar_t* const cigar_dst,
    cigar_t* const cigar_src);

void cigar_discover_mismatches(
    char* const pattern,
    const int pattern_length,
    char* const text,
    const int text_length,
    cigar_t* const cigar);

/*
 * Check
 */
bool cigar_check_alignment(
    FILE* const stream,
    const char* const pattern,
    const int pattern_length,
    const char* const text,
    const int text_length,
    cigar_t* const cigar,
    const bool verbose);

/*
 * Display
 */
void cigar_print(
    FILE* const stream,
    cigar_t* const cigar,
    const bool print_matches,
    mm_allocator_t *const mm_allocator);
int cigar_sprint(
    char* const buffer,
    const int buf_size,
    cigar_t* const cigar,
    const bool print_matches);

void cigar_print_SAM_CIGAR(
    FILE* const stream,
    cigar_t* const cigar,
    const bool show_mismatches,
    mm_allocator_t *const mm_allocator);
int cigar_sprint_SAM_CIGAR(
    char* const buffer,
    const int buf_size,
    cigar_t* const cigar,
    const bool show_mismatches);

void cigar_print_pretty(
    FILE* const stream,
    cigar_t* const cigar,
    const char* const pattern,
    const int pattern_length,
    const char* const text,
    const int text_length,
    mm_allocator_t *const mm_allocator);

#endif /* CIGAR_H_ */
