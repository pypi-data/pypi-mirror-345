"""
Tax Calculator for FY 2025-26
A simple calculator to compute income tax for India based on old and new regimes.
"""

__version__ = '0.2.1'
__author__ = 'Yousaf Khamza'

from .calculator import (
    calculate_tax_2025_26,
    calculate_old_regime_tax,
    calculate_new_regime_tax,
    get_float_input,
    main
)