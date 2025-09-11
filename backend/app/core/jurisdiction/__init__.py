"""
Jurisdiction detection and management system for legal documents.

This module provides comprehensive jurisdiction detection capabilities for Indian and US legal documents,
including state-level detection, confidence scoring, and jurisdiction-specific processing.
"""

from .detector import JurisdictionDetector, JurisdictionResult
from .indian_processor import IndianLegalProcessor
from .us_processor import USLegalProcessor
from .comparative_analyzer import ComparativeJurisdictionAnalyzer

__all__ = [
    'JurisdictionDetector',
    'JurisdictionResult', 
    'IndianLegalProcessor',
    'USLegalProcessor',
    'ComparativeJurisdictionAnalyzer'
]