import pytest
from unmhtml.utils import (
    normalize_url, 
    extract_charset, 
    is_binary_content_type,
    clean_html_content,
    extract_filename_from_url
)


class TestUtils:
    
    @pytest.mark.parametrize("url,expected", [
        ("https://example.com/page.html", "https://example.com/page.html"),
        ("http://example.com/page.html", "http://example.com/page.html"),
        ("data:image/png;base64,abc", "data:image/png;base64,abc"),
        ("mailto:test@example.com", "mailto:test@example.com"),
        ("tel:+1234567890", "tel:+1234567890"),
    ])
    def test_normalize_url_absolute(self, url, expected):
        """Test URL normalization with absolute URLs"""
        assert normalize_url(url) == expected
    
    @pytest.mark.parametrize("url,base_url,expected", [
        ("page.html", "https://example.com/path/", "https://example.com/path/page.html"),
        ("../style.css", "https://example.com/path/", "https://example.com/style.css"),
        ("/absolute/path.html", "https://example.com/path/", "https://example.com/absolute/path.html"),
        ("./image.png", "https://example.com/", "https://example.com/image.png"),
    ])
    def test_normalize_url_relative_with_base(self, url, base_url, expected):
        """Test URL normalization with relative URLs and base URL"""
        assert normalize_url(url, base_url) == expected
    
    def test_normalize_url_relative_without_base(self):
        """Test URL normalization with relative URLs without base"""
        assert normalize_url("page.html") == "page.html"
        assert normalize_url("../style.css") == "../style.css"
    
    @pytest.mark.parametrize("url,expected", [
        ("", ""),
        (None, ""),
    ])
    def test_normalize_url_empty(self, url, expected):
        """Test URL normalization with empty URLs"""
        assert normalize_url(url) == expected
    
    @pytest.mark.parametrize("content_type,expected", [
        ("text/html; charset=utf-8", "utf-8"),
        ("text/html; charset=UTF-8", "UTF-8"),
        ("text/html; charset='utf-8'", "utf-8"),
        ('text/html; charset="utf-8"', "utf-8"),
        ("text/html; charset=iso-8859-1", "iso-8859-1"),
        ("text/html; charset=utf-8; boundary=test", "utf-8"),
        ("application/json; charset=utf-8", "utf-8"),
    ])
    def test_extract_charset_valid(self, content_type, expected):
        """Test charset extraction with valid Content-Type headers"""
        assert extract_charset(content_type) == expected
    
    @pytest.mark.parametrize("content_type", [
        "text/html",
        "",
        None,
        "text/html; charset",
        "text/html; charset=",
        "application/octet-stream",
    ])
    def test_extract_charset_invalid(self, content_type):
        """Test charset extraction with invalid Content-Type headers"""
        assert extract_charset(content_type) is None
    
    @pytest.mark.parametrize("content_type,expected", [
        ("image/png", True),
        ("image/jpeg", True),
        ("image/gif", True),
        ("audio/mp3", True),
        ("audio/wav", True),
        ("video/mp4", True),
        ("video/avi", True),
        ("application/pdf", True),
        ("application/zip", True),
        ("application/octet-stream", True),
        ("font/woff", True),
        ("font/woff2", True),
        ("application/font-woff", True),
        ("application/x-font-ttf", True),
        ("application/x-font-otf", True),
    ])
    def test_is_binary_content_type_true(self, content_type, expected):
        """Test binary content type detection for binary types"""
        assert is_binary_content_type(content_type) == expected
    
    @pytest.mark.parametrize("content_type,expected", [
        ("text/html", False),
        ("text/css", False),
        ("text/javascript", False),
        ("text/plain", False),
        ("application/json", False),
        ("application/xml", False),
        ("application/javascript", False),
        ("text/xml", False),
    ])
    def test_is_binary_content_type_false(self, content_type, expected):
        """Test binary content type detection for text types"""
        assert is_binary_content_type(content_type) == expected
    
    @pytest.mark.parametrize("content_type", [
        "",
        None,
        "invalid/type",
    ])
    def test_is_binary_content_type_invalid(self, content_type):
        """Test binary content type detection with invalid types"""
        assert is_binary_content_type(content_type) is False
    
    def test_is_binary_content_type_case_insensitive(self):
        """Test binary content type detection is case insensitive"""
        assert is_binary_content_type("IMAGE/PNG") is True
        assert is_binary_content_type("Image/Png") is True
        assert is_binary_content_type("TEXT/HTML") is False
        assert is_binary_content_type("Text/Html") is False
    
    def test_clean_html_content_script_removal(self):
        """Test script tag removal"""
        html_with_script = '<html><body><script>alert("test")</script><p>Hello</p></body></html>'
        cleaned = clean_html_content(html_with_script)
        assert '<script>' not in cleaned
        assert 'alert("test")' not in cleaned
        assert '<p>Hello</p>' in cleaned
    
    def test_clean_html_content_event_handlers(self):
        """Test event handler removal"""
        html_with_events = '<div onclick="alert(1)" onload="bad()" class="test">Hello</div>'
        cleaned = clean_html_content(html_with_events)
        assert 'onclick=' not in cleaned
        assert 'onload=' not in cleaned
        assert 'class="test"' in cleaned
        assert 'Hello' in cleaned
    
    def test_clean_html_content_javascript_urls(self):
        """Test javascript: URL removal"""
        html_with_js_url = '<a href="javascript:alert(1)">Link</a>'
        cleaned = clean_html_content(html_with_js_url)
        assert 'javascript:' not in cleaned
        assert 'href="#"' in cleaned
        assert 'Link' in cleaned
    
    def test_clean_html_content_complex(self):
        """Test complex HTML cleaning"""
        complex_html = '''
        <html>
        <head>
            <script type="text/javascript">
                function malicious() { alert("bad"); }
            </script>
        </head>
        <body onclick="malicious()">
            <p>Good content</p>
            <a href="javascript:void(0)">Bad link</a>
            <img src="image.png" onload="track()" alt="test">
        </body>
        </html>
        '''
        cleaned = clean_html_content(complex_html)
        assert '<script>' not in cleaned
        assert 'onclick=' not in cleaned
        assert 'onload=' not in cleaned
        assert 'javascript:' not in cleaned
        assert 'Good content' in cleaned
        assert 'src="image.png"' in cleaned
        assert 'alt="test"' in cleaned
    
    def test_clean_html_content_preserves_good_content(self):
        """Test that good content is preserved"""
        good_html = '''
        <html>
        <head>
            <title>Test Page</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <h1>Title</h1>
            <p class="content">This is good content</p>
            <img src="image.png" alt="test">
            <a href="page.html">Good link</a>
        </body>
        </html>
        '''
        cleaned = clean_html_content(good_html)
        assert '<title>Test Page</title>' in cleaned
        assert '<link rel="stylesheet"' in cleaned
        assert '<h1>Title</h1>' in cleaned
        assert 'class="content"' in cleaned
        assert 'src="image.png"' in cleaned
        assert 'href="page.html"' in cleaned
    
    @pytest.mark.parametrize("url,expected", [
        ("https://example.com/image.png", "image.png"),
        ("https://example.com/path/to/file.css", "file.css"),
        ("https://example.com/script.js", "script.js"),
        ("https://example.com/page.html", "page.html"),
        ("https://cdn.example.com/v1.0/assets/fonts/font.woff2", "font.woff2"),
        ("/static/images/logo.svg", "logo.svg"),
    ])
    def test_extract_filename_from_url_simple(self, url, expected):
        """Test filename extraction from simple URLs"""
        assert extract_filename_from_url(url) == expected
    
    @pytest.mark.parametrize("url,expected", [
        ("https://example.com/image.png?v=1.0", "image.png"),
        ("https://example.com/file.js?cache=false&v=2", "file.js"),
        ("https://example.com/style.css?timestamp=123456", "style.css"),
    ])
    def test_extract_filename_from_url_with_query(self, url, expected):
        """Test filename extraction with query parameters"""
        assert extract_filename_from_url(url) == expected
    
    @pytest.mark.parametrize("url,expected", [
        ("https://example.com/", ""),
        ("https://example.com", ""),
        ("https://example.com/path/", ""),
        ("", ""),
    ])
    def test_extract_filename_from_url_no_filename(self, url, expected):
        """Test filename extraction when no filename is present"""
        assert extract_filename_from_url(url) == expected
    
    @pytest.mark.parametrize("url,expected", [
        ("image.png", "image.png"),
        ("../assets/style.css", "style.css"),
        ("./scripts/app.js", "app.js"),
        ("file.txt", "file.txt"),
    ])
    def test_extract_filename_from_url_relative(self, url, expected):
        """Test filename extraction from relative URLs"""
        assert extract_filename_from_url(url) == expected
    
    def test_extract_filename_from_url_edge_cases(self):
        """Test filename extraction edge cases"""
        # Multiple dots in filename
        assert extract_filename_from_url("https://example.com/jquery.min.js") == "jquery.min.js"
        
        # No extension
        assert extract_filename_from_url("https://example.com/README") == "README"
        
        # Complex path
        assert extract_filename_from_url("https://example.com/a/b/c/d/file.ext") == "file.ext"
        
        # With fragment
        assert extract_filename_from_url("https://example.com/page.html#section") == "page.html"
    
    @pytest.mark.parametrize("input_html,should_contain", [
        ('<script>alert("xss")</script><p>content</p>', '<p>content</p>'),
        ('<div onclick="bad()">text</div>', '<div>text</div>'),
        ('<a href="javascript:void(0)">link</a>', '<a href="#">link</a>'),
        ('<img src="image.png" onload="track()" alt="test">', 'src="image.png"'),
    ])
    def test_clean_html_content_integration(self, input_html, should_contain):
        """Test HTML cleaning integration with various inputs"""
        result = clean_html_content(input_html)
        assert should_contain in result
        
        # Should not contain dangerous content
        assert 'script>' not in result
        assert 'javascript:' not in result
        assert 'on' not in result or 'onclick' not in result