"""
GPP Prediction Package

A package for predicting gross primary production (GPP) based on ecological parameters.
"""

from .core import (
    swrad2par,
    get_tmin_func,
    get_vpd_func,
    calc_gpp,
)

__all__ = [
    "swrad2par",
    "get_tmin_func",
    "get_vpd_func",
    "calc_gpp",
]

__version__ = "0.1.5"
