import email
import base64
from typing import Dict, Tuple, Optional


class MHTMLParser:
    """
    Parser for extracting HTML content and resources from MHTML files.
    
    This class handles the parsing of MHTML (MIME HTML) files, which are structured
    as MIME multipart documents. It extracts the main HTML content and associated
    resources (CSS, images, fonts, etc.) from the MHTML structure.
    
    The parser handles various MHTML formats including multipart/related and
    message/rfc822 structures, with graceful degradation for malformed files.
    
    Args:
        mhtml_content: The raw MHTML content as a string
        
    Example:
        >>> parser = MHTMLParser(mhtml_content)
        >>> html, resources = parser.parse()
        >>> print(f"Found {len(resources)} resources")
    """
    def __init__(self, mhtml_content: str):
        self.mhtml_content = mhtml_content
        
    def parse(self) -> Tuple[str, Dict[str, bytes]]:
        """
        Parse MHTML content and extract HTML and resources.
        
        Extracts the main HTML content and associated resources (CSS, images, fonts)
        from the MHTML structure. Handles both multipart and single-part MHTML files
        with graceful degradation for malformed content.
        
        Returns:
            Tuple containing:
                - Main HTML content as string
                - Dictionary mapping resource URLs to their binary content
                
        Example:
            >>> parser = MHTMLParser(mhtml_content)
            >>> html, resources = parser.parse()
            >>> print(f"HTML length: {len(html)}")
            >>> print(f"Resources: {list(resources.keys())}")
        """
        try:
            message = email.message_from_string(self.mhtml_content)
            main_html = ""
            resources = {}
            
            # Check if this looks like a proper MHTML structure
            has_mime_headers = ('MIME-Version' in message or 
                              'Content-Type' in message or 
                              'From:' in self.mhtml_content)
            
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                        
                    content_type = part.get_content_type()
                    content_location = part.get('Content-Location', '')
                    
                    # First text/html part is the main HTML
                    if content_type == 'text/html' and not main_html:
                        main_html = self._decode_part(part)
                    elif content_location:
                        # Extract resource content
                        resource_data = self._decode_part_binary(part)
                        if resource_data:
                            resources[content_location] = resource_data
            else:
                # Single part MHTML
                if message.get_content_type() == 'text/html':
                    main_html = self._decode_part(message)
            
            # If we didn't find HTML content and this doesn't look like MHTML, 
            # treat it as malformed and return the original content
            if not main_html and not resources and not has_mime_headers:
                return self.mhtml_content, {}
                    
            return main_html, resources
            
        except Exception as e:
            # Graceful degradation for malformed MHTML
            return self.mhtml_content, {}
    
    def _decode_part(self, part) -> str:
        """
        Decode a MIME part to a string.
        
        Handles various content transfer encodings including base64 and
        quoted-printable, with fallback to direct decoding.
        
        Args:
            part: MIME part object from email module
            
        Returns:
            Decoded string content, empty string if decoding fails
        """
        try:
            payload = part.get_payload()
            encoding = part.get('Content-Transfer-Encoding', '').lower()
            
            if encoding == 'base64':
                decoded = base64.b64decode(payload).decode('utf-8', errors='ignore')
            elif encoding == 'quoted-printable':
                import quopri
                decoded = quopri.decodestring(payload).decode('utf-8', errors='ignore')
            else:
                decoded = payload if isinstance(payload, str) else payload.decode('utf-8', errors='ignore')
                
            return decoded
        except Exception:
            return ""
    
    def _decode_part_binary(self, part) -> Optional[bytes]:
        """
        Decode a MIME part to binary data.
        
        Handles various content transfer encodings for binary content
        including base64 and quoted-printable.
        
        Args:
            part: MIME part object from email module
            
        Returns:
            Binary content as bytes, None if decoding fails
        """
        try:
            payload = part.get_payload()
            encoding = part.get('Content-Transfer-Encoding', '').lower()
            
            if encoding == 'base64':
                return base64.b64decode(payload)
            elif encoding == 'quoted-printable':
                import quopri
                return quopri.decodestring(payload)
            else:
                if isinstance(payload, str):
                    return payload.encode('utf-8')
                return payload
        except Exception:
            return None