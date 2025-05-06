QuickEd
&nbsp;
[![Release](https://img.shields.io/github/release/maxdoblas/quicked.svg)](https://github.com/maxdoblas/quicked/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/maxdoblas/quicked/build_and_test.yaml)](https://github.com/maxdoblas/QuickEd/actions/workflows/build_and_test.yaml)
[![Publication](https://img.shields.io/badge/Published%20in-Bioinformatics-167DA4.svg)](https://doi.org/10.1093/bioinformatics/btaf112)
=====

QuickEd is a high-performance exact sequence alignment library based on the bound-and-align paradigm.
Currently, QuickEd focuses on DNA sequence alignment (A, C, G, T, N), using the edit distance (Levenshtein distance) metric.

```py
from quicked import QuickedAligner, QuickedException

pattern = "ACGT" # Pattern sequence
text = "ACTT"    # Text sequence
score = -1       # Alignment score
cigar = ""       # CIGAR string

try:
    aligner = QuickedAligner()    # Aligner object, with sensible default parameters
    # Without any extra configuration, the aligner will use the Quicked algorithm

    aligner.align(pattern, text)  # Align the sequences!

    score = aligner.getScore()    # Get the score
    cigar = aligner.getCigar()    # Get the CIGAR string
except QuickedException as e:
    print(e)

print(f"Score: {score}") # Print the score
print(f"Cigar: {cigar}") # Print the CIGAR string
```

QuickEd is actually a C library, and this package is it’s wrapper for Python.
Check out [QuickEd's GitHub](https://github.com/maxdoblas/QuickEd) for more code examples and more details on how QuickEd works.

## Features

* Calculates **edit distance (Levenshtein distance)**.
* It can find **optimal alignment path** (instructions on how to transform the first sequence into the second sequence).
* Supports **multiple alignment algorithms**:
  * QuickEd
  * BandEd
  * WindowEd
* Efficient implementation of the bound-and-align paradigm.
* It scales to **long and noisy sequences**, even when finding an alignment path, while consuming very little memory thanks to the Hirschberg algorithm.

**IMPORTANT!**
As QuickEd focuses on DNA sequence alignment, expected alphabet characters are limited to A, C, G, T, and N.
However, no check is performed on the input sequences for performance reasons.

## Installation

### PyPI

QuickEd is available on [PyPI](https://pypi.org/project/quicked/), so you can install it using pip:

```bash
pip install quicked
```

### Conda

Conda support is still in progress.

### From source

To install the Python bindings from source, you can simply run `pip install .` from the **root** directory of the [QuickEd](https://github.com/maxdoblas/QuickEd) repository. This will build and install the bindings for your current Python environment.

## API

Take a look at [basic.py](../../examples/bindings/basic.py) for a minimal example.

### QuickedAlgo

Enum that defines the alignment algorithm to use. The available algorithms are:

* `QUICKED`: QuickEd algorithm (default)
* `BANDED`: BandEd algorithm
* `WINDOWED`: WindowEd algorithm
* `HIRSCHBERG`: Hirschberg algorithm

### QuickedAligner

This class defines an aligner object that can be used to perform sequence alignment.
It is initialized with default parameters and can be configured using various setter methods.

```py
aligner = QuickedAligner()
```

#### `align(pattern, text)`

Aligns the provided pattern and text according to the current parameters.

* **Parameters**:
  * `pattern` *(str)*: The pattern to be aligned.
  * `text` *(str)*: The text to be aligned against.

#### `setAlgorithm(algorithm)`

Sets the algorithm to be used for alignment.

* **Parameters**:
  * `algorithm` *(QuickedAlgo)*: The alignment algorithm to use.

#### `setOnlyScore(only_score)`

Sets whether only the score should be computed.

* **Parameters**:
  * `only_score` *(bool)*: A boolean indicating if only the score should be computed.

#### `setBandwidth(bandwidth)`

Sets the bandwidth for BandEd alignment.

* **Parameters**:
  * `bandwidth` *(int)*: The bandwidth value to set.

#### `setWindowSize(window_size)`

Sets the window size for WindowEd alignment.

* **Parameters**:
  * `window_size` *(int)*: The window size value to set.

#### `setOverlapSize(overlap_size)`

Sets the overlap size for WindowEd alignment.

* **Parameters**:
  * `overlap_size` *(int)*: The overlap size value to set.

#### `setForceScalar(force_scalar)`

Forces scalar computation (i.e., no SIMD instructions).

* **Parameters**:
  * `force_scalar` *(bool)*: A boolean indicating whether to force scalar computation.

#### `setHEWThreshold(hew_threshold)`

Sets the HEW threshold.

* **Parameters**:
  * `hew_threshold` *(float)*: The HEW threshold value to set.

#### `setHEWPercentage(hew_percentage)`

Sets the HEW percentage.

* **Parameters**:
  * `hew_percentage` *(float)*: The HEW percentage value to set.

#### `getScore()`

Gets the alignment score.

* **Returns**:
  * *(float)*: The alignment score as a numeric value.

#### `getCigar()`

Gets the CIGAR string representing the alignment.

* **Returns**:
  * *(str)*: A string representing the alignment in CIGAR format.
