import re
from typing import Optional
from urllib.parse import urlparse, urljoin


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Normalize a URL, handling relative URLs with a base URL"""
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
    """Extract charset from Content-Type header"""
    if not content_type:
        return None
    
    charset_match = re.search(r'charset\s*=\s*([^;\s]+)', content_type, re.IGNORECASE)
    if charset_match:
        return charset_match.group(1).strip('\'"')
    
    return None


def is_binary_content_type(content_type: str) -> bool:
    """Check if a content type represents binary data"""
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
    """Clean HTML content by removing problematic elements"""
    # Remove script tags for security
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove on* event handlers
    html = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', html, flags=re.IGNORECASE)
    
    return html


def extract_filename_from_url(url: str) -> str:
    """Extract filename from URL"""
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