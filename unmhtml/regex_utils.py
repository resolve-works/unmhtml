import re
from typing import Pattern, List


# Common regex flags used throughout the application
COMMON_FLAGS = re.DOTALL | re.IGNORECASE
IGNORECASE_ONLY = re.IGNORECASE


class RegexPatterns:
    """
    Centralized collection of regex patterns used across the MHTML converter.
    
    This class provides compiled regex patterns and common operations to avoid
    duplication and ensure consistency across the codebase.
    """
    
    # JavaScript removal patterns
    SCRIPT_TAGS = re.compile(r'<script[^>]*>.*?</script>', COMMON_FLAGS)
    NOSCRIPT_TAGS = re.compile(r'<noscript[^>]*>.*?</noscript>', COMMON_FLAGS)
    SVG_SCRIPT_TAGS = re.compile(r'<svg[^>]*>.*?<script[^>]*>.*?</script>.*?</svg>', COMMON_FLAGS)
    JAVASCRIPT_URLS_HREF = re.compile(r'href\s*=\s*["\']javascript:[^"\']*["\']', IGNORECASE_ONLY)
    JAVASCRIPT_URLS_SRC = re.compile(r'src\s*=\s*["\']javascript:[^"\']*["\']', IGNORECASE_ONLY)
    DATA_URI_JAVASCRIPT = re.compile(r'(src|href)\s*=\s*["\']data:[^"\']*javascript[^"\']*["\']', IGNORECASE_ONLY)
    EXPRESSION_CSS = re.compile(r'expression\s*\([^)]*\)', IGNORECASE_ONLY)
    
    # CSS sanitization patterns
    CSS_IMPORT = re.compile(r'@import\s+(?:url\([^)]*\)|["\'][^"\']*["\'])[^;]*;?', IGNORECASE_ONLY)
    CSS_URL = re.compile(r'url\s*\([^)]*\)', IGNORECASE_ONLY)
    CSS_BEHAVIOR = re.compile(r'behavior\s*:\s*[^;]+;?', IGNORECASE_ONLY)
    
    # Form removal patterns
    FORM_TAGS = re.compile(r'<form[^>]*>.*?</form>', COMMON_FLAGS)
    INPUT_TAGS = re.compile(r'<input[^>]*/?>', IGNORECASE_ONLY)
    TEXTAREA_TAGS = re.compile(r'<textarea[^>]*>.*?</textarea>', COMMON_FLAGS)
    SELECT_TAGS = re.compile(r'<select[^>]*>.*?</select>', COMMON_FLAGS)
    BUTTON_TAGS = re.compile(r'<button[^>]*>.*?</button>', COMMON_FLAGS)
    FIELDSET_TAGS = re.compile(r'<fieldset[^>]*>.*?</fieldset>', COMMON_FLAGS)
    LEGEND_TAGS = re.compile(r'<legend[^>]*>.*?</legend>', COMMON_FLAGS)
    LABEL_TAGS = re.compile(r'<label[^>]*>.*?</label>', COMMON_FLAGS)
    DATALIST_TAGS = re.compile(r'<datalist[^>]*>.*?</datalist>', COMMON_FLAGS)
    
    # Meta tag removal patterns
    META_REFRESH = re.compile(r'<meta[^>]*http-equiv\s*=\s*["\']?refresh["\']?[^>]*>', IGNORECASE_ONLY)
    META_SET_COOKIE = re.compile(r'<meta[^>]*http-equiv\s*=\s*["\']?set-cookie["\']?[^>]*>', IGNORECASE_ONLY)
    META_DNS_PREFETCH = re.compile(r'<meta[^>]*name\s*=\s*["\']?dns-prefetch["\']?[^>]*>', IGNORECASE_ONLY)
    
    # HTML processing patterns
    LINK_STYLESHEET = re.compile(r'<link\s+[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*>', IGNORECASE_ONLY)
    HREF_ATTRIBUTE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', IGNORECASE_ONLY)
    SRC_ATTRIBUTE = re.compile(r'(src\s*=\s*["\'])([^"\']+)(["\'])', IGNORECASE_ONLY)
    HREF_NON_CSS = re.compile(r'(href\s*=\s*["\'])([^"\']+)(["\'])(?![^<]*rel\s*=\s*["\']stylesheet["\'])', IGNORECASE_ONLY)
    CSS_URL_REFERENCES = re.compile(r'url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)', IGNORECASE_ONLY)
    FAVICON_LINKS = re.compile(r'<link\s+[^>]*rel\s*=\s*["\'](?:icon|apple-touch-icon)["\'][^>]*>', IGNORECASE_ONLY)


def remove_html_tags(html: str, patterns: List[Pattern]) -> str:
    """
    Generic HTML tag removal utility.
    
    Applies multiple regex patterns to remove HTML tags from content.
    This consolidates the common pattern of applying multiple regex
    substitutions with empty string replacement.
    
    Args:
        html: HTML content to process
        patterns: List of compiled regex patterns to apply
        
    Returns:
        HTML string with matching tags removed
        
    Example:
        >>> patterns = [RegexPatterns.SCRIPT_TAGS, RegexPatterns.NOSCRIPT_TAGS]
        >>> remove_html_tags(html, patterns)
    """
    for pattern in patterns:
        html = pattern.sub('', html)
    return html


def replace_attribute_values(html: str, pattern: Pattern, replacement: str) -> str:
    """
    Generic attribute value replacement utility.
    
    Replaces attribute values that match a pattern with a safe replacement.
    Commonly used for sanitizing URLs and JavaScript references.
    
    Args:
        html: HTML content to process
        pattern: Compiled regex pattern to match
        replacement: Replacement string
        
    Returns:
        HTML string with attribute values replaced
        
    Example:
        >>> replace_attribute_values(html, RegexPatterns.JAVASCRIPT_URLS_HREF, 'href="#"')
    """
    return pattern.sub(replacement, html)


def remove_event_handlers(html: str) -> str:
    """
    Remove all JavaScript event handlers from HTML.
    
    This function removes event handler attributes (onclick, onload, etc.)
    from HTML elements for security purposes.
    
    Args:
        html: HTML content to process
        
    Returns:
        HTML string with event handlers removed
    """
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
        pattern = re.compile(rf'\s+{handler}\s*=\s*["\'][^"\']*["\']', IGNORECASE_ONLY)
        html = pattern.sub('', html)
    
    return html