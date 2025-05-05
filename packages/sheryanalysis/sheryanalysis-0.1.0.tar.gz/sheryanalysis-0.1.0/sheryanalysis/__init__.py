"""
SheryAnalysis - A simple and powerful EDA library
================================================

SheryAnalysis provides tools for exploratory data analysis with a focus on
simplicity and intelligent defaults.

Main Components:
---------------
- analyze: Main function for basic data analysis
- Imputer: Class for handling missing values with various strategies

Example:
-------
>>> import pandas as pd
>>> from sheryanalysis import analyze
>>> df = pd.read_csv("data.csv")
>>> analyze(df)
>>> analyze.fill_nulls_all(df)
"""

__version__ = "0.1.0"

from .analyzer import analyze
from .imputer import Imputer