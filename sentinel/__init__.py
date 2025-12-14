"""
Sentinel - EVE Online Intelligence Analysis Engine

A read-only intelligence analysis engine for EVE Online recruitment vetting.
"""

from sentinel.analyzer import SentinelAnalyzer
from sentinel.models.analysis_result import AnalysisResult

__version__ = "0.1.0"
__all__ = ["SentinelAnalyzer", "AnalysisResult"]
