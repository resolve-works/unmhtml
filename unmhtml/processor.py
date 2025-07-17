import re
import base64
import mimetypes
from typing import Dict
from urllib.parse import urlparse, urljoin
from html import escape


class HTMLProcessor:
    def __init__(self, html_content: str, resources: Dict[str, bytes]):
        self.html_content = html_content
        self.resources = resources
        
    def embed_css(self) -> str:
        """Convert <link> tags to <style> tags with embedded CSS"""
        html = self.html_content
        
        # Find all CSS link tags
        link_pattern = r'<link\s+[^>]*rel\s*=\s*["\']stylesheet["\'][^>]*>'
        links = re.findall(link_pattern, html, re.IGNORECASE)
        
        for link in links:
            # Extract href attribute
            href_match = re.search(r'href\s*=\s*["\']([^"\']+)["\']', link, re.IGNORECASE)
            if href_match:
                href = href_match.group(1)
                
                # Find CSS content in resources
                css_content = self._find_css_content(href)
                if css_content:
                    # Replace link tag with style tag
                    style_tag = f'<style type="text/css">\n{css_content}\n</style>'
                    html = html.replace(link, style_tag)
                    
        return html
    
    def convert_to_data_uris(self) -> str:
        """Convert resource references to data URIs"""
        html = self.html_content
        
        # Process src attributes (images, scripts, etc.)
        src_pattern = r'(src\s*=\s*["\'])([^"\']+)(["\'])'
        html = re.sub(src_pattern, self._replace_with_data_uri, html, flags=re.IGNORECASE)
        
        # Process href attributes (excluding CSS which was already handled)
        href_pattern = r'(href\s*=\s*["\'])([^"\']+)(["\'])(?![^<]*rel\s*=\s*["\']stylesheet["\'])'
        html = re.sub(href_pattern, self._replace_with_data_uri, html, flags=re.IGNORECASE)
        
        # Process CSS url() references
        css_url_pattern = r'url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)'
        html = re.sub(css_url_pattern, self._replace_css_url, html, flags=re.IGNORECASE)
        
        return html
    
    def _find_css_content(self, href: str) -> str:
        """Find CSS content by href in resources"""
        # Try exact match first
        if href in self.resources:
            try:
                return self.resources[href].decode('utf-8', errors='ignore')
            except Exception:
                return ""
        
        # Try to find by basename or similar URLs
        for resource_url, content in self.resources.items():
            if resource_url.endswith(href) or href.endswith(resource_url.split('/')[-1]):
                try:
                    return content.decode('utf-8', errors='ignore')
                except Exception:
                    continue
                    
        return ""
    
    def _replace_with_data_uri(self, match) -> str:
        """Replace URL with data URI"""
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)
        
        # Skip if already a data URI
        if url.startswith('data:'):
            return match.group(0)
        
        # Find resource content
        resource_data = self._find_resource_content(url)
        if resource_data:
            # Determine MIME type
            mime_type = self._get_mime_type(url)
            
            # Create data URI
            b64_data = base64.b64encode(resource_data).decode('ascii')
            data_uri = f'data:{mime_type};base64,{b64_data}'
            
            return f'{prefix}{data_uri}{suffix}'
        
        # Return original if resource not found
        return match.group(0)
    
    def _replace_css_url(self, match) -> str:
        """Replace CSS url() with data URI"""
        url = match.group(1)
        
        # Skip if already a data URI
        if url.startswith('data:'):
            return match.group(0)
        
        # Find resource content
        resource_data = self._find_resource_content(url)
        if resource_data:
            # Determine MIME type
            mime_type = self._get_mime_type(url)
            
            # Create data URI
            b64_data = base64.b64encode(resource_data).decode('ascii')
            data_uri = f'data:{mime_type};base64,{b64_data}'
            
            return f'url("{data_uri}")'
        
        # Return original if resource not found
        return match.group(0)
    
    def _find_resource_content(self, url: str) -> bytes:
        """Find resource content by URL in resources"""
        # Try exact match first
        if url in self.resources:
            return self.resources[url]
        
        # Try to find by basename or similar URLs
        for resource_url, content in self.resources.items():
            if resource_url.endswith(url) or url.endswith(resource_url.split('/')[-1]):
                return content
                
        # Try without query parameters
        url_without_query = url.split('?')[0]
        if url_without_query in self.resources:
            return self.resources[url_without_query]
            
        return b""
    
    def _get_mime_type(self, url: str) -> str:
        """Get MIME type for a URL"""
        mime_type, _ = mimetypes.guess_type(url)
        
        # Handle some common cases that mimetypes might not recognize properly
        if url.endswith('.woff'):
            return 'font/woff'
        elif url.endswith('.woff2'):
            return 'font/woff2'
        elif url.endswith('.ttf'):
            return 'font/ttf'
        elif url.endswith('.otf'):
            return 'font/otf'
        elif url.endswith('.js'):
            return 'text/javascript'
        
        # Return detected MIME type if it looks reasonable, otherwise use default
        if mime_type and not mime_type.startswith('chemical/'):
            return mime_type
        
        return 'application/octet-stream'