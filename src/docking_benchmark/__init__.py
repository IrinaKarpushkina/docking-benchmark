"""
Docking Benchmark Suite

A reproducible benchmark for comparing molecular docking methods.
"""

__version__ = "0.1.0"
__author__ = "Docking Benchmark Team"

from .config import load_config
from .main import DockingBenchmark

__all__ = ["DockingBenchmark", "load_config"]










