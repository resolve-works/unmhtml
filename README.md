# unmhtml

Convert MHTML files to standalone HTML with embedded CSS and resources.

## Installation

```bash
pip install unmhtml
```

## Usage

```python
from unmhtml import MHTMLConverter

# Convert MHTML file to HTML
converter = MHTMLConverter()
html_content = converter.convert_file('saved_page.mhtml')

# Save as standalone HTML
with open('output.html', 'w') as f:
    f.write(html_content)

# Secure conversion with JavaScript removal
secure_converter = MHTMLConverter(remove_javascript=True)
html_content = secure_converter.convert_file('untrusted_page.mhtml')
```

## Features

- **Pure Python** - No external dependencies, uses only standard library
- **Standalone HTML** - Embeds CSS and converts resources to data URIs
- **Security** - Optional JavaScript removal for safe display of untrusted content
- **Graceful degradation** - Handles malformed MHTML files
- **Memory efficient** - Processes large files without excessive memory usage

## Security

When processing untrusted MHTML files, use the `remove_javascript=True` option to remove potentially dangerous content:

- Removes `<script>` tags and their contents
- Removes event handlers (onclick, onload, etc.)
- Converts `javascript:` URLs to safe `#` anchors

```python
# Safe for displaying untrusted content
secure_converter = MHTMLConverter(remove_javascript=True)
html_content = secure_converter.convert_file('untrusted.mhtml')
```

## Requirements

- Python 3.8+

## License

MIT