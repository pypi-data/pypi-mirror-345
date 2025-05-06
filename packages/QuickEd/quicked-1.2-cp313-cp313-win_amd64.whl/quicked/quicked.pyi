from __future__ import annotations
import typing
__all__ = ['QuickedAlgo', 'QuickedAligner', 'QuickedException']
class QuickedAlgo:
    """
    QuickedAlgo
    ===========

    Enumeration of alignment algorithms.

    Attributes:
        QUICKED (QuickedAlgo): QuickEd algorithm.
        WINDOWED (QuickedAlgo): WindowEd algorithm.
        BANDED (QuickedAlgo): BandEd algorithm.
        HIRSCHBERG (QuickedAlgo): Hirschberg algorithm.
    """
    BANDED: typing.ClassVar[QuickedAlgo]  # value = <QuickedAlgo.BANDED: 2>
    HIRSCHBERG: typing.ClassVar[QuickedAlgo]  # value = <QuickedAlgo.HIRSCHBERG: 3>
    QUICKED: typing.ClassVar[QuickedAlgo]  # value = <QuickedAlgo.QUICKED: 0>
    WINDOWED: typing.ClassVar[QuickedAlgo]  # value = <QuickedAlgo.WINDOWED: 1>
    __members__: typing.ClassVar[dict[str, QuickedAlgo]]  # value = {'QUICKED': <QuickedAlgo.QUICKED: 0>, 'WINDOWED': <QuickedAlgo.WINDOWED: 1>, 'BANDED': <QuickedAlgo.BANDED: 2>, 'HIRSCHBERG': <QuickedAlgo.HIRSCHBERG: 3>}

class QuickedAligner:
    """
    QuickedAligner
    ==============

    This class defines an aligner object that can be used to perform sequence alignment.
    It is initialized with default parameters and can be configured using various setter methods.

    """
    def __init__(self) -> None:
        ...
    def align(self, pattern: str, text: str) -> None:
        """
        Aligns the provided pattern and text according to the current parameters
        """
    def getCigar(self) -> str:
        """
        Gets the CIGAR string representing the alignment
        """
    def getScore(self) -> int:
        """
        Gets the alignment score
        """
    def setAlgorithm(self, algorithm: QuickedAlgo) -> None:
        """
        Sets the algorithm to be used for alignment
        """
    def setBandwidth(self, bandwidth: int) -> None:
        """
        Sets the bandwidth for BandEd alignment
        """
    def setForceScalar(self, force_scalar: bool) -> None:
        """
        Forces scalar computation (i.e., no SIMD instructions)
        """
    def setHEWPercentage(self, hew_percentage: int) -> None:
        """
        Sets the HEW percentage
        """
    def setHEWThreshold(self, hew_threshold: int) -> None:
        """
        Sets the HEW threshold
        """
    def setOnlyScore(self, only_score: bool) -> None:
        """
        Sets whether only the score should be computed
        """
    def setOverlapSize(self, overlap_size: int) -> None:
        """
        Sets the overlap size for WindowEd alignment
        """
    def setWindowSize(self, window_size: int) -> None:
        """
        Sets the window size for WindowEd alignment
        """

class QuickedException(Exception):
    pass
