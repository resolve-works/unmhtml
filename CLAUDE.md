# **unmhtml - MHTML to HTML Converter Library Specification**

This document outlines the requirements and design for a Python library that converts MHTML (MIME HTML) files to standalone HTML files with embedded CSS, using only Python standard library modules.

## **1. Project Goals and Scope**

This library is responsible for:

- Converting MHTML files to standalone HTML files with embedded CSS
- Preserving the original rendered content structure for accurate display
- Providing a pure Python implementation using only standard library modules
- Supporting integration with web applications that need to display archived content

## **2. Technology Stack**

- **Programming Language:** Python 3.8+
- **Package Manager:** uv toolchain
- **Core Libraries:** Built-in Python standard library only
  - `email` module for MIME parsing
  - `base64` for resource decoding
  - `mimetypes` for content type detection
  - `urllib.parse` for URL handling
  - `html` for HTML escaping
  - `re` for text processing
- **No External Dependencies:** Pure stdlib implementation for maximum portability

## **3. MHTML Format Understanding**

MHTML files are structured as MIME multipart documents:

- **Content-Type:** `multipart/related` or `message/rfc822`
- **Main HTML Document:** First part containing the primary HTML content
- **Embedded Resources:** Subsequent parts containing CSS, images, fonts, etc.
- **Resource References:** Content-Location headers link resources to HTML references
- **Encoding:** Resources typically base64-encoded for binary content

## **4. Core Functionality**

### **4.1. MHTML Parser**

**Class: `MHTMLParser`**

```python
import email
import base64
from typing import Dict, Tuple

class MHTMLParser:
    def __init__(self, mhtml_content: str):
        self.mhtml_content = mhtml_content
        
    def parse(self) -> Tuple[str, Dict[str, bytes]]:
        """Parse MHTML and return main HTML + resource map"""
        message = email.message_from_string(self.mhtml_content)
        # Extract main HTML and resources
        return main_html, resources
```

### **4.2. HTML Processor**

**Class: `HTMLProcessor`**

```python
class HTMLProcessor:
    def __init__(self, html_content: str, resources: Dict[str, bytes]):
        self.html_content = html_content
        self.resources = resources
        
    def embed_css(self) -> str:
        """Convert <link> tags to <style> tags with embedded CSS"""
        # Replace external CSS references with inline styles
        return modified_html
        
    def convert_to_data_uris(self) -> str:
        """Convert resource references to data URIs"""
        # Replace src/href attributes with data: URLs
        return modified_html
```

### **4.3. Main Converter**

**Class: `MHTMLConverter`**

```python
class MHTMLConverter:
    def __init__(self, remove_javascript: bool = False):
        """
        Initialize the MHTML converter.
        
        Args:
            remove_javascript: If True, removes potentially dangerous JavaScript content
                              including script tags, event handlers, and javascript: URLs.
                              Default is False to preserve original content.
        """
        self.remove_javascript = remove_javascript
        
    def convert_file(self, mhtml_path: str) -> str:
        """Convert MHTML file to HTML string"""
        with open(mhtml_path, 'r', encoding='utf-8') as f:
            mhtml_content = f.read()
        return self.convert(mhtml_content)
        
    def convert(self, mhtml_content: str) -> str:
        """Convert MHTML content to HTML string"""
        parser = MHTMLParser(mhtml_content)
        main_html, resources = parser.parse()
        
        processor = HTMLProcessor(main_html, resources)
        html_with_css = processor.embed_css()
        final_html = processor.convert_to_data_uris()
        
        # Apply JavaScript removal if requested
        if self.remove_javascript:
            final_html = clean_html_content(final_html)
        
        return final_html
```

## **5. Package Structure**

```
unmhtml/
├── __init__.py
├── parser.py          # MHTMLParser class
├── processor.py       # HTMLProcessor class
├── converter.py       # MHTMLConverter main class
├── utils.py           # Utility functions
└── py.typed           # Type hints marker
```

## **6. API Design**

### **6.1. Simple API**

```python
from unmhtml import MHTMLConverter

# Basic conversion
converter = MHTMLConverter()
html_content = converter.convert_file('page.mhtml')

# Direct content conversion
html_content = converter.convert(mhtml_string)

# Secure conversion with JavaScript removal
secure_converter = MHTMLConverter(remove_javascript=True)
html_content = secure_converter.convert_file('page.mhtml')
```

## **7. Key Features**

- **CSS Embedding:** Convert `<link rel="stylesheet">` to `<style>` tags
- **Resource Embedding:** Convert images/fonts to data URIs
- **URL Resolution:** Handle relative and absolute resource references
- **JavaScript Removal:** Optional security feature to remove script tags, event handlers, and javascript: URLs
- **Error Handling:** Graceful degradation for malformed MHTML
- **Memory Efficient:** Process large files without excessive memory usage

## **8. Security Considerations**

The library provides optional JavaScript removal functionality for secure conversion:

- **Script Tag Removal:** Removes `<script>` tags and their contents
- **Event Handler Removal:** Removes `on*` event handlers (onclick, onload, etc.)
- **JavaScript URL Removal:** Converts `javascript:` URLs to safe `#` anchors
- **Default Behavior:** JavaScript removal is disabled by default to preserve original content
- **Use Cases:** Enable JavaScript removal when displaying untrusted MHTML content

## **9. Testing Strategy**

- **Basic Functionality:** Test MHTML to HTML conversion works
- **Error Handling:** Test graceful handling of malformed input
- **Resource Embedding:** Verify CSS and resources are properly embedded
- **JavaScript Removal:** Test security features work correctly

## **10. Success Criteria**

- **Functionality:** Successfully convert MHTML files to standalone HTML
- **Performance:** Process typical web pages (1-5MB MHTML) efficiently
- **Reliability:** Handle malformed MHTML gracefully
- **Security:** Provide optional JavaScript removal for safe content display
- **Simplicity:** Clean, minimal API with good documentation
- **Portability:** Zero external dependencies, pure Python stdlib

This specification provides a focused foundation for building a lightweight MHTML to HTML converter library called unmhtml using the uv toolchain.