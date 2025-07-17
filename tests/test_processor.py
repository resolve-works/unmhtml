import pytest
from unmhtml.processor import HTMLProcessor


class TestHTMLProcessor:
    
    def test_embed_css(self, html_with_css, sample_resources):
        """Test CSS embedding functionality"""
        processor = HTMLProcessor(html_with_css, sample_resources)
        result = processor.embed_css()
        
        # Check that link tags are replaced with style tags
        assert '<link rel="stylesheet"' not in result
        assert '<style type="text/css">' in result
        
        # Check that CSS content is embedded
        assert 'font-family: Arial' in result
        assert 'color: red' in result
    
    def test_convert_to_data_uris(self, sample_resources):
        """Test resource conversion to data URIs"""
        html = '<img src="image.png" alt="test"><img src="https://example.com/logo.png" alt="logo">'
        processor = HTMLProcessor(html, sample_resources)
        result = processor.convert_to_data_uris()
        
        # Check that src attributes are converted to data URIs
        assert 'src="data:image/png;base64,' in result
        assert 'src="image.png"' not in result
        assert 'src="https://example.com/logo.png"' not in result
    
    def test_css_url_replacement(self, sample_css, sample_resources):
        """Test CSS url() replacement"""
        html = f'<style>{sample_css}</style>'
        processor = HTMLProcessor(html, sample_resources)
        result = processor.convert_to_data_uris()
        
        # Check that CSS urls are converted to data URIs
        assert 'url("data:image/jpeg;base64,' in result  # background.jpg
        assert 'url("data:image/png;base64,' in result   # pattern.png
        assert 'url(\'background.jpg\')' not in result
        assert 'url("pattern.png")' not in result
    
    def test_preserve_existing_data_uris(self, sample_resources):
        """Test that existing data URIs are preserved"""
        html = '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" alt="test">'
        processor = HTMLProcessor(html, sample_resources)
        result = processor.convert_to_data_uris()
        
        # Should not modify existing data URIs
        assert html == result
    
    def test_find_css_content(self, sample_resources):
        """Test CSS content finding"""
        processor = HTMLProcessor("", sample_resources)
        
        # Test exact match
        result = processor._find_css_content("style.css")
        assert result == "body { font-family: Arial; }"
        
        # Test URL match
        result = processor._find_css_content("https://example.com/external.css")
        assert result == "h1 { color: red; }"
        
        # Test not found
        result = processor._find_css_content("nonexistent.css")
        assert result == ""
    
    def test_find_resource_content(self, sample_resources):
        """Test resource content finding"""
        processor = HTMLProcessor("", sample_resources)
        
        # Test exact match
        result = processor._find_resource_content("image.png")
        assert len(result) > 0
        assert result.startswith(b'\x89PNG')
        
        # Test URL match
        result = processor._find_resource_content("https://example.com/logo.png")
        assert len(result) > 0
        
        # Test not found
        result = processor._find_resource_content("nonexistent.png")
        assert result == b""
    
    @pytest.mark.parametrize("filename,expected_mime", [
        ("image.png", "image/png"),
        ("style.css", "text/css"),
        ("script.js", "text/javascript"),
        ("page.html", "text/html"),
        ("font.woff", "font/woff"),
        ("unknown.xyz", "application/octet-stream"),
    ])
    def test_get_mime_type(self, filename, expected_mime):
        """Test MIME type detection"""
        processor = HTMLProcessor("", {})
        result = processor._get_mime_type(filename)
        assert result == expected_mime
    
    def test_complex_html_processing(self, sample_resources):
        """Test processing complex HTML with multiple resources"""
        complex_html = """
        <html>
        <head>
            <link rel="stylesheet" href="style.css">
            <style>
                body { background: url('background.jpg'); }
            </style>
        </head>
        <body>
            <img src="image.png" alt="test">
            <img src="https://example.com/logo.png" alt="logo">
        </body>
        </html>
        """
        
        processor = HTMLProcessor(complex_html, sample_resources)
        
        # First embed CSS
        result = processor.embed_css()
        assert '<style type="text/css">' in result
        assert 'font-family: Arial' in result
        
        # Then convert to data URIs
        processor.html_content = result
        final_result = processor.convert_to_data_uris()
        
        # Check all resources are converted
        assert 'src="data:image/png;base64,' in final_result
        assert 'url("data:image/jpeg;base64,' in final_result
        assert 'src="image.png"' not in final_result
        assert 'background.jpg' not in final_result
    
    def test_malformed_html_handling(self, sample_resources):
        """Test handling of malformed HTML"""
        malformed_html = '<img src="image.png" alt="test><link rel="stylesheet" href="style.css"'
        processor = HTMLProcessor(malformed_html, sample_resources)
        
        # Should not crash and should attempt to process
        result = processor.embed_css()
        assert isinstance(result, str)
        
        result = processor.convert_to_data_uris()
        assert isinstance(result, str)
    
    def test_multiple_css_links(self, sample_resources):
        """Test processing multiple CSS links"""
        html = '''
        <html>
        <head>
            <link rel="stylesheet" href="style.css">
            <link rel="stylesheet" href="https://example.com/external.css">
            <link rel="icon" href="favicon.ico">
        </head>
        <body>Test</body>
        </html>
        '''
        
        processor = HTMLProcessor(html, sample_resources)
        result = processor.embed_css()
        
        # Should convert stylesheet links but not icon links
        assert '<link rel="stylesheet"' not in result
        assert '<link rel="icon"' in result
        assert '<style type="text/css">' in result
        assert 'font-family: Arial' in result
        assert 'color: red' in result
    
    def test_css_with_media_queries(self, sample_resources):
        """Test CSS with media queries"""
        html = '''
        <html>
        <head>
            <link rel="stylesheet" href="style.css" media="screen">
            <link rel="stylesheet" href="https://example.com/external.css" media="print">
        </head>
        <body>Test</body>
        </html>
        '''
        
        processor = HTMLProcessor(html, sample_resources)
        result = processor.embed_css()
        
        # Should still convert to style tags
        assert '<style type="text/css">' in result
        assert 'font-family: Arial' in result
        assert 'color: red' in result
    
    def test_resource_url_variations(self, sample_resources):
        """Test handling of various resource URL formats"""
        html = '''
        <img src="image.png">
        <img src="./image.png">
        <img src="/image.png">
        <img src="image.png?v=1">
        '''
        
        processor = HTMLProcessor(html, sample_resources)
        result = processor.convert_to_data_uris()
        
        # At least one should be converted (exact match)
        assert 'data:image/png;base64,' in result
    
    def test_empty_resources(self):
        """Test processing with empty resources"""
        html = '<img src="image.png" alt="test">'
        processor = HTMLProcessor(html, {})
        result = processor.convert_to_data_uris()
        
        # Should not crash, should return original HTML
        assert result == html
    
    def test_no_resources_to_process(self):
        """Test HTML with no resources to process"""
        html = '<html><body><p>Just text content</p></body></html>'
        processor = HTMLProcessor(html, {})
        
        embed_result = processor.embed_css()
        assert embed_result == html
        
        uri_result = processor.convert_to_data_uris()
        assert uri_result == html
    
    def test_javascript_file_filtering(self):
        """Test that JavaScript files are filtered when remove_javascript=True"""
        html = '''<html>
        <body>
            <script src="app.js"></script>
            <img src="image.png" alt="test">
            <link rel="stylesheet" href="style.css">
        </body>
        </html>'''
        
        resources = {
            'app.js': b'alert("hello world");',
            'image.png': b'fake_image_data',
            'style.css': b'body { color: red; }'
        }
        
        # Test with remove_javascript=False (default)
        processor_normal = HTMLProcessor(html, resources, remove_javascript=False)
        result_normal = processor_normal.convert_to_data_uris()
        
        # JavaScript file should be converted to data URI
        assert 'data:text/javascript;base64,' in result_normal
        assert 'data:image/png;base64,' in result_normal
        
        # Test with remove_javascript=True
        processor_secure = HTMLProcessor(html, resources, remove_javascript=True)
        result_secure = processor_secure.convert_to_data_uris()
        
        # JavaScript file should NOT be converted to data URI
        assert 'data:text/javascript;base64,' not in result_secure
        # Other resources should still be converted
        assert 'data:image/png;base64,' in result_secure
        
        # The original src="app.js" should remain unchanged (not converted to data URI)
        assert 'src="app.js"' in result_secure
    
    def test_javascript_file_filtering_with_css_embedding(self):
        """Test JavaScript filtering works with CSS embedding"""
        html = '''<html>
        <head>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <script src="app.js"></script>
            <img src="image.png" alt="test">
        </body>
        </html>'''
        
        resources = {
            'app.js': b'console.log("test");',
            'image.png': b'fake_image_data',
            'style.css': b'body { background: blue; }'
        }
        
        # Test with remove_javascript=True
        processor = HTMLProcessor(html, resources, remove_javascript=True)
        
        # First embed CSS
        html_with_css = processor.embed_css()
        assert '<style type="text/css">' in html_with_css
        assert 'background: blue' in html_with_css
        
        # Update processor content and convert to data URIs
        processor.html_content = html_with_css
        result = processor.convert_to_data_uris()
        
        # JavaScript should not be embedded as data URI
        assert 'data:text/javascript;base64,' not in result
        # Image should be embedded
        assert 'data:image/png;base64,' in result
        # CSS should be embedded inline
        assert '<style type="text/css">' in result
        assert 'background: blue' in result