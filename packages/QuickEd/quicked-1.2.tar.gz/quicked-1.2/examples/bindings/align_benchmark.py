#!/usr/bin/env python3

import sys
import timeit

from quicked import QuickedAligner, QuickedException, backend

if len(sys.argv) < 2:
    print("Usage: python3 test.py <input_file>")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, 'r') as f:
        lines = f.readlines()
        if len(lines) % 2 != 0:
            print("Error: Input file must contain an even number of lines.")
            sys.exit(1)
except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
    sys.exit(1)

def align_sequences():
    aligner = QuickedAligner()  # Aligner object, with sensible default parameters

    for i in range(0, len(lines), 2):
        pattern = lines[i][1:].strip()  # Drop the first character and strip whitespace
        text = lines[i + 1][1:].strip()  # Drop the first character and strip whitespace

        try:
            aligner.align(pattern, text)  # Align the sequences!

            score = aligner.getScore()  # Get the score
            cigar = aligner.getCigar()  # Get the CIGAR string

            # print(f"Pair {i // 2 + 1}:")
            print(f"Score: {score}")
            # print(f"CIGAR: {cigar}")
        except QuickedException as e:
            print(f"Error in pair {i // 2 + 1}: {e}")

try:
    print("Using backend:", backend)
    execution_time = timeit.timeit(align_sequences, number=1)
    print(f"Execution time: {execution_time:.2f} seconds")
except QuickedException as e:
    print(e)
