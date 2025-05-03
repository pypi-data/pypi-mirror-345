from bs4 import BeautifulSoup, NavigableString
import jinja2
from jinja2.ext import i18n
from jinja2.sandbox import SandboxedEnvironment
import uuid
import asyncio

class VueJinjaEngine:
    def __init__(self, sandboxed=False, enable_async=False, i18n_translations=None):
        """
        Initialize the VueJinja engine with customizable settings.
        
        Args:
            sandboxed (bool): Use SandboxedEnvironment for untrusted templates.
            enable_async (bool): Enable AsyncIO support.
            i18n_translations: Babel translations object for I18N support.
        """
        env_class = SandboxedEnvironment if sandboxed else jinja2.Environment
        self.env = env_class(
            block_start_string='{{',
            block_end_string='}}',
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='{#',
            comment_end_string='#}',
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            enable_async=enable_async,
            extensions=[i18n] if i18n_translations else [],
            cache_size=400  # Enable template caching
        )
        
        # Install I18N translations if provided
        if i18n_translations:
            self.env.install_gettext_translations(i18n_translations)
        
        # Add custom globals and filters
        self.env.globals['set_key'] = lambda x: ''  # Placeholder for p-key
        self.env.filters['custom_upper'] = lambda x: str(x).upper()  # Example extensible filter

    def transform_template(self, template_string):
        """Transform HTML template with p- directives into Jinja2 syntax."""
        soup = BeautifulSoup(template_string, 'html.parser')

        def transform(node):
            if isinstance(node, NavigableString):
                return str(node)
            elif not node.name:
                return ''
            else:
                # Handle p-pre (skip compilation)
                if 'p-pre' in node.attrs:
                    del node['p-pre']
                    return str(node)

                # Handle p-for with p-key
                if 'p-for' in node.attrs:
                    loop = node['p-for']
                    key_attr = node.attrs.get('p-key', '')
                    del node['p-for']
                    if 'p-key' in node.attrs:
                        del node['p-key']
                    transformed = transform(node)
                    if key_attr:
                        return f"{{{{ for {loop}: }}}}{{ set_key('{key_attr}') }}{transformed}{{ end }}"
                    return f"{{{{ for {loop}: }}}}{transformed}{{ end }}"

                # Handle attribute directives
                attrs = []
                content = None
                for attr, value in list(node.attrs.items()):
                    if attr.startswith('p-bind:'):
                        attr_name = attr[7:]
                        attrs.append(f'{attr_name}="{{{{ {value} }}}}"')
                        del node[attr]
                    elif attr == 'p-text':
                        content = f"{{{{ {value} }}}}"
                        del node[attr]
                    elif attr == 'p-html':
                        content = f"{{{{ {value} | safe }}}}"
                        del node[attr]
                    elif attr == 'p-show':
                        style = f"{{{{ 'display: block;' if {value} else 'display: none;' }}}}"
                        attrs.append(f'style="{style}"')
                        del node[attr]
                    elif attr.startswith('p-on:'):
                        event = attr[5:]
                        attrs.append(f'{event}="{value}"')
                        del node[attr]
                    elif attr == 'p-model':
                        attrs.append(f'name="{value}" value="{{{{ {value} }}}}"')
                        del node[attr]
                    elif attr == 'p-once' or attr == 'p-cloak':
                        del node[attr]
                    else:
                        attrs.append(f'{attr}="{value}"')

                attrs_str = ' '.join(attrs) if attrs else ''
                children = content if content is not None else ''.join(transform(child) for child in node.children)
                return f"<{node.name}{' ' if attrs_str else ''}{attrs_str}>{children}</{node.name}>"

        def transform_children(parent):
            i = 0
            result = ''
            while i < len(parent.contents):
                child = parent.contents[i]
                if child.name and 'p-if' in child.attrs:
                    group = [child]
                    j = i + 1
                    while j < len(parent.contents):
                        next_child = parent.contents[j]
                        if next_child.name and ('p-else-if' in next_child.attrs or 'p-else' in next_child.attrs):
                            group.append(next_child)
                            j += 1
                        else:
                            break
                    result += transform_conditional_group(group)
                    i = j
                else:
                    result += transform(child)
                    i += 1
            return result

        def transform_conditional_group(group):
            result = ''
            for idx, elem in enumerate(group):
                if idx == 0:
                    condition = elem['p-if']
                    del elem['p-if']
                    content = transform(elem)
                    result += f"{{{{ if {condition}: }}}}{content}"
                elif 'p-else-if' in elem.attrs:
                    condition = elem['p-else-if']
                    del elem['p-else-if']
                    content = transform(elem)
                    result += f"{{{{ elif {condition}: }}}}{content}"
                elif 'p-else' in elem.attrs:
                    del elem['p-else']
                    content = transform(elem)
                    result += f"{{{{ else: }}}}{content}"
            result += "{{ end }}"
            return result

        return transform_children(soup)

    def render_template(self, template_string, data):
        """Render the template synchronously."""
        transformed = self.transform_template(template_string)
        template = self.env.from_string(transformed)
        return template.render(**data)

    async def render_template_async(self, template_string, data):
        """Render the template asynchronously."""
        transformed = self.transform_template(template_string)
        template = self.env.from_string(transformed)
        return await template.render_async(**data)

# Convenience function for default usage
def render_template(template_string, data, sandboxed=False, enable_async=False, i18n_translations=None):
    engine = VueJinjaEngine(sandboxed=sandboxed, enable_async=enable_async, i18n_translations=i18n_translations)
    return engine.render_template(template_string, data)

# Example usage
if __name__ == "__main__":
    template = """
    {{ extends "base.html" }}
    {{ block content }}
        <div p-if="show">
            <p p-text="message"></p>
        </div>
        <div p-else>
            Not shown
        </div>
        <ul>
            <li p-for="item in items" p-key="item.id">{{ item.name }}</li>
        </ul>
        <img p-bind:src="image_url" p-show="visible">
        {{ _gettext('Hello') }}
    {{ endblock }}
    """

    data = {
        'show': True,
        'message': 'Hello, World!',
        'items': [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}],
        'image_url': 'http://example.com/image.jpg',
        'visible': True
    }

    output = render_template(template, data, sandboxed=True)
    print(output)