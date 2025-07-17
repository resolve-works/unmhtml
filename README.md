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
```

## Features

- **Pure Python** - No external dependencies, uses only standard library
- **Standalone HTML** - Embeds CSS and converts resources to data URIs
- **Graceful degradation** - Handles malformed MHTML files
- **Memory efficient** - Processes large files without excessive memory usage

## Requirements

- Python 3.8+

## License

MIT