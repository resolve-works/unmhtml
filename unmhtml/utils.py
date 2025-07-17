import re
from typing import Optional
from urllib.parse import urlparse, urljoin


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """
    Normalize a URL, handling relative URLs with a base URL.
    
    Resolves relative URLs against a base URL and handles various URL schemes.
    Returns absolute URLs unchanged.
    
    Args:
        url: The URL to normalize
        base_url: Optional base URL for resolving relative URLs
        
    Returns:
        Normalized URL string
        
    Example:
        >>> normalize_url('style.css', 'https://example.com/page.html')
        'https://example.com/style.css'
        >>> normalize_url('https://example.com/image.jpg')
        'https://example.com/image.jpg'
    """
    if not url:
        return ""
    
    # If it's already an absolute URL, return as-is
    if url.startswith(('http://', 'https://', 'data:', 'mailto:', 'tel:')):
        return url
    
    # If we have a base URL, resolve relative URLs
    if base_url:
        return urljoin(base_url, url)
    
    return url


def extract_charset(content_type: str) -> Optional[str]:
    """
    Extract charset from Content-Type header.
    
    Parses the charset parameter from HTTP Content-Type headers.
    
    Args:
        content_type: Content-Type header value
        
    Returns:
        Charset string if found, None otherwise
        
    Example:
        >>> extract_charset('text/html; charset=utf-8')
        'utf-8'
        >>> extract_charset('text/plain')
        None
    """
    if not content_type:
        return None
    
    charset_match = re.search(r'charset\s*=\s*([^;\s]+)', content_type, re.IGNORECASE)
    if charset_match:
        return charset_match.group(1).strip('\'"')
    
    return None


def is_binary_content_type(content_type: str) -> bool:
    """
    Check if a content type represents binary data.
    
    Determines whether a MIME type indicates binary content that should
    be handled differently from text content.
    
    Args:
        content_type: MIME type string to check
        
    Returns:
        True if the content type represents binary data, False otherwise
        
    Example:
        >>> is_binary_content_type('image/jpeg')
        True
        >>> is_binary_content_type('text/html')
        False
    """
    if not content_type:
        return False
    
    # Common binary content types
    binary_types = [
        'image/',
        'audio/',
        'video/',
        'application/octet-stream',
        'application/pdf',
        'application/zip',
        'font/',
        'application/font-',
        'application/x-font-'
    ]
    
    content_type_lower = content_type.lower()
    return any(content_type_lower.startswith(bt) for bt in binary_types)


def clean_html_content(html: str) -> str:
    """
    Clean HTML content by removing potentially dangerous JavaScript elements.
    
    This function removes potentially dangerous JavaScript content from HTML to make it
    safer for display. It performs the following sanitization steps:
    
    1. Removes all <script> tags and their contents (including external script references)
    2. Removes all event handlers (onclick, onload, onmouseover, etc.)
    3. Converts javascript: URLs to safe # anchors
    4. Removes data URIs containing JavaScript
    5. Removes noscript tags (they may contain fallback JavaScript)
    6. Removes SVG script elements
    
    This is used by MHTMLConverter when remove_javascript=True is specified.
    
    Args:
        html: HTML content to clean
        
    Returns:
        Cleaned HTML string with dangerous JavaScript elements removed
        
    Example:
        >>> html = '<div onclick="alert()">Hello</div><script>alert("bad")</script>'
        >>> clean_html_content(html)
        '<div>Hello</div>'
        
        >>> html = '<a href="javascript:alert()">Link</a>'
        >>> clean_html_content(html)
        '<a href="#">Link</a>'
    """
    # Remove script tags (both inline and external) for security
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove noscript tags as they may contain fallback JavaScript
    html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove SVG script elements
    html = re.sub(r'<svg[^>]*>.*?<script[^>]*>.*?</script>.*?</svg>', 
                  lambda m: re.sub(r'<script[^>]*>.*?</script>', '', m.group(0), flags=re.DOTALL | re.IGNORECASE),
                  html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove on* event handlers (comprehensive list)
    event_handlers = [
        'onabort', 'onbeforeunload', 'onblur', 'onchange', 'onclick', 'oncontextmenu',
        'oncopy', 'oncut', 'ondblclick', 'ondrag', 'ondragend', 'ondragenter',
        'ondragleave', 'ondragover', 'ondragstart', 'ondrop', 'onerror', 'onfocus',
        'onhashchange', 'oninput', 'onkeydown', 'onkeypress', 'onkeyup', 'onload',
        'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup',
        'onmousewheel', 'onoffline', 'ononline', 'onpaste', 'onreset', 'onresize',
        'onscroll', 'onselect', 'onstorage', 'onsubmit', 'onunload', 'onwheel'
    ]
    
    for handler in event_handlers:
        html = re.sub(rf'\s+{handler}\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs from href attributes
    html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs from src attributes
    html = re.sub(r'src\s*=\s*["\']javascript:[^"\']*["\']', 'src="#"', html, flags=re.IGNORECASE)
    
    # Remove data URIs containing JavaScript
    html = re.sub(r'(src|href)\s*=\s*["\']data:[^"\']*javascript[^"\']*["\']', r'\1="#"', html, flags=re.IGNORECASE)
    
    # Remove expression() CSS (IE-specific JavaScript in CSS)
    html = re.sub(r'expression\s*\([^)]*\)', '', html, flags=re.IGNORECASE)
    
    return html


def is_javascript_file(url: str, content_type: str = None) -> bool:
    """
    Check if a resource is a JavaScript file.
    
    Determines if a resource should be considered JavaScript based on URL extension
    and/or content type. Used for filtering JavaScript resources when remove_javascript=True.
    
    Args:
        url: URL or filename to check
        content_type: Optional MIME type to check
        
    Returns:
        True if the resource is a JavaScript file, False otherwise
        
    Example:
        >>> is_javascript_file('app.js')
        True
        >>> is_javascript_file('style.css')
        False
        >>> is_javascript_file('unknown', 'text/javascript')
        True
    """
    if not url:
        return False
    
    # Check file extension
    url_lower = url.lower()
    js_extensions = ['.js', '.mjs', '.jsx', '.ts', '.tsx']
    if any(url_lower.endswith(ext) for ext in js_extensions):
        return True
    
    # Check content type if provided
    if content_type:
        content_type_lower = content_type.lower()
        js_content_types = [
            'text/javascript',
            'application/javascript',
            'application/x-javascript',
            'text/ecmascript',
            'application/ecmascript'
        ]
        if any(js_type in content_type_lower for js_type in js_content_types):
            return True
    
    return False


def extract_filename_from_url(url: str) -> str:
    """
    Extract filename from URL.
    
    Parses a URL to extract the filename component, handling query parameters
    and path structures.
    
    Args:
        url: URL to extract filename from
        
    Returns:
        Filename string, empty string if no filename found
        
    Example:
        >>> extract_filename_from_url('https://example.com/path/file.css?v=1')
        'file.css'
        >>> extract_filename_from_url('https://example.com/path/')
        ''
    """
    if not url:
        return ""
    
    # Parse the URL
    parsed = urlparse(url)
    path = parsed.path
    
    # Get the last part of the path
    if path and '/' in path:
        filename = path.split('/')[-1]
    else:
        filename = path
    
    # Remove query parameters
    if '?' in filename:
        filename = filename.split('?')[0]
    
    return filename if filename else ""