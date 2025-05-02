"""
Gemini Profanity Filter

A Python module for detecting and filtering profanity in text using Google's Gemini API.
"""

from .profanity_filter import ProfanityFilter, FilterResult, ProfanityInstance

__version__ = "0.1.0"
__all__ = ["ProfanityFilter", "FilterResult", "ProfanityInstance"]