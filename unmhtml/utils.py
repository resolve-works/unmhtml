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
    Clean HTML content by removing potentially problematic elements.
    
    Removes script tags, event handlers, and javascript: URLs for security.
    This helps create safer standalone HTML files.
    
    Args:
        html: HTML content to clean
        
    Returns:
        Cleaned HTML string with problematic elements removed
        
    Example:
        >>> clean_html_content('<div onclick="alert()">Hello</div>')
        '<div>Hello</div>'
    """
    # Remove script tags for security
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove on* event handlers
    html = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', html, flags=re.IGNORECASE)
    
    return html


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