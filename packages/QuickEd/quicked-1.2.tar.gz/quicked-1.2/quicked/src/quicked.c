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

#include "quicked.h"
#include "bpm_banded.h"
#include "bpm_commons.h"
#include "bpm_windowed.h"
#include "bpm_hirschberg.h"
#include "quicked_utils/include/commons.h"
#include "quicked_utils/include/profiler_timer.h"
#include <stddef.h>

void extract_results(
    quicked_aligner_t *aligner,
    cigar_t *const cigar)
{
    if (aligner->params->only_score)
    {
        // Precomputed score
        aligner->score = cigar->score;
    }
    else
    {
        // CIGAR
        if (cigar->begin_offset < cigar->end_offset)
        {
            int buf_size = (2 * (cigar->end_offset - cigar->begin_offset) + 10) * sizeof(char);
            aligner->cigar = (char*) mm_allocator_malloc(aligner->mm_allocator, buf_size);
            cigar_sprint(aligner->cigar, buf_size, cigar, true);
        }

        // Score from CIGAR
        aligner->score = cigar_score_edit(cigar);
    }
}

quicked_status_t run_banded(
    quicked_aligner_t *aligner,
    const char* pattern, const int pattern_len,
    const char* text, const int text_len)
{
    // FIXME: What if cutoff_score becomes 0?
    const int cutoff_score = (MAX(text_len, pattern_len) * (aligner->params->bandwidth)) / 100;

    // Allocate
    mm_allocator_t *const mm_allocator = aligner->mm_allocator;

    banded_pattern_t banded_pattern;
    banded_pattern_compile(&banded_pattern, pattern, pattern_len, mm_allocator);

    banded_matrix_t banded_matrix;
    banded_matrix_allocate(&banded_matrix, pattern_len, text_len, cutoff_score, aligner->params->only_score, mm_allocator);

    // Align
    timer_start(aligner->timer);
    banded_compute(&banded_matrix, &banded_pattern, text, text_len, text_len, aligner->params->only_score, aligner->params->force_scalar);
    timer_stop(aligner->timer);

    // Retrieve results
    extract_results(aligner, banded_matrix.cigar);

    // Free
    banded_pattern_free(&banded_pattern, mm_allocator);

    banded_matrix_free(&banded_matrix, mm_allocator);

    return QUICKED_WIP;
}

quicked_status_t run_windowed(
    quicked_aligner_t *aligner,
    const char* pattern, const int pattern_len,
    const char* text, const int text_len)
{
    const int window_size = aligner->params->window_size;
    const int overlap_size = aligner->params->overlap_size;

    // Allocate
    mm_allocator_t *const mm_allocator = aligner->mm_allocator;

    windowed_pattern_t windowed_pattern;
    windowed_pattern_compile(&windowed_pattern, pattern, pattern_len, mm_allocator);

    windowed_matrix_t windowed_matrix;
    windowed_matrix_allocate(&windowed_matrix, pattern_len, text_len, mm_allocator, window_size);

    // Align
    timer_start(aligner->timer);
    windowed_compute(&windowed_matrix, &windowed_pattern, text, 0, window_size, overlap_size,
                     aligner->params->only_score, aligner->params->force_scalar);
    timer_stop(aligner->timer);


    // Retrieve results
    extract_results(aligner, windowed_matrix.cigar);

    // Free
    windowed_pattern_free(&windowed_pattern, mm_allocator);
    windowed_matrix_free(&windowed_matrix, mm_allocator);

    return QUICKED_WIP;
}

quicked_status_t run_hirschberg(
    quicked_aligner_t *aligner,
    const char* pattern, const int pattern_len,
    const char* text, const int text_len)
{
    // FIXME: What if cutoff_score becomes 0?
    const int cutoff_score = (MAX(text_len, pattern_len) * (aligner->params->bandwidth)) / 100;

    // Allocate
    mm_allocator_t *const mm_allocator = aligner->mm_allocator;

    char *text_r = (char *)mm_allocator_malloc(mm_allocator, text_len);
    char *pattern_r = (char *)mm_allocator_malloc(mm_allocator, pattern_len);

    reverse_string(text, text_r, text_len);
    reverse_string(pattern, pattern_r, pattern_len);

    cigar_t cigar_out;
    cigar_out.operations = (char *)  mm_allocator_malloc(aligner->mm_allocator, (pattern_len + text_len) * sizeof(char));
    cigar_out.begin_offset = pattern_len + text_len;
    cigar_out.end_offset = pattern_len + text_len;

    // Align
    timer_start(aligner->timer);
    quicked_status_t status = bpm_compute_matrix_hirschberg(text, text_r, text_len, pattern, pattern_r, pattern_len,
                                  cutoff_score, &cigar_out, aligner->params->force_scalar, mm_allocator);
    timer_stop(aligner->timer);

    // Retrieve results
    extract_results(aligner, &cigar_out);

    // Free
    mm_allocator_free(mm_allocator, cigar_out.operations);
    mm_allocator_free(mm_allocator, pattern_r);
    mm_allocator_free(mm_allocator, text_r);
    return status;
}

quicked_status_t run_quicked(
    quicked_aligner_t *aligner,
    const char* pattern, const int pattern_len,
    const char* text, const int text_len)
{
    // TODO: Comment phases of the algorithm

    mm_allocator_t *const mm_allocator = aligner->mm_allocator;

    char *text_r = (char *)mm_allocator_malloc(mm_allocator, text_len);
    char *pattern_r = (char *)mm_allocator_malloc(mm_allocator, pattern_len);

    reverse_string(text, text_r, text_len);
    reverse_string(pattern, pattern_r, pattern_len);

    windowed_pattern_t windowed_pattern;
    windowed_pattern_compile(&windowed_pattern, pattern, pattern_len, mm_allocator);

    windowed_matrix_t windowed_matrix;
    windowed_matrix_allocate(&windowed_matrix, pattern_len, text_len, mm_allocator, QUICKED_FAST_WINDOW_SIZE);

    timer_start(aligner->timer);
    timer_start(aligner->timer_windowed_s);

    // Align
    windowed_compute(&windowed_matrix, &windowed_pattern, text,
                    aligner->params->hew_threshold[0],
                    QUICKED_FAST_WINDOW_SIZE, QUICKED_FAST_WINDOW_OVERLAP,
                    SCORE_ONLY, aligner->params->force_scalar);

    timer_stop(aligner->timer_windowed_s);

    int64_t score = windowed_matrix.cigar->score;

    // Free
    windowed_pattern_free(&windowed_pattern, mm_allocator);
    windowed_matrix_free(&windowed_matrix, mm_allocator);

    if((windowed_matrix.high_error_window * 64) >
        (MAX(text_len, pattern_len) * aligner->params->hew_percentage[0] / 100))
    {
        timer_start(aligner->timer_windowed_l);

        windowed_pattern_compile(&windowed_pattern, pattern, pattern_len, mm_allocator);
        windowed_matrix_allocate(&windowed_matrix, pattern_len, text_len, mm_allocator, aligner->params->window_size);

        windowed_compute(&windowed_matrix, &windowed_pattern, text,
                aligner->params->hew_threshold[1],
                aligner->params->window_size, aligner->params->overlap_size,
                SCORE_ONLY, aligner->params->force_scalar);

        score = windowed_matrix.cigar->score;
        uint64_t high_error_window = windowed_matrix.high_error_window;

        // TODO: This free/alloc could be avoided
        windowed_pattern_free(&windowed_pattern, mm_allocator);
        windowed_matrix_free(&windowed_matrix, mm_allocator);

        windowed_pattern_compile(&windowed_pattern, pattern_r, pattern_len, mm_allocator);
        windowed_matrix_allocate(&windowed_matrix, pattern_len, text_len, mm_allocator, aligner->params->window_size);

        windowed_compute(&windowed_matrix, &windowed_pattern, text_r,
                aligner->params->hew_threshold[1],
                aligner->params->window_size, aligner->params->overlap_size,
                SCORE_ONLY, aligner->params->force_scalar);

        score = MIN(score, windowed_matrix.cigar->score);
        if (score >= windowed_matrix.cigar->score) high_error_window = windowed_matrix.high_error_window;

        windowed_pattern_free(&windowed_pattern, mm_allocator);
        windowed_matrix_free(&windowed_matrix, mm_allocator);

        timer_stop(aligner->timer_windowed_l);

        if((high_error_window * 64 * (aligner->params->window_size - aligner->params->overlap_size)) >
            (MAX(text_len, pattern_len) * aligner->params->hew_percentage[1] / 100))
        {
            timer_start(aligner->timer_banded);

            banded_pattern_t banded_pattern;
            banded_matrix_t banded_matrix_score;
            banded_pattern_compile(&banded_pattern, pattern, pattern_len, mm_allocator);

            score = MIN(MAX(text_len, pattern_len) * aligner->params->bandwidth / 100, score);

            banded_matrix_allocate(&banded_matrix_score, pattern_len, text_len, score, SCORE_ONLY, mm_allocator);

            banded_compute(&banded_matrix_score, &banded_pattern, text, text_len, text_len, SCORE_ONLY, aligner->params->force_scalar);

            // align_input->seqs_with_15 = true; // TODO: Remove if unused

            int64_t new_score = banded_matrix_score.cigar->score;

            banded_matrix_free(&banded_matrix_score, mm_allocator);

            timer_stop(aligner->timer_banded);

            while((new_score > MAX(text_len, pattern_len) / 4 && score * 3/2 < new_score) || new_score < 0)
            {
                score *= 2;
                timer_start(aligner->timer_banded);

                banded_matrix_allocate(&banded_matrix_score, pattern_len, text_len, score, SCORE_ONLY, mm_allocator);

                banded_compute(&banded_matrix_score, &banded_pattern, text, text_len, text_len, SCORE_ONLY, aligner->params->force_scalar);

                // align_input->seqs_with_30 = true; // TODO: Remove if unused

                new_score = banded_matrix_score.cigar->score;

                banded_matrix_free(&banded_matrix_score, mm_allocator);

                timer_stop(aligner->timer_banded);
            }

            score = new_score;
            banded_pattern_free(&banded_pattern, mm_allocator);
        }
    }

    timer_start(aligner->timer_align);

    cigar_t cigar_out;
    cigar_out.operations = (char *)  mm_allocator_malloc(aligner->mm_allocator, (pattern_len + text_len) * sizeof(char));
    cigar_out.begin_offset = pattern_len + text_len;
    cigar_out.end_offset = pattern_len + text_len;

    bpm_compute_matrix_hirschberg(text, text_r, text_len, pattern, pattern_r, pattern_len,
                                  score, &cigar_out, aligner->params->force_scalar, mm_allocator);

    timer_stop(aligner->timer_align);
    timer_stop(aligner->timer);

    // benchmark_print_output(align_input, false, &cigar_out);
    // align_input->diff_scores = (float)(score - cigar_out.score) / (float)(MAX(align_input->text_length, align_input->pattern_length));

    extract_results(aligner, &cigar_out);

    mm_allocator_free(mm_allocator, cigar_out.operations);
    mm_allocator_free(mm_allocator,text_r);
    mm_allocator_free(mm_allocator,pattern_r);

    return QUICKED_WIP;
}

quicked_params_t quicked_default_params(void)
{
    return (quicked_params_t){
        .algo = QUICKED,
        .only_score = false,
        .bandwidth = 15,
        .window_size = 9,
        .hew_threshold = {40, 40},
        .hew_percentage = {15, 15},
        .overlap_size = 1,
        .force_scalar = false,
        .external_timer = false,
        .external_allocator = NULL,
    };
}

quicked_status_t quicked_new(
    quicked_aligner_t *aligner,
    quicked_params_t *params)
{
    aligner->params = params;
    aligner->score = -1;
    aligner->cigar = NULL;
    if(params->external_allocator == NULL){
        aligner->mm_allocator = mm_allocator_new(BUFFER_SIZE_128M);
    }else {
        aligner->mm_allocator = params->external_allocator;
    }

    if(!params->external_timer){
        aligner->timer = mm_allocator_malloc(aligner->mm_allocator, sizeof(profiler_timer_t));
        aligner->timer_windowed_s = mm_allocator_malloc(aligner->mm_allocator, sizeof(profiler_timer_t));
        aligner->timer_windowed_l = mm_allocator_malloc(aligner->mm_allocator, sizeof(profiler_timer_t));
        aligner->timer_banded = mm_allocator_malloc(aligner->mm_allocator, sizeof(profiler_timer_t));
        aligner->timer_align = mm_allocator_malloc(aligner->mm_allocator, sizeof(profiler_timer_t));

        timer_reset(aligner->timer);
        timer_reset(aligner->timer_windowed_s);
        timer_reset(aligner->timer_windowed_l);
        timer_reset(aligner->timer_banded);
        timer_reset(aligner->timer_align);
    }


    return QUICKED_WIP;
}

quicked_status_t quicked_free(
    quicked_aligner_t *aligner)
{
    if (aligner->cigar != NULL)
    {
        mm_allocator_free(aligner->mm_allocator, aligner->cigar);
        aligner->cigar = NULL;
    }

    if(!aligner->params->external_timer){
        mm_allocator_free(aligner->mm_allocator, aligner->timer);
        mm_allocator_free(aligner->mm_allocator, aligner->timer_windowed_s);
        mm_allocator_free(aligner->mm_allocator, aligner->timer_windowed_l);
        mm_allocator_free(aligner->mm_allocator, aligner->timer_banded);
        mm_allocator_free(aligner->mm_allocator, aligner->timer_align);
    }

    if ((aligner->mm_allocator != NULL) && (aligner->params->external_allocator == NULL))
    {
        mm_allocator_delete(aligner->mm_allocator);
        aligner->mm_allocator = NULL;
    }

    return QUICKED_WIP;
}

bool quicked_check_error(quicked_status_t status) { return status < 0; }

const char* quicked_status_msg(
    quicked_status_t status)
{
    switch (status)
    {
        case QUICKED_ERROR:
            return "ERROR: QuickEd has finished with unspecific error\n";
        case QUICKED_FAIL_NON_CONVERGENCE:
            return "ERROR: Hirschberg algorithm can not find a middle point of subsequence division!\n";
        case QUICKED_UNIMPLEMENTED:
            return "ERROR: The algorithm or parameter combination selected is not implemented\n";
        case QUICKED_UNKNOWN_ALGO:
            return "ERROR: Unknown algorithm selection\n";
        case QUICKED_EMPTY_SEQUENCE:
            return "ERROR: Tried to align an empty sequence\n";
        case QUICKED_OK:
        case QUICKED_WIP:
        default:
            return "QuickEd finished without errors.\n";
    }

}

quicked_status_t quicked_align(
    quicked_aligner_t *aligner,
    const char* pattern, const int pattern_len,
    const char* text, const int text_len)
{

    if (pattern_len == 0 || text_len == 0)
    {
        return QUICKED_EMPTY_SEQUENCE;
    }

    quicked_status_t status = QUICKED_ERROR;

    switch (aligner->params->algo)
    {
    case QUICKED:
        status = run_quicked(aligner, pattern, pattern_len, text, text_len);
        break;
    case BANDED:
        status = run_banded(aligner, pattern, pattern_len, text, text_len);
        break;
    case WINDOWED:
        status = run_windowed(aligner, pattern, pattern_len, text, text_len);
        break;
    case HIRSCHBERG:
        status = run_hirschberg(aligner, pattern, pattern_len, text, text_len);
        break;
    default:
        return QUICKED_UNKNOWN_ALGO;
    }

    return status;
}