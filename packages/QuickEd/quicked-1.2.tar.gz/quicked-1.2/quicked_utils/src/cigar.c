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

#include "commons.h"
#include "cigar.h"
#include "quicked_utils/include/mm_allocator.h"

/*
 * SAM CIGAR Operations
 */
#define SAM_CIGAR_MATCH  0
#define SAM_CIGAR_INS    1
#define SAM_CIGAR_DEL    2
#define SAM_CIGAR_N_SKIP 3
#define SAM_CIGAR_EQ     7
#define SAM_CIGAR_X      8
/* ... */
#define SAM_CIGAR_NA    15

const uint8_t sam_cigar_lut[256] =
{
  REPEAT_256(SAM_CIGAR_NA),
  ['M'] = SAM_CIGAR_MATCH,
  ['I'] = SAM_CIGAR_INS,
  ['D'] = SAM_CIGAR_DEL,
  ['N'] = SAM_CIGAR_N_SKIP,
  ['='] = SAM_CIGAR_EQ,
  ['X'] = SAM_CIGAR_X,
};

/*
 * Setup
 */
cigar_t* cigar_new(
    const int max_operations,
    mm_allocator_t *const mm_allocator) {
  // Allocate
  cigar_t* const cigar = mm_allocator_malloc(mm_allocator, sizeof(cigar_t));
  // Allocate alignment-operations buffer
  cigar->max_operations = max_operations;
  cigar->operations = mm_allocator_malloc(mm_allocator, cigar->max_operations);
  cigar->begin_offset = 0;
  cigar->end_offset = 0;
  cigar->score = INT32_MIN;
  cigar->end_v = -1;
  cigar->end_h = -1;
  // CIGAR
  cigar->cigar_length = 0;
  //cigar->cigar_buffer = calloc(max_operations,sizeof(uint32_t));
  cigar->cigar_buffer = mm_allocator_calloc(mm_allocator, max_operations, uint32_t, true);
  // Return
  return cigar;
}
void cigar_clear(
    cigar_t* const cigar) {
  // Alignment operations
  cigar->begin_offset = 0;
  cigar->end_offset = 0;
  // Score and end position
  cigar->score = INT32_MIN;
  cigar->end_v = -1;
  cigar->end_h = -1;
  // CIGAR
  cigar->cigar_length = 0;
}
void cigar_resize(
    cigar_t* const cigar,
    const int max_operations,
    mm_allocator_t *const mm_allocator) {
  // Check maximum operations
  if (max_operations > cigar->max_operations) {
    cigar->max_operations = max_operations;
    free(cigar->operations); // Free
    free(cigar->cigar_buffer); // Free
    cigar->operations = mm_allocator_malloc(mm_allocator, max_operations); // Allocate
    cigar->cigar_buffer = mm_allocator_calloc(mm_allocator, max_operations, uint32_t, true); // Allocate
  }
  cigar_clear(cigar);
}
void cigar_free(
    cigar_t* const cigar,
    mm_allocator_t *const mm_allocator) {
  mm_allocator_free(mm_allocator, cigar->operations);
  mm_allocator_free(mm_allocator, cigar->cigar_buffer);
  mm_allocator_free(mm_allocator, cigar);
}
/*
 * Accessors
 */
bool cigar_is_null(
    cigar_t* const cigar) {
  return (cigar->begin_offset >= cigar->end_offset);
}
int cigar_count_matches(
    cigar_t* const cigar) {
  int i, num_matches=0;
  for (i=cigar->begin_offset;i<cigar->end_offset;++i) {
    num_matches += (cigar->operations[i]=='M');
  }
  return num_matches;
}
void cigar_append_forward(
    cigar_t* const cigar_dst,
    cigar_t* const cigar_src) {
  // Parameters
  const int cigar_length = cigar_src->end_offset - cigar_src->begin_offset;
  char* const operations_src = cigar_src->operations + cigar_src->begin_offset;
  char* const operations_dst = cigar_dst->operations + cigar_dst->end_offset;
  // Append forward
  memcpy(operations_dst,operations_src,cigar_length);
  // Update offset
  cigar_dst->end_offset += cigar_length;
}
void cigar_append_reverse(
    cigar_t* const cigar_dst,
    cigar_t* const cigar_src) {
  // Parameters
  const int begin_offset = cigar_src->begin_offset;
  const int end_offset = cigar_src->end_offset;
  const int cigar_length = end_offset - begin_offset;
  char* const operations_src = cigar_src->operations + begin_offset;
  char* const operations_dst = cigar_dst->operations + cigar_dst->end_offset;
  // Append reverse
  int i;
  for (i=0;i<cigar_length;++i) {
    operations_dst[i] = operations_src[cigar_length-1-i];
  }
  // Update offset
  cigar_dst->end_offset += cigar_length;
}
void cigar_append_deletion(
    cigar_t* const cigar,
    const int length) {
  // Append deletions
  char* const operations = cigar->operations + cigar->end_offset;
  int i;
  for (i=0;i<length;++i) {
    operations[i] = 'D';
  }
  // Update offset
  cigar->end_offset += length;
}
void cigar_append_insertion(
    cigar_t* const cigar,
    const int length) {
  // Append insertions
  char* const operations = cigar->operations + cigar->end_offset;
  int i;
  for (i=0;i<length;++i) {
    operations[i] = 'I';
  }
  // Update offset
  cigar->end_offset += length;
}

// Inserts cigar_in just before the last carecter of the cigar_out
// TODO: check possible errors (not enough spcace)
void cigar_prepend_forward(
    cigar_t* const cigar_in,
    cigar_t* const cigar_out) {
  // Print Sequence
  int op_sentinel = cigar_out->begin_offset-1;
  for(int i = cigar_in->end_offset-1; i >= cigar_in->begin_offset; i--){
    cigar_out->operations[op_sentinel--] = cigar_in->operations[i];
  }
  cigar_out->begin_offset = op_sentinel + 1;
}

/*
 * SAM-compliant CIGAR
 */
void cigar_compute_CIGAR(
    cigar_t* const cigar,
    const bool show_mismatches) {
  // Prepare CIGAR (SAM compliant)
  if (cigar->cigar_length == 0) {
    const char* const operations = cigar->operations;
    const int begin_offset = cigar->begin_offset;
    const int end_offset = cigar->end_offset;
    // Check null CIGAR
    if (begin_offset >= end_offset) {
      cigar->cigar_length = 0;
      return;
    }
    // Generate CIGAR
    uint32_t* const cigar_buffer = cigar->cigar_buffer;
    int cigar_length = 0;
    char last_op = operations[begin_offset];
    uint32_t last_op_len = 1;
    int i;
    for (i=begin_offset+1;i<end_offset;++i) {
      // Fetch operation
      char op = operations[i];
      if (!show_mismatches && op=='X') op = 'M';
      // Check previous operations
      if (op == last_op) {
        ++last_op_len;
      } else {
        // Dump operation
        if (show_mismatches && last_op=='M') {
          cigar_buffer[cigar_length++] = (last_op_len << 4) | ((uint32_t)SAM_CIGAR_EQ);
        } else {
          cigar_buffer[cigar_length++] = (last_op_len << 4) | ((uint32_t)sam_cigar_lut[(int)last_op]);
        }
        // Save new operation
        last_op = op;
        last_op_len = 1;
      }
    }
    // Dump last operation
    if (show_mismatches && last_op=='M') {
      cigar_buffer[cigar_length++] = (last_op_len << 4) | ((uint32_t)SAM_CIGAR_EQ);
    } else {
      cigar_buffer[cigar_length++] = (last_op_len << 4) | ((uint32_t)sam_cigar_lut[(int)last_op]);
    }
    // Set as ready
    cigar->cigar_length = cigar_length;
  }
}
void cigar_get_CIGAR(
    cigar_t* const cigar,
    const bool show_mismatches,
    uint32_t** const cigar_buffer,
    int* const cigar_length) {
  // Compute CIGAR
  cigar_compute_CIGAR(cigar,show_mismatches);
  // Return
  *cigar_buffer = cigar->cigar_buffer;
  *cigar_length = cigar->cigar_length;
}
void cigar_to_operations(
    cigar_t* const cigar,
    const char* const cigar_str,
    const uint64_t cigar_length) {
  int num = 0;
  for(uint64_t i = 0; i < cigar_length;){
    char operation = cigar_str[i];
    if (operation >= '0' && operation <= '9') {
      num = atoi(cigar_str + i);
      while (cigar_str[i] >= '0' && cigar_str[i] <= '9') { i++; } // skip the number
    }
    else {
      for (int j = 0; j < num; j++) {
        cigar->operations[cigar->end_offset++] = operation;
      }
      i++;
    }
  }
}
/*
 * Score
 */
int cigar_score_edit(
    cigar_t* const cigar) {
  int score = 0, i;
  for (i=cigar->begin_offset;i<cigar->end_offset;++i) {
    switch (cigar->operations[i]) {
      case 'M': break;
      case 'X':
      case 'D':
      case 'I': ++score; break;
      default:
        fprintf(stderr,"[CIGAR] Computing CIGAR score: Unknown operation (%c)\n",cigar->operations[i]);
        exit(1);
    }
  }
  return score;
}
/*
 * Utils
 */
int cigar_cmp(
    cigar_t* const cigar_a,
    cigar_t* const cigar_b) {
  // Compare lengths
  const int length_cigar_a = cigar_a->end_offset - cigar_a->begin_offset;
  const int length_cigar_b = cigar_b->end_offset - cigar_b->begin_offset;
  if (length_cigar_a != length_cigar_b) return length_cigar_a - length_cigar_b;
  // Compare operations
  char* const operations_a = cigar_a->operations + cigar_a->begin_offset;
  char* const operations_b = cigar_b->operations + cigar_b->begin_offset;
  int i;
  for (i=0;i<length_cigar_a;++i) {
    if (operations_a[i] != operations_b[i]) {
      return operations_a[i] - operations_b[i];
    }
  }
  // Equal
  return 0;
}
void cigar_copy(
    cigar_t* const cigar_dst,
    cigar_t* const cigar_src) {
  cigar_dst->max_operations = cigar_src->max_operations;
  cigar_dst->begin_offset = cigar_src->begin_offset;
  cigar_dst->end_offset = cigar_src->end_offset;
  cigar_dst->score = cigar_src->score;
  memcpy(cigar_dst->operations+cigar_src->begin_offset,
         cigar_src->operations+cigar_src->begin_offset,
         cigar_src->end_offset-cigar_src->begin_offset);
}
void cigar_discover_mismatches(
    char* const pattern,
    const int pattern_length,
    char* const text,
    const int text_length,
    cigar_t* const cigar) {
  // Refine adding mismatches
  int i, p=0, t=0;
  for (i=cigar->begin_offset;i<cigar->end_offset;++i) {
    // Check limits
    if (p >= pattern_length || t >= text_length) break;
    switch (cigar->operations[i]) {
      case 'M':
        cigar->operations[i] = (pattern[p]==text[t]) ? 'M' : 'X';
        ++p; ++t;
        break;
      case 'I':
        ++t;
        break;
      case 'D':
        ++p;
        break;
      default:
        fprintf(stderr,"[CIGAR] Wrong edit operation\n");
        exit(1);
        break;
    }
  }
  while (p < pattern_length) { cigar->operations[i++] = 'D'; ++p; };
  while (t < text_length) { cigar->operations[i++] = 'I'; ++t; };
  cigar->end_offset = i;
  cigar->operations[cigar->end_offset] = '\0';
  //  // DEBUG
  //  printf("Score=%ld\nPath-length=%" PRIu64 "\nCIGAR=%s\n",
  //      gaba_alignment->score,gaba_alignment->plen,
  //      cigar->operations);
}
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
    const bool verbose) {
  // Parameters
  char* const operations = cigar->operations;
  // Traverse CIGAR
  int pattern_pos=0, text_pos=0, i;
  for (i=cigar->begin_offset;i<cigar->end_offset;++i) {
    switch (operations[i]) {
      case 'M':
        // Check match
        if (pattern[pattern_pos] != text[text_pos]) {
          if (verbose) {
            fprintf(stream,
                "[AlignCheck] Alignment not matching (pattern[%d]=%c != text[%d]=%c)\n",
                pattern_pos,pattern[pattern_pos],text_pos,text[text_pos]);
          }
          return false;
        }
        ++pattern_pos;
        ++text_pos;
        break;
      case 'X':
        // Check mismatch
        if (pattern[pattern_pos] == text[text_pos]) {
          if (verbose) {
            fprintf(stream,
                "[AlignCheck] Alignment not mismatching (pattern[%d]=%c == text[%d]=%c)\n",
                pattern_pos,pattern[pattern_pos],text_pos,text[text_pos]);
          }
          return false;
        }
        ++pattern_pos;
        ++text_pos;
        break;
      case 'I':
        ++text_pos;
        break;
      case 'D':
        ++pattern_pos;
        break;
      default:
        fprintf(stderr,"[AlignCheck] Unknown edit operation '%c'\n",operations[i]);
        exit(1);
        break;
    }
  }
  // Check alignment length
  if (pattern_pos != pattern_length) {
    if (verbose) {
      fprintf(stream,
          "[AlignCheck] Alignment incorrect length (pattern-aligned=%d,pattern-length=%d)\n",
          pattern_pos,pattern_length);
    }
    return false;
  }
  if (text_pos != text_length) {
    if (verbose) {
      fprintf(stream,
          "[AlignCheck] Alignment incorrect length (text-aligned=%d,text-length=%d)\n",
          text_pos,text_length);
    }
    return false;
  }
  // OK
  return true;
}
/*
 * Display
 */
void cigar_print(
    FILE* const stream,
    cigar_t* const cigar,
    const bool print_matches,
    mm_allocator_t *const mm_allocator) {
  // Check null
  if (cigar_is_null(cigar)) return;
  // Generate and print operations
  int buf_size = 2*(cigar->end_offset-cigar->begin_offset)+10;
  char* const buffer = mm_allocator_malloc(mm_allocator, buf_size);
  cigar_sprint(buffer,buf_size,cigar,print_matches);
  fprintf(stream,"%s",buffer); // Print
  // Free
  mm_allocator_free(mm_allocator, buffer);
}
int cigar_sprint(
    char* const buffer,
    const int buf_size,
    cigar_t* const cigar,
    const bool print_matches) {
  // Check null
  if (cigar_is_null(cigar)) {
    buffer[0] = '\0';
    return 0;
  }
  // Parameters
  const char* const operations = cigar->operations;
  const int begin_offset = cigar->begin_offset;
  const int end_offset = cigar->end_offset;
  // Print operations
  char last_op = operations[begin_offset];
  int last_op_length = 1;
  int i, cursor = 0;
  for (i=begin_offset+1;i<end_offset;++i) {
    if (operations[i]==last_op) {
      ++last_op_length;
    } else {
      if (print_matches || last_op != 'M') {
        cursor += snprintf(buffer+cursor,buf_size,"%d%c",last_op_length,last_op);
      }
      last_op = operations[i];
      last_op_length = 1;
    }
  }
  if (print_matches || last_op != 'M') {
    cursor += snprintf(buffer+cursor,buf_size,"%d%c",last_op_length,last_op);
  }
  // Return
  buffer[cursor] = '\0';
  return cursor;
}
void cigar_print_SAM_CIGAR(
    FILE* const stream,
    cigar_t* const cigar,
    const bool show_mismatches,
    mm_allocator_t *const mm_allocator) {
  // Check null
  if (cigar_is_null(cigar)) return;
  // Generate and print operations
  int buf_size = 2*(cigar->end_offset-cigar->begin_offset);
  char* const buffer = mm_allocator_malloc(mm_allocator,buf_size);
  cigar_sprint_SAM_CIGAR(buffer,buf_size,cigar,show_mismatches);
  fprintf(stream,"%s",buffer); // Print
  // Free
  mm_allocator_free(mm_allocator, buffer);
}
int cigar_sprint_SAM_CIGAR(
    char* const buffer,
    const int buf_size,
    cigar_t* const cigar,
    const bool show_mismatches) {
  // Get SAM CIGAR
  uint32_t* cigar_buffer;
  int cigar_length;
  cigar_get_CIGAR(cigar,show_mismatches,&cigar_buffer,&cigar_length);
  // Print CIGAR-operations
  int i, cursor = 0;
  for (i=0;i<cigar_length;++i) {
    const int op_idx = cigar_buffer[i] & 0xf;
    if (op_idx <= 8) {
      cursor += snprintf(buffer+cursor,buf_size,"%u%c",
          cigar_buffer[i]>>4,
          "MIDN---=X"[cigar_buffer[i]&0xf]);
        } else {
      cursor += snprintf(buffer+cursor,buf_size,"%u%c",
          cigar_buffer[i]>>4,'?');
    }
  }
  // Return
  buffer[cursor] = '\0';
  return cursor;
}
void cigar_print_pretty(
    FILE* const stream,
    cigar_t* const cigar,
    const char* const pattern,
    const int pattern_length,
    const char* const text,
    const int text_length,
    mm_allocator_t *const mm_allocator) {
  // Parameters
  char* const operations = cigar->operations;
  const int begin_offset = cigar->begin_offset;
  const int end_offset = cigar->end_offset;
  // Allocate alignment buffers
  const int max_buffer_length = text_length + pattern_length + 1;
  char* const mem = mm_allocator_calloc(mm_allocator, 3*max_buffer_length, char, true);
  char* const pattern_alg = mem;
  char* const ops_alg = pattern_alg + max_buffer_length;
  char* const text_alg = ops_alg + max_buffer_length;
  // Compute alignment buffers
  int i, alg_pos = 0, pattern_pos = 0, text_pos = 0;
  for (i=begin_offset;i<end_offset;++i) {
    switch (operations[i]) {
      case 'M':
        if (pattern[pattern_pos] != text[text_pos]) {
          pattern_alg[alg_pos] = pattern[pattern_pos];
          ops_alg[alg_pos] = 'X';
          text_alg[alg_pos++] = text[text_pos];
        } else {
          pattern_alg[alg_pos] = pattern[pattern_pos];
          ops_alg[alg_pos] = '|';
          text_alg[alg_pos++] = text[text_pos];
        }
        pattern_pos++; text_pos++;
        break;
      case 'X':
        if (pattern[pattern_pos] != text[text_pos]) {
          pattern_alg[alg_pos] = pattern[pattern_pos++];
          ops_alg[alg_pos] = ' ';
          text_alg[alg_pos++] = text[text_pos++];
        } else {
          pattern_alg[alg_pos] = pattern[pattern_pos++];
          ops_alg[alg_pos] = 'X';
          text_alg[alg_pos++] = text[text_pos++];
        }
        break;
      case 'I':
        pattern_alg[alg_pos] = '-';
        ops_alg[alg_pos] = ' ';
        text_alg[alg_pos++] = text[text_pos++];
        break;
      case 'D':
        pattern_alg[alg_pos] = pattern[pattern_pos++];
        ops_alg[alg_pos] = ' ';
        text_alg[alg_pos++] = '-';
        break;
      default:
        break;
    }
  }
  i=0;
  while (pattern_pos < pattern_length) {
    pattern_alg[alg_pos+i] = pattern[pattern_pos++];
    ops_alg[alg_pos+i] = '?';
    ++i;
  }
  i=0;
  while (text_pos < text_length) {
    text_alg[alg_pos+i] = text[text_pos++];
    ops_alg[alg_pos+i] = '?';
    ++i;
  }
  // Print string
  fprintf(stream,"      ALIGNMENT ");
  cigar_print(stream,cigar,true,mm_allocator);
  fprintf(stream,"\n");
  fprintf(stream,"      ETRACE    ");
  cigar_print(stream,cigar,false,mm_allocator);
  fprintf(stream,"\n");
  fprintf(stream,"      CIGAR     ");
  cigar_print_SAM_CIGAR(stream,cigar,false,mm_allocator);
  fprintf(stream,"\n");
  fprintf(stream,"      PATTERN    %s\n",pattern_alg);
  fprintf(stream,"                 %s\n",ops_alg);
  fprintf(stream,"      TEXT       %s\n",text_alg);
  // Free
  mm_allocator_free(mm_allocator, mem);
}


