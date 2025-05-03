# Py Level Fleet

A powerful Vue.js-like templating engine for Python using Jinja2. This package provides a familiar Vue.js syntax while leveraging the robust features of Jinja2.

## Features

- Vue.js-like template syntax with `p-` directives
- Full Jinja2 template engine capabilities
- Support for async rendering
- Sandboxed environment for security
- I18N support
- BeautifulSoup4 for HTML parsing
- Template caching for better performance

## Installation

```bash
pip install py_level_fleet
```

## Quick Start

```python
from py_level_fleet import render_template

template = """
<div p-if="show">
    <p p-text="message"></p>
</div>
<ul>
    <li p-for="item in items" p-key="item.id">{{ item.name }}</li>
</ul>
"""

data = {
    'show': True,
    'message': 'Hello, World!',
    'items': [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}]
}

output = render_template(template, data)
print(output)
```

## Available Directives

- `p-if`: Conditional rendering
- `p-else-if`: Alternative condition
- `p-else`: Fallback content
- `p-for`: List rendering
- `p-key`: Unique key for list items
- `p-bind`: Dynamic attribute binding
- `p-text`: Text content binding
- `p-html`: HTML content binding
- `p-show`: Conditional display
- `p-on`: Event handling
- `p-model`: Two-way data binding
- `p-pre`: Skip compilation
- `p-once`: Render once
- `p-cloak`: Hide until compiled

## Advanced Usage

### Async Rendering

```python
from py_level_fleet import VueJinjaEngine

engine = VueJinjaEngine(enable_async=True)
output = await engine.render_template_async(template, data)
```

### Sandboxed Environment

```python
from py_level_fleet import VueJinjaEngine

engine = VueJinjaEngine(sandboxed=True)
output = engine.render_template(template, data)
```

### I18N Support

```python
from py_level_fleet import VueJinjaEngine
from babel.support import Translations

translations = Translations.load('locale', ['en'])
engine = VueJinjaEngine(i18n_translations=translations)
output = engine.render_template(template, data)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Vishnu Prasad - [GitHub](https://github.com/vishnuprasad)

## Acknowledgments

- [Jinja2](https://jinja.palletsprojects.com/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Vue.js](https://vuejs.org/) 