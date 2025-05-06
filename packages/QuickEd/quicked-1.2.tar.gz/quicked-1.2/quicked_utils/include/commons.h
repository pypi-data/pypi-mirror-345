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

#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <time.h>
#include <string.h>
#include <math.h>
#include <errno.h>
#ifdef _WIN32
#include <windows.h>
#include <_getopt.h>
#else
#include <getopt.h>
#endif
#ifdef __linux__
#include <sys/mman.h>
#endif

#ifdef _MSC_VER
#define strncasecmp _strnicmp
#define strcasecmp _stricmp
#endif

// #include <stdbool.h>
// #include <float.h>
// #include <ctype.h>
// #include <sys/types.h>
// #include <string.h>
// #include <wchar.h>
// #include <sys/time.h>
// #include <sys/stat.h>
// #include <sys/mman.h>
// #include <fcntl.h>
// #include <limits.h>
// #include <pwd.h>
// #include <stdarg.h>
// #include <err.h>
// #include <assert.h>
// #include <signal.h>

/*
 * Macro Utils
 */
#define STRINGIFY_(a) #a
#define STRINGIFY(a) STRINGIFY_(a)
#define SWAP(a,b) do {__typeof__(a) aux = a; a = b; b = aux;} while (0)
#define REPEAT_8(x) x, x, x, x, x, x, x, x
#define REPEAT_32(x) REPEAT_8(x), REPEAT_8(x), REPEAT_8(x), REPEAT_8(x)
#define REPEAT_256(x) REPEAT_32(x), REPEAT_32(x), REPEAT_32(x), REPEAT_32(x)
/*
 * Special Characters
 */
#define EOS '\0'
#define EOL '\n'
#define TAB '\t'
#define DOS_EOL '\r'
#define PLUS '+'
#define MINUS '-'
#define FORMAT '%'
#define SPACE ' '
#define SLASH '/'
#define STAR '*'
#define DOT '.'
#define COMA ','
#define SEMICOLON ';'
#define COLON ':'
#define HASH '#'
#define UNDERSCORE '_'

/*
 * Metric Factors
 */
#define METRIC_FACTOR_1K   (1000ul)
#define METRIC_FACTOR_1M   (1000000ul)
#define METRIC_FACTOR_1G   (1000000000ul)

/*
 * Number of lines
 */
#define NUM_LINES_1K      (1000ul)
#define NUM_LINES_2K      (2000ul)
#define NUM_LINES_5K      (5000ul)
#define NUM_LINES_10K    (10000ul)
#define NUM_LINES_20K    (20000ul)
#define NUM_LINES_50K    (50000ul)
#define NUM_LINES_100K  (100000ul)
#define NUM_LINES_200K  (200000ul)
#define NUM_LINES_500K  (500000ul)
#define NUM_LINES_1M   (1000000ul)
#define NUM_LINES_2M   (2000000ul)
#define NUM_LINES_5M   (5000000ul)
#define NUM_LINES_10M (10000000ul)
#define NUM_LINES_20M (20000000ul)
#define NUM_LINES_50M (50000000ul)

/*
 * Buffer sizes
 */
#define BUFFER_SIZE_1K   (1ul<<10)
#define BUFFER_SIZE_2K   (1ul<<11)
#define BUFFER_SIZE_4K   (1ul<<12)
#define BUFFER_SIZE_8K   (1ul<<13)
#define BUFFER_SIZE_16K  (1ul<<14)
#define BUFFER_SIZE_32K  (1ul<<15)
#define BUFFER_SIZE_64K  (1ul<<16)
#define BUFFER_SIZE_128K (1ul<<17)
#define BUFFER_SIZE_256K (1ul<<18)
#define BUFFER_SIZE_512K (1ul<<19)
#define BUFFER_SIZE_1M   (1ul<<20)
#define BUFFER_SIZE_2M   (1ul<<21)
#define BUFFER_SIZE_4M   (1ul<<22)
#define BUFFER_SIZE_8M   (1ul<<23)
#define BUFFER_SIZE_16M  (1ul<<24)
#define BUFFER_SIZE_32M  (1ul<<25)
#define BUFFER_SIZE_64M  (1ul<<26)
#define BUFFER_SIZE_128M (1ul<<27)
#define BUFFER_SIZE_256M (1ul<<28)
#define BUFFER_SIZE_512M (1ul<<29)
#define BUFFER_SIZE_1G   (1ul<<30)
#define BUFFER_SIZE_2G   (1ul<<31)
#define BUFFER_SIZE_4G   (1ul<<32)
#define BUFFER_SIZE_8G   (1ul<<33)
#define BUFFER_SIZE_16G  (1ul<<34)
#define BUFFER_SIZE_32G  (1ul<<35)
#define BUFFER_SIZE_64G  (1ul<<36)
#define BUFFER_SIZE_128G (1ul<<37)
#define BUFFER_SIZE_256G (1ul<<38)
// Conversion utils
#define CONVERT_B_TO_KB(number) ((number)/(1024))
#define CONVERT_B_TO_MB(number) ((number)/(1024*1024))
#define CONVERT_B_TO_GB(number) ((number)/(1024*1024*1024))

/*
 * BM sizes
 */
#define UINT512_LENGTH 512
#define UINT512_SIZE    64
#define UINT256_LENGTH 256
#define UINT256_SIZE    32
#define UINT128_LENGTH 128
#define UINT128_SIZE    16
#define UINT64_LENGTH   64
#define UINT64_SIZE      8
#define UINT32_LENGTH   32
#define UINT32_SIZE      4
#define UINT16_LENGTH   16
#define UINT16_SIZE      2
#define UINT8_LENGTH     8
#define UINT8_SIZE       1

/*
 * Common Masks
 */
#define UINT64_ZEROS           0x0000000000000000ull
#define UINT64_ONES            0xFFFFFFFFFFFFFFFFull
#define UINT32_ZEROS           0x00000000ul
#define UINT32_ONES            0xFFFFFFFFul
// Extraction masks
#define UINT64_ONE_MASK        0x0000000000000001ull
#define UINT64_ZERO_MASK       0xFFFFFFFFFFFFFFFEull
#define UINT64_ONE_LAST_MASK   0x8000000000000000ull
#define UINT64_ZERO_LAST_MASK  0x7FFFFFFFFFFFFFFFull
#define UINT32_ONE_MASK        0x00000001ul
#define UINT32_ZERO_MASK       0xFFFFFFFEul
#define UINT32_ONE_LAST_MASK   0x80000000ul
#define UINT32_ZERO_LAST_MASK  0x7FFFFFFFul
// Conversions/Extractions
#define UINT64_TO_UINT32_LSB(value) ((uint32_t)((value) & 0x00000000FFFFFFFFul))
#define UINT64_TO_UINT32_MSB(value) ((uint32_t)((value) >> 32))

/*
 * Common numerical data processing/formating
 */
#define MIN(a,b) (((a)<=(b))?(a):(b))
#define MAX(a,b) (((a)>=(b))?(a):(b))
#define ABS(a) (((a)>=0)?(a):-(a))

/*
 * Pseudo-Random number generator
 */
#define rand_init() srand(time(0))
#define rand_i(min,max) ( min + ( rand()%(max-min+1) ) )
#define rand_f(min,max) ( min + ((double)rand()/(double)(RAND_MAX+1)) * (max-min+1) )
uint64_t rand_iid(const uint64_t min,const uint64_t max);

/*
 * String
 */

void reverse_string(const char* in_string, char* out_string, uint64_t lenght);

#ifdef _WIN32
typedef long long ssize_t;
ssize_t getline(char **restrict lineptr, size_t *restrict n, FILE *restrict stream);
ssize_t getdelim(char **restrict lineptr, size_t *restrict n, int delim, FILE *restrict stream);
#endif

/*
 * Parsing
 */
#define IS_NUMBER(character) ('0' <= (character) && (character) <= '9')
#define IS_DIGIT(character) IS_NUMBER(character)
#define IS_LETTER(character) (('a' <= (character) && (character) <= 'z') || ('A' <= (character) && (character) <= 'Z'))
#define IS_ALPHANUMERIC(character) (IS_NUMBER(character) || IS_LETTER(character))
#define IS_BETWEEN(number,a,b) ((a)<=(number) && (number)<=(b))

#define IS_EOL(character) ((character)==EOL)
#define IS_ANY_EOL(character) ((character)==EOL || (character)==DOS_EOL)
#define IS_HEX_DIGIT(character) (IS_NUMBER(character) || ('a' <= (character) && (character) <= 'f') || ('A' <= (character) && (character) <= 'F'))

#define IS_END_OF_RECORD(character) ( (character)==EOL || (character)==EOS )
#define IS_END_OF_FIELD(character) ( IS_END_OF_RECORD(character) || (character)==SPACE || (character)==TAB )

#define GET_DIGIT(character) ((character) - '0')
#define GET_HEX_DIGIT(character) (IS_NUMBER(character) ? GET_DIGIT(character) : (toupper(character) - 'A' + 10))

/*
 * Math
 */
#define BOUNDED_SUBTRACTION(minuend,subtrahend,limit) (((minuend)>((limit)+(subtrahend))) ? (minuend)-(subtrahend):(limit))
#define BOUNDED_ADDITION(summand_A,summand_B,limit) ((((summand_A)+(summand_B))<(limit)) ? (summand_A)+(summand_B):(limit))

#define PERCENTAGE(AMOUNT,TOTAL) ((TOTAL)?100.0*(float)(AMOUNT)/(float)(TOTAL):0.0)
#define DIV_FLOOR(NUMERATOR,DENOMINATOR)  ((NUMERATOR)/(DENOMINATOR))
#define DIV_CEIL(NUMERATOR,DENOMINATOR)   (((NUMERATOR)+((DENOMINATOR)-1))/(DENOMINATOR))
#define DIVC_FLOOR(NUMERATOR,DENOMINATOR) ((DENOMINATOR) ? DIV_FLOOR(NUMERATOR,DENOMINATOR) :(0))
#define DIVC_CEIL(NUMERATOR,DENOMINATOR)  ((DENOMINATOR) ? DIV_CEIL(NUMERATOR,DENOMINATOR) :(0))

#define TELESCOPIC_FACTOR (3.0/2.0)

uint32_t nominal_prop_u32(const uint32_t base,const double factor);
uint64_t nominal_prop_u64(const uint64_t base,const double factor);

/*
 * Inline
 */
#if defined(_MSC_VER)
  #define FORCE_INLINE __forceinline
  #define FORCE_NO_INLINE __declspec(noinline)
  #else
  #define FORCE_INLINE __attribute__((always_inline)) inline
  #define FORCE_NO_INLINE __attribute__((noinline))
#endif

/*
 * Vectorize & unroll
 */
#if defined(__clang__)
  #define PRAGMA_LOOP_VECTORIZE _Pragma("clang loop vectorize(enable)")
  #define PRAGMA_UNROLL(n) _Pragma(STRINGIFY(clang loop unroll_count(n)))
#elif defined(__GNUC__)
  #define PRAGMA_LOOP_VECTORIZE _Pragma("GCC ivdep")
  #define PRAGMA_UNROLL(n) _Pragma(STRINGIFY(GCC unroll(n)))
#elif defined(_MSC_VER)
  #define PRAGMA_LOOP_VECTORIZE _Pragma("loop(ivdep)")
  #define PRAGMA_UNROLL(n) //MSVC does not support unroll pragma
#else
  #define PRAGMA_LOOP_VECTORIZE _Pragma("ivdep")
  #define PRAGMA_UNROLL(n) _Pragma(STRINGIFY(unroll(n)))
#endif

/*
 * Popcount macros
 */
#define POPCOUNT_64(word64) __builtin_popcountll((word64))
#define POPCOUNT_32(word32) __builtin_popcount((word32))

/*
 * Prefetch macros
 */
#define PREFETCH(ADDR) __builtin_prefetch(((const char*)ADDR))

/*
 * Display
 */
#define PRINT_CHAR_REP(stream,character,times) { \
  int i; \
  for (i=0;i<times;++i) fprintf(stream,"%c",character); \
}

/*
* Unused variable
*/
#define UNUSED(x) (void)(x)

/*
* Pointer utils
*/
#define OFFSET_VOIDPTR(ptr,offset) ((void*)((uintptr_t)(ptr)+(offset)))
#define NEG_OFFSET_VOIDPTR(ptr,offset) ((void*)((uintptr_t)(ptr)-(offset)))

/*
* VLAs
*/
#ifdef _MSC_VER
  #include <malloc.h>
  #define VLA_INIT(type, name, count) type* name = (type*)_malloca((count) * sizeof(type))
#else
  #define VLA_INIT(type, name, count) type name[count]
#endif