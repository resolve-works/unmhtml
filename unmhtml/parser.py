import email
import base64
import mimetypes
from typing import Dict, Tuple, Optional
from urllib.parse import urlparse, urljoin


class MHTMLParser:
    def __init__(self, mhtml_content: str):
        self.mhtml_content = mhtml_content
        
    def parse(self) -> Tuple[str, Dict[str, bytes]]:
        """Parse MHTML and return main HTML + resource map"""
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
        """Decode a text part to string"""
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
        """Decode a binary part to bytes"""
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