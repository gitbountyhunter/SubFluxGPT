"""
Benchmarking module for SubFluxGPT.
Compares local models with external APIs.
"""

# Lazy imports to avoid requiring all dependencies for basic module import
__all__ = ['BenchmarkResult', 'BenchmarkRunner']

def __getattr__(name):
    if name == 'BenchmarkResult':
        from .benchmark_runner import BenchmarkResult
        return BenchmarkResult
    if name == 'BenchmarkRunner':
        from .benchmark_runner import BenchmarkRunner
        return BenchmarkRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
