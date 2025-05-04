import pytest
from kwargify_core.blocks.json_to_string import JsonToStringBlock


def test_json_to_string_basic_dict():
    block = JsonToStringBlock(name="TestJsonConverter")
    data = {"key": "value", "number": 42}
    block.inputs["data"] = data
    block.run()
    
    assert "json_string" in block.outputs
    assert block.outputs["json_string"] == '{"key": "value", "number": 42}'


def test_json_to_string_with_indent():
    block = JsonToStringBlock(
        name="TestJsonConverter",
        config={"indent": 2}
    )
    data = {"nested": {"key": "value"}}
    block.inputs["data"] = data
    block.run()
    
    expected = '''{
  "nested": {
    "key": "value"
  }
}'''
    assert block.outputs["json_string"] == expected


def test_json_to_string_with_non_ascii():
    block = JsonToStringBlock(
        name="TestJsonConverter",
        config={"ensure_ascii": False}
    )
    data = {"text": "Hello 世界"}
    block.inputs["data"] = data
    block.run()
    
    assert block.outputs["json_string"] == '{"text": "Hello 世界"}'


def test_json_to_string_missing_data():
    block = JsonToStringBlock(name="TestJsonConverter")
    
    with pytest.raises(ValueError) as exc_info:
        block.run()
    
    assert "Missing required input 'data'" in str(exc_info.value)


def test_json_to_string_invalid_data():
    block = JsonToStringBlock(name="TestJsonConverter")
    # Create an object with circular reference
    data = {"self": None}
    data["self"] = data
    block.inputs["data"] = data
    
    with pytest.raises(RuntimeError) as exc_info:
        block.run()
    
    assert "Failed to convert data to JSON string" in str(exc_info.value)