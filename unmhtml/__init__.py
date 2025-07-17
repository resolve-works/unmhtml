"""
unmhtml - MHTML to HTML converter library

A pure Python library for converting MHTML (MIME HTML) files to standalone HTML 
files with embedded CSS and resources, using only Python standard library modules.

This library provides a simple interface for converting MHTML files (saved web pages)
into standalone HTML files that can be viewed in any web browser without requiring
the original resources to be available.

Basic Usage:
    >>> from unmhtml import MHTMLConverter
    >>> converter = MHTMLConverter()
    >>> 
    >>> # Convert from file
    >>> html_content = converter.convert_file('saved_page.mhtml')
    >>> with open('output.html', 'w') as f:
    ...     f.write(html_content)
    >>> 
    >>> # Convert from string content
    >>> with open('page.mhtml', 'r') as f:
    ...     mhtml_content = f.read()
    >>> html_content = converter.convert(mhtml_content)

Advanced Usage:
    >>> from unmhtml import MHTMLParser, HTMLProcessor
    >>> 
    >>> # Manual parsing and processing
    >>> parser = MHTMLParser(mhtml_content)
    >>> html, resources = parser.parse()
    >>> 
    >>> processor = HTMLProcessor(html, resources)
    >>> html_with_css = processor.embed_css()
    >>> standalone_html = processor.convert_to_data_uris()
"""

from .converter import MHTMLConverter
from .parser import MHTMLParser
from .processor import HTMLProcessor

__version__ = "0.1.0"
__all__ = ["MHTMLConverter", "MHTMLParser", "HTMLProcessor"]