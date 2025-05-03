"""
Basic tests for fleetvue package.
"""

import pytest
from fleetvue import render_template, VueJinjaEngine

def test_basic_rendering():
    template = '<div p-text="message"></div>'
    data = {'message': 'Hello World'}
    result = render_template(template, data)
    assert '<div>Hello World</div>' in result

def test_conditional_rendering():
    template = '<div p-if="show">Visible</div>'
    assert 'Visible' in render_template(template, {'show': True})
    assert 'Visible' not in render_template(template, {'show': False})

def test_list_rendering():
    template = '<ul><li p-for="item in items" p-text="item"></li></ul>'
    data = {'items': ['one', 'two', 'three']}
    result = render_template(template, data)
    assert '<li>one</li>' in result
    assert '<li>two</li>' in result
    assert '<li>three</li>' in result

def test_attribute_binding():
    template = '<img p-bind:src="url">'
    data = {'url': 'https://example.com/image.jpg'}
    result = render_template(template, data)
    assert 'src="https://example.com/image.jpg"' in result

@pytest.mark.asyncio
async def test_async_rendering():
    engine = VueJinjaEngine(enable_async=True)
    template = '<div p-text="message"></div>'
    data = {'message': 'Hello World'}
    result = await engine.render_template_async(template, data)
    assert '<div>Hello World</div>' in result

def test_sandboxed_environment():
    engine = VueJinjaEngine(sandboxed=True)
    template = '<div p-text="message | upper"></div>'
    data = {'message': 'hello'}
    result = engine.render_template(template, data)
    assert '<div>HELLO</div>' in result

def test_custom_filter():
    engine = VueJinjaEngine()
    engine.env.filters['double'] = lambda x: x * 2
    template = '<div p-text="number | double"></div>'
    data = {'number': 21}
    result = engine.render_template(template, data)
    assert '<div>42</div>' in result 