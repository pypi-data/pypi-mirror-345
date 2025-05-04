"""
pstatstools: A comprehensive package for statistical analysis.

This package provides tools for sampling, distributions, hypothesis testing,
categorical data analysis, and error propagation. The main sample function
is exposed directly at the package level for convenience.
"""

from .samples import sample
from .distributions import distribution

from . import distributions
from . import samples
from . import inferential
from . import categorical
from . import nonparametric
from . import probability
from . import error_propagation

__all__ = [
    # Core functions
    'sample',
    'distribution',
    
    # Submodules
    'distributions',
    'samples',
    'inferential',
    'categorical',
    'nonparametric',
    'probability',
    'error_propagation'
]