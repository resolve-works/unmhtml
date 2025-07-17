from .parser import MHTMLParser
from .processor import HTMLProcessor
from .security import remove_javascript_content, sanitize_css, remove_forms


class MHTMLConverter:
    """
    Main converter class for converting MHTML files to standalone HTML files.
    
    This class provides the primary interface for converting MHTML (MIME HTML) files
    to standalone HTML files with embedded CSS and resources. It handles the entire
    conversion process including parsing, resource embedding, and error handling.
    
    Args:
        remove_javascript: If True, removes script tags, event handlers, and javascript: URLs
                          for security. Default is False to preserve original content.
        sanitize_css: If True, removes CSS properties that can make network requests
                     (url(), @import, expression(), behavior:). Default is False.
        remove_forms: If True, removes form elements that could submit data externally.
                     Default is False.
    
    Example:
        >>> converter = MHTMLConverter()
        >>> html_content = converter.convert_file('example.mhtml')
        >>> # Or convert from string content with JavaScript removed
        >>> secure_converter = MHTMLConverter(remove_javascript=True)
        >>> html_content = secure_converter.convert(mhtml_string)
        >>> # Or convert with CSS sanitization enabled
        >>> css_safe_converter = MHTMLConverter(sanitize_css=True)
        >>> html_content = css_safe_converter.convert(mhtml_string)
    """
    
    def __init__(self, remove_javascript: bool = False, sanitize_css: bool = False, remove_forms: bool = False):
        """
        Initialize the MHTML converter.
        
        Args:
            remove_javascript: If True, removes potentially dangerous JavaScript content
                              including script tags, event handlers, and javascript: URLs.
                              Default is False to preserve original content.
            sanitize_css: If True, removes CSS properties that can make network requests
                         (url(), @import, expression(), behavior:). Default is False.
            remove_forms: If True, removes form elements that could submit data externally.
                         Default is False.
        """
        self.remove_javascript = remove_javascript
        self.sanitize_css = sanitize_css
        self.remove_forms = remove_forms
    def convert_file(self, mhtml_path: str) -> str:
        """
        Convert an MHTML file to a standalone HTML string.
        
        Args:
            mhtml_path: Path to the MHTML file to convert
            
        Returns:
            Standalone HTML string with embedded CSS and resources
            
        Raises:
            ValueError: If the file cannot be read or processed
            FileNotFoundError: If the specified file does not exist
            
        Example:
            >>> converter = MHTMLConverter()
            >>> html = converter.convert_file('saved_page.mhtml')
            >>> with open('output.html', 'w') as f:
            ...     f.write(html)
        """
        try:
            with open(mhtml_path, 'r', encoding='utf-8') as f:
                mhtml_content = f.read()
            return self.convert(mhtml_content)
        except Exception as e:
            raise ValueError(f"Failed to read MHTML file: {e}")
        
    def convert(self, mhtml_content: str) -> str:
        """
        Convert MHTML content string to a standalone HTML string.
        
        Args:
            mhtml_content: Raw MHTML content as a string
            
        Returns:
            Standalone HTML string with embedded CSS and resources
            
        Raises:
            ValueError: If the MHTML content is malformed or cannot be processed
            
        Example:
            >>> with open('page.mhtml', 'r') as f:
            ...     mhtml_content = f.read()
            >>> converter = MHTMLConverter()
            >>> html = converter.convert(mhtml_content)
        """
        try:
            # Parse MHTML to extract HTML and resources
            parser = MHTMLParser(mhtml_content)
            main_html, resources = parser.parse()
            
            # If we got the original content back, it means the MHTML is malformed
            if main_html == mhtml_content:
                raise ValueError("No HTML content found in MHTML")
            
            if not main_html:
                raise ValueError("No HTML content found in MHTML")
            
            # Process HTML to embed CSS and convert resources
            # Pass remove_javascript flag to filter JavaScript files from resources
            processor = HTMLProcessor(main_html, resources, remove_javascript=self.remove_javascript)
            html_with_css = processor.embed_css()
            processor.html_content = html_with_css  # Update processor with embedded CSS
            final_html = processor.convert_to_data_uris()
            
            # Apply security sanitization if requested
            if self.remove_javascript:
                final_html = remove_javascript_content(final_html)
            
            if self.sanitize_css:
                final_html = sanitize_css(final_html)
            
            if self.remove_forms:
                final_html = remove_forms(final_html)
            
            return final_html
            
        except Exception as e:
            raise ValueError(f"Failed to convert MHTML: {e}")