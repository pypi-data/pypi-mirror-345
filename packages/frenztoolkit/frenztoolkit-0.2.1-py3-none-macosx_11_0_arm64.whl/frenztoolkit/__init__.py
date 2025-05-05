"""
Frenz Streaming Toolkit
A toolkit for streaming data from Frenz Brainband
"""

__version__ = "0.2.0"

from .scanner import Scanner
from .streamer import Streamer, validate_product_key

__all__ = ["Scanner", "Streamer", "validate_product_key"] 