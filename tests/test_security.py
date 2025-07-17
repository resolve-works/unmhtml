import pytest
from unmhtml.security import (
    remove_javascript_content,
    is_javascript_file
)


class TestSecurity:
    
    def test_remove_javascript_content_script_removal(self):
        """Test script tag removal"""
        html_with_script = '<html><body><script>alert("test")</script><p>Hello</p></body></html>'
        cleaned = remove_javascript_content(html_with_script)
        assert '<script>' not in cleaned
        assert 'alert("test")' not in cleaned
        assert '<p>Hello</p>' in cleaned
    
    def test_remove_javascript_content_event_handlers(self):
        """Test event handler removal"""
        html_with_events = '<div onclick="alert(1)" onload="bad()" class="test">Hello</div>'
        cleaned = remove_javascript_content(html_with_events)
        assert 'onclick=' not in cleaned
        assert 'onload=' not in cleaned
        assert 'class="test"' in cleaned
        assert 'Hello' in cleaned
    
    def test_remove_javascript_content_javascript_urls(self):
        """Test javascript: URL removal"""
        html_with_js_url = '<a href="javascript:alert(1)">Link</a>'
        cleaned = remove_javascript_content(html_with_js_url)
        assert 'javascript:' not in cleaned
        assert 'href="#"' in cleaned
        assert 'Link' in cleaned
    
    def test_remove_javascript_content_complex(self):
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
        cleaned = remove_javascript_content(complex_html)
        assert '<script>' not in cleaned
        assert 'onclick=' not in cleaned
        assert 'onload=' not in cleaned
        assert 'javascript:' not in cleaned
        assert 'Good content' in cleaned
        assert 'src="image.png"' in cleaned
        assert 'alt="test"' in cleaned
    
    def test_remove_javascript_content_preserves_good_content(self):
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
        cleaned = remove_javascript_content(good_html)
        assert '<title>Test Page</title>' in cleaned
        assert '<link rel="stylesheet"' in cleaned
        assert '<h1>Title</h1>' in cleaned
        assert 'class="content"' in cleaned
        assert 'src="image.png"' in cleaned
        assert 'href="page.html"' in cleaned
    
    @pytest.mark.parametrize("input_html,should_contain", [
        ('<script>alert("xss")</script><p>content</p>', '<p>content</p>'),
        ('<div onclick="bad()">text</div>', '<div>text</div>'),
        ('<a href="javascript:void(0)">link</a>', '<a href="#">link</a>'),
        ('<img src="image.png" onload="track()" alt="test">', 'src="image.png"'),
    ])
    def test_remove_javascript_content_integration(self, input_html, should_contain):
        """Test HTML cleaning integration with various inputs"""
        result = remove_javascript_content(input_html)
        assert should_contain in result
        
        # Should not contain dangerous content
        assert 'script>' not in result
        assert 'javascript:' not in result
        assert 'on' not in result or 'onclick' not in result
    
    # Tests for JavaScript file detection
    @pytest.mark.parametrize("url,expected", [
        ("app.js", True),
        ("script.mjs", True),
        ("component.jsx", True),
        ("module.ts", True),
        ("component.tsx", True),
        ("APP.JS", True),  # Case insensitive
        ("style.css", False),
        ("image.png", False),
        ("page.html", False),
        ("data.json", False),
        ("", False),
    ])
    def test_is_javascript_file_by_extension(self, url, expected):
        """Test JavaScript file detection by extension"""
        assert is_javascript_file(url) == expected
    
    @pytest.mark.parametrize("url,content_type,expected", [
        ("unknown", "text/javascript", True),
        ("unknown", "application/javascript", True),
        ("unknown", "application/x-javascript", True),
        ("unknown", "text/ecmascript", True),
        ("unknown", "application/ecmascript", True),
        ("unknown", "TEXT/JAVASCRIPT", True),  # Case insensitive
        ("unknown", "text/css", False),
        ("unknown", "image/png", False),
        ("unknown", "text/html", False),
        ("unknown", "", False),
        ("unknown", None, False),
    ])
    def test_is_javascript_file_by_content_type(self, url, content_type, expected):
        """Test JavaScript file detection by content type"""
        assert is_javascript_file(url, content_type) == expected
    
    def test_is_javascript_file_combined(self):
        """Test JavaScript file detection with both extension and content type"""
        # Extension overrides content type
        assert is_javascript_file("app.js", "text/css") == True
        assert is_javascript_file("style.css", "text/javascript") == True
        
        # Both indicate JavaScript
        assert is_javascript_file("app.js", "text/javascript") == True
        
        # Neither indicates JavaScript
        assert is_javascript_file("style.css", "text/css") == False