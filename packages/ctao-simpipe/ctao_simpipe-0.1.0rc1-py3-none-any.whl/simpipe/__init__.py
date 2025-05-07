"""SimPipe: CTAO Simulation Processing Pipeline.

SimPipe is a pipeline subsystem of DPPS.
"""
from simtools import __version__ as simtools_version

from .version import __version__

__all__ = [
    "__version__",
    "simtools_version",
]
