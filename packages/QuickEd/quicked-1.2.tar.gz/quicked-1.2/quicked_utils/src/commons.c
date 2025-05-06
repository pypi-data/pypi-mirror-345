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

/*
 * Random number generator [min,max)
 */
uint64_t rand_iid(
    const uint64_t min,
    const uint64_t max)
{
    const uint64_t n_rand = (uint64_t) rand(); // [0, RAND_MAX]
    const uint64_t range = max - min;
    const uint64_t rem = RAND_MAX % range;
    const uint64_t sample = RAND_MAX / range;
    // Consider the small interval within remainder of RAND_MAX
    if (n_rand < RAND_MAX - rem)
    {
        return min + n_rand / sample;
    }
    else
    {
        return rand_iid(min, max);
    }
}
/*
 * Math
 */
uint32_t nominal_prop_u32(
    const uint32_t base,
    const double factor)
{
    if (0.0 <= factor && factor <= 1.0)
    {
        return (uint32_t)((double)base * factor);
    }
    else
    {
        return (uint32_t)factor;
    }
}
uint64_t nominal_prop_u64(
    const uint64_t base,
    const double factor)
{
    if (0.0 <= factor && factor <= 1.0)
    {
        return (uint64_t)((double)base * factor);
    }
    else
    {
        return (uint64_t)factor;
    }
}

/*
 * String
 */

void reverse_string(const char* in_string, char *out_string, uint64_t lenght)
{
    for (uint64_t i = 0; i < lenght; i++)
    {
        out_string[lenght - 1 - i] = in_string[i];
    }
}

#ifdef _WIN32
static void fseterr(FILE *fp)
{
    struct file { // Undocumented implementation detail
        unsigned char *_ptr;
        unsigned char *_base;
        int _cnt;
        int _flag;
        int _file;
        int _charbuf;
        int _bufsiz;
    };

    #ifndef _IOERR
    #define _IOERR 0x10
    #endif

    ((struct file *)fp)->_flag |= _IOERR;
}

ssize_t getdelim(char **restrict lineptr, size_t *restrict n, int delim, FILE *restrict stream)
{
    if (lineptr == NULL || n == NULL || stream == NULL || (*lineptr == NULL && *n != 0)) {
        errno = EINVAL;
        return -1;
    }
    if (feof(stream) || ferror(stream)) {
        return -1;
    }

    if (*lineptr == NULL) {
        *n = 256;
        *lineptr = malloc(*n);
        if (*lineptr == NULL) {
            fseterr(stream);
            errno = ENOMEM;
            return -1;
        }
    }
    ssize_t nread = 0;
    int c = EOF;
    while (c != delim) {
        c = fgetc(stream);
        if (c == EOF) {
            break;
        }
        if (nread >= (ssize_t)(*n - 1)) {
            size_t newn = *n * 2;
            char *newptr = realloc(*lineptr, newn);
            if (newptr == NULL) {
                fseterr(stream);
                errno = ENOMEM;
                return -1;
            }
            *lineptr = newptr;
            *n = newn;
        }
        (*lineptr)[nread++] = (char)c;
    }
    if (c == EOF && nread == 0) {
        return -1;
    }
    (*lineptr)[nread] = 0;
    return nread;
}

ssize_t getline(char **restrict lineptr, size_t *restrict n, FILE *restrict stream)
{
    return getdelim(lineptr, n, '\n', stream);
}
#endif