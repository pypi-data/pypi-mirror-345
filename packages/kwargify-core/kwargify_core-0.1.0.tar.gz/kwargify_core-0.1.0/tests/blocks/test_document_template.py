import pytest
from kwargify_core.blocks.document_template import DocumentTemplateBlock


def test_basic_variable_substitution():
    """Test basic variable substitution in template."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": "Hello {{ name }}!",
        "data": {"name": "World"}
    }
    block.run()
    assert block.outputs["document"] == "Hello World!"


def test_multiple_variables():
    """Test template with multiple variables."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": "{{ greeting }} {{ name }}! Age: {{ age }}",
        "data": {
            "greeting": "Hello",
            "name": "John",
            "age": 30
        }
    }
    block.run()
    assert block.outputs["document"] == "Hello John! Age: 30"


def test_conditional_rendering():
    """Test conditional statements in template."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": """{% if age >= 18 %}Adult{% else %}Minor{% endif %}""",
        "data": {"age": 20}
    }
    block.run()
    assert block.outputs["document"] == "Adult"


def test_loop_rendering():
    """Test loop rendering in template."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": """Items:
{% for item in items %}
- {{ item }}
{% endfor %}""",
        "data": {"items": ["apple", "banana", "orange"]}
    }
    block.run()
    expected = """Items:
- apple
- banana
- orange"""
    # Normalize line endings and whitespace
    actual = "\n".join(line.strip() for line in block.outputs["document"].splitlines())
    expected = "\n".join(line.strip() for line in expected.splitlines())
    assert actual == expected


def test_nested_data():
    """Test template with nested dictionary data."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": """Name: {{ person.name }}
Age: {{ person.age }}
City: {{ person.address.city }}""",
        "data": {
            "person": {
                "name": "John",
                "age": 30,
                "address": {"city": "New York"}
            }
        }
    }
    block.run()
    expected = """Name: John
Age: 30
City: New York"""
    # Normalize line endings and whitespace
    actual = "\n".join(line.strip() for line in block.outputs["document"].splitlines())
    expected = "\n".join(line.strip() for line in expected.splitlines())
    assert actual == expected


def test_filters():
    """Test Jinja2 filters in template."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": """{{ name | upper }}
{{ names | join(', ') }}
{{ number | default(0) }}""",
        "data": {
            "name": "john",
            "names": ["apple", "banana", "orange"]
        }
    }
    block.run()
    expected = """JOHN
apple, banana, orange
0"""
    # Normalize line endings and whitespace
    actual = "\n".join(line.strip() for line in block.outputs["document"].splitlines())
    expected = "\n".join(line.strip() for line in expected.splitlines())
    assert actual == expected


def test_missing_template():
    """Test error handling for missing template."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "data": {"name": "John"}
    }
    with pytest.raises(ValueError, match="Missing 'template' input"):
        block.run()


def test_missing_data():
    """Test error handling for missing data."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": "Hello {{ name }}!"
    }
    with pytest.raises(ValueError, match="Missing 'data' input"):
        block.run()


def test_invalid_data_type():
    """Test error handling for invalid data type."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": "Hello {{ name }}!",
        "data": "not a dictionary"
    }
    with pytest.raises(ValueError, match="'data' input must be a dictionary"):
        block.run()


def test_undefined_variable():
    """Test error handling for undefined variables in template."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": "Hello {{ name }}! Age: {{ age }}",
        "data": {"name": "John"}  # age is missing
    }
    with pytest.raises(RuntimeError, match="Undefined variable"):
        block.run()


def test_syntax_error():
    """Test error handling for template syntax errors."""
    block = DocumentTemplateBlock()
    block.inputs = {
        "template": "{% if true %}",  # Missing endif
        "data": {"dummy": "data"}
    }
    with pytest.raises(RuntimeError, match="Template syntax error"):
        block.run()