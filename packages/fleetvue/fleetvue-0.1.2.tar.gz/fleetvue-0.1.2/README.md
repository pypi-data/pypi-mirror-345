# FleetVue

A powerful Vue.js-like templating engine for Python using Jinja2. FleetVue brings the familiar Vue.js syntax to Python while leveraging the robust features of Jinja2.

## Features

- Vue.js-like template syntax with `p-` directives
- Full Jinja2 template engine capabilities
- Support for async rendering
- Sandboxed environment for security
- BeautifulSoup4 for HTML parsing
- Template caching for better performance
- Custom filters support

## Installation

```bash
pip install fleetvue
```

## Quick Start

```python
from fleetvue import render_template

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

### Custom Engine Configuration

```python
from fleetvue import VueJinjaEngine

# Create a custom engine instance
engine = VueJinjaEngine(
    sandboxed=True,  # Use sandboxed environment for security
    enable_async=True  # Enable async support
)

# Add custom filters
engine.env.filters['uppercase'] = lambda x: str(x).upper()

# Use the engine
template = '<h1 p-text="title | uppercase"></h1>'
data = {'title': 'Hello World'}
output = engine.render_template(template, data)
```

### Async Rendering

```python
import asyncio
from fleetvue import VueJinjaEngine

async def main():
    engine = VueJinjaEngine(enable_async=True)
    template = '<div p-text="message"></div>'
    data = {'message': 'Hello World'}
    output = await engine.render_template_async(template, data)
    print(output)

asyncio.run(main())
```

### Sandboxed Environment

```python
from fleetvue import VueJinjaEngine

engine = VueJinjaEngine(sandboxed=True)
output = engine.render_template(template, data)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Vishnu Prasad - [GitHub](https://github.com/vishnuprasad)

## Acknowledgments

- [Jinja2](https://jinja.palletsprojects.com/) for the powerful templating engine
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Vue.js](https://vuejs.org/) for the inspiration and syntax 