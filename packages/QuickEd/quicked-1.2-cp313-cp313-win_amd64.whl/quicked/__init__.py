"""
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
"""
def __cpu_supports_simd():
    try:
        import cpuinfo

        info = cpuinfo.get_cpu_info()
        arch = info.get("arch", "").lower()
        if "x86" not in arch:
            return False
        flags = info.get("flags", [])
        return "avx2" in flags and "sse4_1" in flags
    except Exception:
        return False


def __load_compiled_backend(name: str):
    import os
    import importlib.util
    import importlib.machinery

    base_dir = os.path.dirname(__file__)
    backend_dir = os.path.join(base_dir, "backend")
    for ext in importlib.machinery.EXTENSION_SUFFIXES:
        candidate = os.path.join(backend_dir, name + ext)
        if os.path.isfile(candidate):
            loader = importlib.machinery.ExtensionFileLoader(name, candidate)
            spec = importlib.util.spec_from_file_location(
                name, candidate, loader=loader
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError(f"Cannot find compiled backend: {name}")


backend = "_quicked_simd" if __cpu_supports_simd() else "_quicked_scalar"
"""
The name of the backend module to load, determined based on CPU SIMD support.
If the CPU supports AVX2 and SSE4.1, the SIMD-optimized backend ("_quicked_simd") is used.
Otherwise, the scalar backend ("_quicked_scalar") is selected.
"""

__backend_module = __load_compiled_backend(backend)

# Import public symbols
__public_symbols = getattr(
    __backend_module,
    "__all__",
    [k for k in dir(__backend_module) if not k.startswith("_")],
)
globals().update({k: getattr(__backend_module, k) for k in __public_symbols})
__all__ = __public_symbols + ["backend"]

