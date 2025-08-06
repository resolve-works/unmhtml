import re
import base64
import mimetypes
from typing import Dict
from .security import is_javascript_file


class HTMLProcessor:
    """
    Processor for embedding CSS and converting resources to data URIs in HTML.
    
    This class takes HTML content and a collection of resources (CSS, images, fonts)
    and processes the HTML to create a standalone document. It converts external
    CSS links to inline <style> tags and converts resource references to data URIs.
    
    The processor handles various resource types including CSS files, images, fonts,
    and other binary resources, converting them to base64-encoded data URIs for
    embedding directly in the HTML.
    
    Args:
        html_content: The HTML content to process
        resources: Dictionary mapping resource URLs to their binary content
        
    Example:
        >>> processor = HTMLProcessor(html_content, resources)
        >>> html_with_css = processor.embed_css()
        >>> standalone_html = processor.convert_to_data_uris()
    """
    def __init__(self, html_content: str, resources: Dict[str, bytes], remove_javascript: bool = False):
        self.html_content = html_content
        self.resources = resources
        self.remove_javascript = remove_javascript
        
        # Filter out JavaScript files if remove_javascript is True
        if self.remove_javascript:
            self.resources = self._filter_javascript_resources(resources)
        
    def embed_css(self) -> str:
        """
        Convert external CSS <link> tags to inline <style> tags.
        
        Finds all stylesheet link tags in the HTML and replaces them with
        inline <style> tags containing the CSS content from the resources.
        
        Returns:
            HTML string with CSS embedded as inline styles
            
        Example:
            >>> processor = HTMLProcessor(html, resources)
            >>> html_with_css = processor.embed_css()
            >>> # <link rel="stylesheet" href="style.css"> becomes <style>...</style>
        """
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
        """
        Convert resource references to data URIs for standalone HTML.
        
        Processes src and href attributes in the HTML, converting references
        to embedded resources into base64-encoded data URIs. Also handles
        CSS url() references within stylesheets.
        
        Returns:
            HTML string with all resource references converted to data URIs
            
        Example:
            >>> processor = HTMLProcessor(html, resources)
            >>> standalone_html = processor.convert_to_data_uris()
            >>> # <img src="image.jpg"> becomes <img src="data:image/jpeg;base64,...">
        """
        html = self.html_content
        
        # Process src attributes (images, scripts, etc.)
        src_pattern = r'(src\s*=\s*["\'])([^"\']+)(["\'])'
        html = re.sub(src_pattern, self._replace_with_data_uri, html, flags=re.IGNORECASE)
        
        # Remove favicon links that point to missing resources to prevent external requests
        html = self._remove_missing_favicons(html)
        
        # Process href attributes (excluding CSS which was already handled)
        href_pattern = r'(href\s*=\s*["\'])([^"\']+)(["\'])(?![^<]*rel\s*=\s*["\']stylesheet["\'])'
        html = re.sub(href_pattern, self._replace_with_data_uri, html, flags=re.IGNORECASE)
        
        # Process CSS url() references
        css_url_pattern = r'url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)'
        html = re.sub(css_url_pattern, self._replace_css_url, html, flags=re.IGNORECASE)
        
        return html
    
    def _find_css_content(self, href: str) -> str:
        """
        Find CSS content in resources by href attribute.
        
        Searches for CSS content using exact match first, then fallback
        to basename matching for more flexible resource resolution.
        
        Args:
            href: The href attribute value from the link tag
            
        Returns:
            CSS content as string, empty string if not found
        """
        # Decode HTML entities and find resource content
        import html
        decoded_href = html.unescape(href)
        resource_data = self._find_resource_by_url(decoded_href)
        
        if resource_data:
            try:
                return resource_data.decode('utf-8', errors='ignore')
            except Exception:
                return ""
        return ""
    
    def _replace_with_data_uri(self, match) -> str:
        """
        Replace a URL match with a data URI.
        
        Callback function for regex substitution that converts resource
        URLs to base64-encoded data URIs.
        
        Args:
            match: Regex match object containing URL components
            
        Returns:
            Replacement string with data URI or original if resource not found
        """
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)
        
        # Skip if already a data URI
        if url.startswith('data:'):
            return match.group(0)
        
        # Find resource content
        resource_data = self._find_resource_content(url)
        if resource_data:
            # Create data URI using centralized helper
            data_uri = self._create_data_uri(resource_data, url)
            return f'{prefix}{data_uri}{suffix}'
        
        # Return original if resource not found
        return match.group(0)
    
    def _replace_css_url(self, match) -> str:
        """
        Replace CSS url() references with data URIs.
        
        Callback function for regex substitution that converts CSS url()
        references to base64-encoded data URIs.
        
        Args:
            match: Regex match object containing the URL
            
        Returns:
            Replacement CSS url() with data URI or original if resource not found
        """
        url = match.group(1)
        
        # Skip if already a data URI
        if url.startswith('data:'):
            return match.group(0)
        
        # Find resource content
        resource_data = self._find_resource_content(url)
        if resource_data:
            # Create data URI using centralized helper
            data_uri = self._create_data_uri(resource_data, url)
            return f'url("{data_uri}")'
        
        # Return original if resource not found
        return match.group(0)
    
    def _find_resource_content(self, url: str) -> bytes:
        """
        Find resource content by URL with flexible matching.
        
        Searches for resource content using multiple strategies:
        exact match, basename match, and URL without query parameters.
        
        Args:
            url: The URL to search for in resources
            
        Returns:
            Binary content of the resource, empty bytes if not found
        """
        return self._find_resource_by_url(url)
        
    def _find_resource_by_url(self, url: str) -> bytes:
        """
        Centralized resource finder with flexible URL matching strategies.
        
        This method consolidates all resource finding logic used across
        the processor to avoid duplication. It tries multiple matching
        strategies in order of preference.
        
        Args:
            url: The URL to search for in resources
            
        Returns:
            Binary content of the resource, empty bytes if not found
        """
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
    
    def _create_data_uri(self, resource_data: bytes, url: str) -> str:
        """
        Create a base64-encoded data URI from resource data.
        
        This method consolidates the data URI creation logic used across
        the processor to avoid duplication. It determines the MIME type
        and creates a properly formatted data URI.
        
        Args:
            resource_data: Binary content of the resource
            url: The original URL (used for MIME type detection)
            
        Returns:
            Complete data URI string with MIME type and base64 content
            
        Example:
            >>> data_uri = processor._create_data_uri(image_bytes, "image.png")
            >>> # Returns: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
        """
        mime_type = self._get_mime_type(url)
        b64_data = base64.b64encode(resource_data).decode('ascii')
        return f'data:{mime_type};base64,{b64_data}'
    
    def _get_mime_type(self, url: str) -> str:
        """
        Determine MIME type for a resource URL.
        
        Uses Python's mimetypes module with additional handling for
        common web font types and other edge cases.
        
        Args:
            url: The resource URL to analyze
            
        Returns:
            MIME type string, defaults to 'application/octet-stream'
        """
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
    
    def _remove_missing_favicons(self, html: str) -> str:
        """
        Remove favicon links that point to missing resources.
        
        Prevents external requests by removing favicon and apple-touch-icon
        links that reference resources not available in the MHTML bundle.
        
        Args:
            html: The HTML content to process
            
        Returns:
            HTML with missing favicon links removed
        """
        # Find favicon links
        favicon_pattern = r'<link\s+[^>]*rel\s*=\s*["\'](?:icon|apple-touch-icon)["\'][^>]*>'
        favicon_links = re.findall(favicon_pattern, html, re.IGNORECASE)
        
        for link in favicon_links:
            # Extract href attribute
            href_match = re.search(r'href\s*=\s*["\']([^"\']+)["\']', link, re.IGNORECASE)
            if href_match:
                href = href_match.group(1)
                
                # Check if resource exists in our bundle
                resource_data = self._find_resource_content(href)
                if not resource_data:
                    # Resource not found, remove the link
                    html = html.replace(link, '')
                    
        return html
    
    def _filter_javascript_resources(self, resources: Dict[str, bytes]) -> Dict[str, bytes]:
        """
        Filter out JavaScript files from resources when remove_javascript=True.
        
        Removes JavaScript files from the resources dictionary to prevent them
        from being embedded as data URIs in the final HTML.
        
        Args:
            resources: Dictionary of resource URLs to binary content
            
        Returns:
            Filtered resources dictionary without JavaScript files
        """
        filtered_resources = {}
        
        for url, content in resources.items():
            # Check if this is a JavaScript file
            if not is_javascript_file(url):
                filtered_resources[url] = content
        
        return filtered_resources