"""
unmhtml - MHTML to HTML converter library

A pure Python library for converting MHTML (MIME HTML) files to standalone HTML 
files with embedded CSS and resources, using only Python standard library modules.
"""

from .converter import MHTMLConverter
from .parser import MHTMLParser
from .processor import HTMLProcessor

__version__ = "0.1.0"
__all__ = ["MHTMLConverter", "MHTMLParser", "HTMLProcessor"]