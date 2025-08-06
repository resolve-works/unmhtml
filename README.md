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

# Secure conversion with all security options
secure_converter = MHTMLConverter(
    remove_javascript=True,
    sanitize_css=True,
    remove_forms=True
)
html_content = secure_converter.convert_file('untrusted_page.mhtml')
```

## Features

- **Pure Python** - No external dependencies, uses only standard library
- **Standalone HTML** - Embeds CSS and converts resources to data URIs
- **Comprehensive Security** - Multiple sanitization options for safe display of untrusted content
- **Graceful degradation** - Handles malformed MHTML files
- **Memory efficient** - Processes large files without excessive memory usage

## Security

The library provides comprehensive security options for safe display of untrusted content:

### Available Security Options

- **`remove_javascript=True`** - Removes `<script>` tags, event handlers (onclick, onload, etc.), and converts `javascript:` URLs to safe `#` anchors
- **`sanitize_css=True`** - Removes CSS properties that can make network requests (`url()`, `@import`, `expression()`, `behavior:`)
- **`remove_forms=True`** - Removes form elements (`<form>`, `<input>`, `<textarea>`, `<select>`) that could submit data externally

### Usage Examples

```python
# JavaScript removal only
secure_converter = MHTMLConverter(remove_javascript=True)

# Maximum security for untrusted content
safe_converter = MHTMLConverter(
    remove_javascript=True,
    sanitize_css=True,
    remove_forms=True
)
html_content = safe_converter.convert_file('untrusted.mhtml')
```

## Requirements

- Python 3.8+

## License

MIT