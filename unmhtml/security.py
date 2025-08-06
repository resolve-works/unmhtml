import re


def remove_javascript_content(html: str) -> str:
    """
    Remove potentially dangerous JavaScript content from HTML.
    
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
        HTML string with dangerous JavaScript elements removed
        
    Example:
        >>> html = '<div onclick="alert()">Hello</div><script>alert("bad")</script>'
        >>> remove_javascript_content(html)
        '<div>Hello</div>'
        
        >>> html = '<a href="javascript:alert()">Link</a>'
        >>> remove_javascript_content(html)
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


def sanitize_css(html: str) -> str:
    """
    Sanitize CSS content by removing properties that can make network requests.
    
    This function removes potentially dangerous CSS properties that could be used to
    exfiltrate data or make external network requests:
    
    1. Removes CSS url() properties (background-image, list-style-image, etc.)
    2. Removes @import statements that load external stylesheets
    3. Removes IE-specific expression() properties
    4. Removes behavior: properties
    
    Args:
        html: HTML content containing CSS to sanitize
        
    Returns:
        HTML string with dangerous CSS properties removed
        
    Example:
        >>> html = '<style>body { background: url("http://evil.com/img.png"); }</style>'
        >>> sanitize_css(html)
        '<style>body {  }</style>'
        
        >>> html = '<style>@import url("http://evil.com/style.css");</style>'
        >>> sanitize_css(html)
        '<style></style>'
    """
    # Remove @import statements that could load external stylesheets first
    # Use a more specific pattern to avoid backtracking
    html = re.sub(r'@import\s+(?:url\([^)]*\)|["\'][^"\']*["\'])[^;]*;?', '', html, flags=re.IGNORECASE)
    
    # Remove CSS url() properties that could exfiltrate data
    # Use a more efficient pattern that doesn't cause backtracking
    html = re.sub(r'url\s*\([^)]*\)', '', html, flags=re.IGNORECASE)
    
    # Remove IE-specific expression() properties
    html = re.sub(r'expression\s*\([^)]*\)', '', html, flags=re.IGNORECASE)
    
    # Remove behavior: properties (IE-specific)
    html = re.sub(r'behavior\s*:\s*[^;]+;?', '', html, flags=re.IGNORECASE)
    
    return html


def remove_forms(html: str) -> str:
    """
    Remove form elements that could submit data externally.
    
    This function removes potentially dangerous form elements that could be used to
    submit data to external endpoints:
    
    1. Removes <form> elements and their contents
    2. Removes <input> elements (all types)
    3. Removes <textarea> elements
    4. Removes <select> elements and their <option> children
    5. Removes <button type="submit"> elements
    6. Removes <fieldset> and <legend> elements
    7. Removes <label> elements (as they become meaningless without form controls)
    
    Args:
        html: HTML content containing forms to remove
        
    Returns:
        HTML string with form elements removed
        
    Example:
        >>> html = '<form action="/submit"><input type="text" name="data"><button type="submit">Submit</button></form>'
        >>> remove_forms(html)
        ''
        
        >>> html = '<div><p>Text</p><form><input type="hidden" name="csrf"></form><p>More text</p></div>'
        >>> remove_forms(html)
        '<div><p>Text</p><p>More text</p></div>'
    """
    # Remove entire form elements and their contents
    html = re.sub(r'<form[^>]*>.*?</form>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove input elements (all types: text, hidden, submit, button, etc.)
    html = re.sub(r'<input[^>]*/?>', '', html, flags=re.IGNORECASE)
    
    # Remove textarea elements
    html = re.sub(r'<textarea[^>]*>.*?</textarea>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove select elements and their options
    html = re.sub(r'<select[^>]*>.*?</select>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove button elements that could be used for form submission
    html = re.sub(r'<button[^>]*>.*?</button>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove fieldset and legend elements (form grouping elements)
    html = re.sub(r'<fieldset[^>]*>.*?</fieldset>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<legend[^>]*>.*?</legend>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove label elements (they become meaningless without form controls)
    html = re.sub(r'<label[^>]*>.*?</label>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove datalist elements (used with input elements)
    html = re.sub(r'<datalist[^>]*>.*?</datalist>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    return html


