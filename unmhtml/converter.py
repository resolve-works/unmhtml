from .parser import MHTMLParser
from .processor import HTMLProcessor


class MHTMLConverter:
    def convert_file(self, mhtml_path: str) -> str:
        """Convert MHTML file to HTML string"""
        try:
            with open(mhtml_path, 'r', encoding='utf-8') as f:
                mhtml_content = f.read()
            return self.convert(mhtml_content)
        except Exception as e:
            raise ValueError(f"Failed to read MHTML file: {e}")
        
    def convert(self, mhtml_content: str) -> str:
        """Convert MHTML content to HTML string"""
        try:
            # Parse MHTML to extract HTML and resources
            parser = MHTMLParser(mhtml_content)
            main_html, resources = parser.parse()
            
            # If we got the original content back, it means the MHTML is malformed
            if main_html == mhtml_content:
                raise ValueError("No HTML content found in MHTML")
            
            if not main_html:
                raise ValueError("No HTML content found in MHTML")
            
            # Process HTML to embed CSS and convert resources
            processor = HTMLProcessor(main_html, resources)
            html_with_css = processor.embed_css()
            processor.html_content = html_with_css  # Update processor with embedded CSS
            final_html = processor.convert_to_data_uris()
            
            return final_html
            
        except Exception as e:
            raise ValueError(f"Failed to convert MHTML: {e}")