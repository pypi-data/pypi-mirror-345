/*
 *                             The MIT License
 *
 * This file is part of QuickEd library.
 * Copyright (c) 2017 by Santiago Marco-Sola  <santiagomsola@gmail.com>
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
#ifdef _OPENMP
#include <omp.h>
#endif

#include "align_benchmark_params.h"

#include "quicked_utils/include/commons.h"
#include "quicked_utils/include/sequence_buffer.h"
#include "quicked_utils/include/profiler_timer.h"

#include "score_matrix.h"
#include "edit/edit_dp.h"

#include "benchmark/benchmark_edit.h"

/*
 * Configuration
 */
void align_input_configure_global(
    align_input_t* const align_input) {
  // Clear
  benchmark_align_input_clear(align_input);
  // Output
  align_input->output_file = parameters.output_file;
  align_input->output_full = parameters.output_full;
  // MM
  align_input->mm_allocator = mm_allocator_new(BUFFER_SIZE_128M);
  // PROFILE/STATS
  timer_reset(&align_input->timer);
  timer_reset(&align_input->timer_windowed_s);
  timer_reset(&align_input->timer_windowed_l);
  timer_reset(&align_input->timer_banded);
  timer_reset(&align_input->timer_align);
  // DEBUG
  align_input->debug_flags = 0;
  if (parameters.check_display) align_input->debug_flags |= ALIGN_DEBUG_DISPLAY_INFO;
  if (parameters.check_correct) align_input->debug_flags |= ALIGN_DEBUG_CHECK_CORRECT;
  if (parameters.check_score) align_input->debug_flags |= ALIGN_DEBUG_CHECK_SCORE;
  if (parameters.check_alignments) align_input->debug_flags |= ALIGN_DEBUG_CHECK_ALIGNMENT;
  align_input->verbose = parameters.verbose;
}
void align_benchmark_free(
    align_input_t* const align_input) {
  mm_allocator_delete(align_input->mm_allocator);
}
/*
 * I/O
 */
bool align_benchmark_read_input(
    FILE* input_file,
    char** line1,
    char** line2,
    size_t* line1_allocated,
    size_t* line2_allocated,
    const int seqs_processed,
    align_input_t* const align_input) {
  // Parameters
  int line1_length=0, line2_length=0;
  // Read queries
  line1_length = (int)getline(line1,line1_allocated,input_file);
  if (line1_length==-1) return false;
  line2_length = (int)getline(line2,line2_allocated,input_file);
  if (line1_length==-1) return false;
  // Configure input
  align_input->sequence_id = seqs_processed;
  align_input->pattern = *line1 + 1;
  align_input->pattern_length = line1_length - 2;
  align_input->pattern[align_input->pattern_length] = '\0';
  align_input->text = *line2 + 1;
  align_input->text_length = line2_length - 2;
  if (align_input->text[align_input->text_length] == '\n') {
    align_input->text[align_input->text_length] = '\0';
  }
  return true;
}
/*
 * Display
 */
void align_benchmark_print_progress(
    const int seqs_processed) {
  const uint64_t time_elapsed_alg = timer_get_current_total_ns(&parameters.timer_global);
  const double rate_alg = (double)seqs_processed/(double)TIMER_CONVERT_NS_TO_S(time_elapsed_alg);
  fprintf(stderr,"...processed %d reads (alignment = %2.3f seq/s)\n",seqs_processed,rate_alg);
}
void align_benchmark_print_results(
    align_input_t* const align_input,
    const int seqs_processed) {
  // Print benchmark results
  fprintf(stderr,"[Benchmark]\n");
  fprintf(stderr,"=> Total.reads              %d\n",seqs_processed);
  fprintf(stderr,"=> Time.Benchmark        ");
  timer_print(stderr,&parameters.timer_global,NULL);
  if (parameters.num_threads == 1) {
    fprintf(stderr,"  => Time.Alignment      ");
    timer_print(stderr,&align_input->timer,&parameters.timer_global);
    if (parameters.algorithm == alignment_edit_quicked && parameters.verbose){
      fprintf(stderr,"  => Time.Windowed Small ");
      timer_print(stderr,&align_input->timer_windowed_s,&parameters.timer_global);
      fprintf(stderr,"  => Time.Windowed Large ");
      timer_print(stderr,&align_input->timer_windowed_l,&parameters.timer_global);
      fprintf(stderr,"  => Time.Banded         ");
      timer_print(stderr,&align_input->timer_banded,&parameters.timer_global);
      fprintf(stderr,"  => Time.Align          ");
      timer_print(stderr,&align_input->timer_align,&parameters.timer_global);
    }
  } else {
    for (int i=0;i<parameters.num_threads;++i) {
      fprintf(stderr,"  => Time.Alignment.Thread.%0d     ",i);
      timer_print(stderr,&align_input[i].timer,&parameters.timer_global);
    }
  }
  // Print Stats
  const bool checks_enabled =
      parameters.check_correct || parameters.check_score || parameters.check_alignments;
  if (checks_enabled && parameters.num_threads==1) {
    benchmark_print_stats(stderr,align_input);
  }
}
/*
 * Benchmark
 */
void align_benchmark_run_algorithm(
    align_input_t* const align_input) {
  // Select algorithm
  switch (parameters.algorithm) {
    // Edit
    case alignment_edit_bpm:
      benchmark_edit_bpm(align_input);
      break;
    case alignment_edit_windowed:
      benchmark_windowed(align_input,parameters.window_size, parameters.overlap_size,
                          parameters.force_scalar, false);
      break;
    case alignment_edit_banded:
      benchmark_banded(align_input,parameters.bandwidth, false);
      break;
    case alignment_edit_banded_hirschberg:
      benchmark_hirschberg(align_input,parameters.bandwidth);
      break;
    case alignment_edit_quicked:
      benchmark_quicked(align_input,parameters.window_size,parameters.overlap_size,
                        parameters.bandwidth, parameters.force_scalar, parameters.hew_threshold,
                        parameters.hew_percentage);
      break;
    case alignment_edit_dp:
      benchmark_edit_dp(align_input);
      break;
    case alignment_edit_dp_banded:
      benchmark_edit_dp_banded(align_input, parameters.bandwidth);
      break;
    // External
    case alignment_edlib:
      benchmark_edlib(align_input, parameters.bandwidth);
      break;
    default:
      fprintf(stderr,"Algorithm not implemented\n");
      exit(1);
      break;
  }
}
void align_benchmark_sequential(void) {
  // PROFILE
  timer_reset(&parameters.timer_global);
  timer_start(&parameters.timer_global);
  // I/O files
  parameters.input_file = fopen(parameters.input_filename, "r");
  if (parameters.input_file == NULL) {
    fprintf(stderr,"Input file '%s' couldn't be opened\n",parameters.input_filename);
    exit(1);
  }
  if (parameters.output_filename != NULL) {
    parameters.output_file = fopen(parameters.output_filename, "w");
  }
  // Global configuration
  align_input_t align_input;
  align_input_configure_global(&align_input);
  // Read-align loop
  int seqs_processed = 0, progress = 0;
  while (true) {
    // Read input sequence-pair
    const bool input_read = align_benchmark_read_input(
        parameters.input_file,&parameters.line1,&parameters.line2,
        &parameters.line1_allocated,&parameters.line2_allocated,
        seqs_processed,&align_input);
    if (!input_read) break;
    // Execute the selected algorithm
    align_benchmark_run_algorithm(&align_input);
    // Update progress
    ++seqs_processed;
    if (++progress == parameters.progress) {
      progress = 0;
      if (parameters.verbose >= 0) align_benchmark_print_progress(seqs_processed);
    }
  }
  // Print benchmark results
  timer_stop(&parameters.timer_global);

  if (parameters.verbose >= 0) align_benchmark_print_results(&align_input,seqs_processed);
  // Free
  align_benchmark_free(&align_input);
  fclose(parameters.input_file);
  if (parameters.output_file) fclose(parameters.output_file);
  free(parameters.line1);
  free(parameters.line2);
}

#ifdef _OPENMP
void align_benchmark_parallel(void) {
  // PROFILE
  timer_reset(&parameters.timer_global);
  timer_start(&parameters.timer_global);
  // Open input file
  parameters.input_file = fopen(parameters.input_filename, "r");
  if (parameters.input_file == NULL) {
    fprintf(stderr,"Input file '%s' couldn't be opened\n",parameters.input_filename);
    exit(1);
  }
  if (parameters.output_filename != NULL) {
    parameters.output_file = fopen(parameters.output_filename, "w");
  }

  VLA_INIT(align_input_t, align_input, parameters.num_threads);
  for (int tid=0;tid<parameters.num_threads;++tid) {
    align_input_configure_global(align_input+tid);
  }
  // Read-align loop
  sequence_buffer_t* const sequence_buffer = sequence_buffer_new(2*parameters.batch_size,100);
  int seqs_processed = 0, progress = 0, seqs_batch = 0;
  while (true) {
    // Read batch-input sequence-pair
    sequence_buffer_clear(sequence_buffer);
    for (seqs_batch=0;seqs_batch<parameters.batch_size;++seqs_batch) {
      const bool seqs_pending = align_benchmark_read_input(
          parameters.input_file,&parameters.line1,&parameters.line2,
          &parameters.line1_allocated,&parameters.line2_allocated,
          seqs_processed,align_input);
      if (!seqs_pending) break;
      // Add pair pattern-text
      sequence_buffer_add_pair(sequence_buffer,
          align_input->pattern,align_input->pattern_length,
          align_input->text,align_input->text_length);
    }
    if (seqs_batch == 0) break;
    // Parallel processing of the sequences batch
    #pragma omp parallel num_threads(parameters.num_threads)
    {
      int tid = omp_get_thread_num();
      int seq_idx;
      #pragma omp for
      for (seq_idx=0;seq_idx<seqs_batch;++seq_idx) {
        // Configure sequence
        sequence_offset_t* const offset = sequence_buffer->offsets + seq_idx;
        align_input[tid].sequence_id = seqs_processed;
        align_input[tid].pattern = sequence_buffer->buffer + offset->pattern_offset;
        align_input[tid].pattern_length = (int)(offset->pattern_length);
        align_input[tid].text = sequence_buffer->buffer + offset->text_offset;
        align_input[tid].text_length = (int)(offset->text_length);
        // Execute the selected algorithm
        align_benchmark_run_algorithm(align_input+tid);
      }
    }
    // Update progress
    seqs_processed += seqs_batch;
    progress += seqs_batch;
    if (progress >= parameters.progress) {
      progress -= parameters.progress;
      if (parameters.verbose >= 0) align_benchmark_print_progress(seqs_processed);
    }
  }
  // Print benchmark results
  timer_stop(&parameters.timer_global);
  if (parameters.verbose >= 0) align_benchmark_print_results(align_input,seqs_processed);
  // Free
  for (int tid=0;tid<parameters.num_threads;++tid) {
    align_benchmark_free(align_input+tid);
  }
  sequence_buffer_delete(sequence_buffer);
  fclose(parameters.input_file);
  if (parameters.output_file) fclose(parameters.output_file);
  free(parameters.line1);
  free(parameters.line2);
}
#endif
/*
 * Main
 */
int main(int argc,char* argv[]) {
  // Parsing command-line options
  parse_arguments(argc,argv);
  // Execute benchmark
  if (parameters.num_threads == 1) {
    align_benchmark_sequential();
  } else {
    #ifdef _OPENMP
      align_benchmark_parallel();
    #else
      align_benchmark_sequential();
    #endif
  }
}
