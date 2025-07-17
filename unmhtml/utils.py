import re


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


