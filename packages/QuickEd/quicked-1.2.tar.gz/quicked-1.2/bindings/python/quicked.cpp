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

#include <pybind11/pybind11.h>
#include "quicked.hpp"

namespace py = pybind11;
using namespace py::literals;

#ifndef PY_MODULE_NAME
#define PY_MODULE_NAME _quicked
#endif

namespace quicked {
    PYBIND11_MODULE(PY_MODULE_NAME, m) {
        m.doc() = R"pbdoc(
QuickEd - A high-performance exact sequence alignment based on the bound-and-align paradigm
===========================================================================================

QuickEd is a high-performance exact sequence alignment based on the bound-and-align paradigm.
Currently, QuickEd focuses on DNA sequence alignment, using the edit distance (Levenshtein distance) metric.

    >>> pattern = "ACGT"
    >>> text = "ACTT"
    >>> aligner = quicked.QuickedAligner()
    >>> aligner.align(pattern, text)
    >>> score = aligner.getScore()
    >>> cigar = aligner.getCigar()

QuickEd is actually a C library, and this package is it’s wrapper for Python.
Check out QuickEd's GitHub for more code examples and more details on how QuickEd works.
)pbdoc";

        py::enum_<quicked_algo_t>(m, "QuickedAlgo",
            R"pbdoc(
QuickedAlgo
===========

Enumeration of alignment algorithms
            )pbdoc")
            .value("QUICKED", QUICKED, R"pbdoc(QuickEd algorithm)pbdoc")
            .value("WINDOWED", WINDOWED, R"pbdoc(WindowEd algorithm)pbdoc")
            .value("BANDED", BANDED, R"pbdoc(BandEd algorithm)pbdoc")
            .value("HIRSCHBERG", HIRSCHBERG, R"pbdoc(Hirschberg algorithm)pbdoc");

        py::class_<QuickedAligner>(m, "QuickedAligner",
            R"pbdoc(
QuickedAligner
==============

This class defines an aligner object that can be used to perform sequence alignment.
It is initialized with default parameters and can be configured using various setter methods.
            )pbdoc")
            .def(py::init<>())
            .def("align", &QuickedAligner::align, "pattern"_a, "text"_a,
            R"pbdoc(Aligns the provided pattern and text according to the current parameters)pbdoc")
            .def("setAlgorithm", &QuickedAligner::setAlgorithm, "algorithm"_a,
            R"pbdoc(Sets the algorithm to be used for alignment)pbdoc")
            .def("setOnlyScore", &QuickedAligner::setOnlyScore, "only_score"_a,
            R"pbdoc(Sets whether only the score should be computed)pbdoc")
            .def("setBandwidth", &QuickedAligner::setBandwidth, "bandwidth"_a,
            R"pbdoc(Sets the bandwidth for BandEd alignment)pbdoc")
            .def("setWindowSize", &QuickedAligner::setWindowSize, "window_size"_a,
            R"pbdoc(Sets the window size for WindowEd alignment)pbdoc")
            .def("setOverlapSize", &QuickedAligner::setOverlapSize, "overlap_size"_a,
            R"pbdoc(Sets the overlap size for WindowEd alignment)pbdoc")
            .def("setForceScalar", &QuickedAligner::setForceScalar, "force_scalar"_a,
            R"pbdoc(Forces scalar computation (i.e., no SIMD instructions))pbdoc")
            .def("setHEWThreshold", &QuickedAligner::setHEWThreshold, "hew_threshold"_a,
            R"pbdoc(Sets the HEW threshold)pbdoc")
            .def("setHEWPercentage", &QuickedAligner::setHEWPercentage, "hew_percentage"_a,
            R"pbdoc(Sets the HEW percentage)pbdoc")
            .def("getScore", &QuickedAligner::getScore, R"pbdoc(Gets the alignment score)pbdoc")
            .def("getCigar", &QuickedAligner::getCigar, R"pbdoc(Gets the CIGAR string representing the alignment)pbdoc");

        py::register_exception<QuickedException>(m, "QuickedException");
    }
}