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

#ifndef QUICKED_HPP
#define QUICKED_HPP

#include <string>
#include <ctime>

namespace quicked {

    extern "C" {
    #include "quicked/quicked.h"
    }

    class QuickedException : public std::exception {
    private:
        quicked_status_t status;

    public:
        QuickedException(quicked_status_t s) : status(s) {}
        const char* what () const noexcept override {
            return quicked_status_msg(this->status);
        }
    };

    class QuickedAligner {
    public:
        QuickedAligner();
        ~QuickedAligner();

        void align(std::string *pattern, std::string *text);

        void setAlgorithm(quicked_algo_t algo)          { this->aligner.params->algo = algo; };
        void setOnlyScore(bool only_score)              { this->aligner.params->only_score = only_score; };
        void setBandwidth(unsigned int bandwidth)       { this->aligner.params->bandwidth = bandwidth; };
        void setWindowSize(unsigned int window_size)    { this->aligner.params->window_size = window_size; };
        void setOverlapSize(unsigned int overlap_size)  { this->aligner.params->overlap_size = overlap_size; };
        void setForceScalar(bool force_scalar)          { this->aligner.params->force_scalar = force_scalar; };
        void setHEWThreshold(unsigned int hew_threshold);
        void setHEWPercentage(unsigned int hew_percentage);

        int getScore()          { return this->aligner.score; }
        std::string getCigar()  { return std::string((this->aligner.cigar) ? this->aligner.cigar : "NULL"); }

    private:
        quicked_aligner_t aligner;
        quicked_params_t params;
    };
}

#endif // QUICKED_HPP