from unittest.mock import patch, Mock
import pytest
from kwargify_core.blocks.ai_extractor import AIExtractorBlock


def test_ai_extractor_missing_content():
    block = AIExtractorBlock()
    block.inputs = {
        "extraction_fields": {
            "name": {"type": "string", "description": "Extract person name"}
        }
    }
    
    with pytest.raises(ValueError, match="Missing 'content' input"):
        block.run()


def test_ai_extractor_missing_fields():
    block = AIExtractorBlock()
    block.inputs = {
        "content": "Hello, my name is John Doe"
    }
    
    with pytest.raises(ValueError, match="Missing 'extraction_fields' input"):
        block.run()


def test_clean_json_response():
    block = AIExtractorBlock()
    
    # Test clean JSON
    clean_json = '{"name": "John", "age": 30}'
    assert block._clean_json_response(clean_json) == clean_json
    
    # Test JSON with surrounding text
    messy_json = 'Here is the extracted data: {"name": "John", "age": 30} End of response.'
    assert block._clean_json_response(messy_json) == '{"name": "John", "age": 30}'
    
    # Test invalid input
    with pytest.raises(ValueError, match="Could not find valid JSON"):
        block._clean_json_response("No JSON here")


@patch('litellm.completion')
def test_ai_extractor_successful_extraction(mock_completion):
    # Mock LLM response
    mock_response = Mock()
    mock_response.choices = [
        Mock(message={"content": '{"name": "John Doe", "age": 30}'})
    ]
    mock_completion.return_value = mock_response

    block = AIExtractorBlock()
    block.inputs = {
        "content": "Hello, my name is John Doe and I am 30 years old",
        "extraction_fields": {
            "name": {"type": "string", "description": "Extract person name"},
            "age": {"type": "number", "description": "Extract person age"}
        }
    }

    block.run()

    assert "extracted_data" in block.outputs
    assert block.outputs["extracted_data"] == {"name": "John Doe", "age": 30}
    assert "raw_response" in block.outputs
    assert block.outputs["raw_response"] == '{"name": "John Doe", "age": 30}'


@patch('litellm.completion')
def test_ai_extractor_messy_json_response(mock_completion):
    # Mock LLM response with surrounding text
    mock_response = Mock()
    mock_response.choices = [
        Mock(message={"content": 'Here is the extracted information:\n{"name": "John Doe", "age": 30}\nEnd of response'})
    ]
    mock_completion.return_value = mock_response

    block = AIExtractorBlock()
    block.inputs = {
        "content": "Some content",
        "extraction_fields": {
            "name": {"type": "string", "description": "Name"},
            "age": {"type": "number", "description": "Age"}
        }
    }

    block.run()
    assert block.outputs["extracted_data"] == {"name": "John Doe", "age": 30}


@patch('litellm.completion')
def test_ai_extractor_empty_response(mock_completion):
    # Mock empty response
    mock_response = Mock()
    mock_response.choices = [
        Mock(message={"content": ""})
    ]
    mock_completion.return_value = mock_response

    block = AIExtractorBlock()
    block.inputs = {
        "content": "Some content",
        "extraction_fields": {
            "field1": {"type": "string", "description": "Some field"}
        }
    }

    with pytest.raises(ValueError, match="Empty response received from LLM"):
        block.run()


@patch('litellm.completion')
def test_ai_extractor_invalid_json_response(mock_completion):
    # Mock invalid JSON response
    mock_response = Mock()
    mock_response.choices = [
        Mock(message={"content": "Invalid JSON response"})
    ]
    mock_completion.return_value = mock_response

    block = AIExtractorBlock()
    block.inputs = {
        "content": "Some content",
        "extraction_fields": {
            "field1": {"type": "string", "description": "Some field"}
        }
    }

    with pytest.raises(ValueError, match="Failed to extract valid JSON from LLM response"):
        block.run()


@patch('litellm.completion')
def test_ai_extractor_llm_error(mock_completion):
    # Mock LLM error
    mock_completion.side_effect = Exception("LLM API error")

    block = AIExtractorBlock()
    block.inputs = {
        "content": "Some content",
        "extraction_fields": {
            "field1": {"type": "string", "description": "Some field"}
        }
    }

    with pytest.raises(RuntimeError, match="LLM call failed"):
        block.run()


def test_ai_extractor_prompt_generation():
    block = AIExtractorBlock()
    content = "Test content"
    fields = {
        "name": {"type": "string", "description": "Person name"},
        "age": {"type": "number", "description": "Person age"}
    }
    
    prompt = block._generate_extraction_prompt(content, fields)
    
    assert "Test content" in prompt
    assert "name: string - Person name" in prompt
    assert "age: number - Person age" in prompt
    assert "valid JSON" in prompt