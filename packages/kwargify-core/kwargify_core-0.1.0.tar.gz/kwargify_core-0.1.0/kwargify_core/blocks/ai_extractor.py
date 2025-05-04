from typing import Optional, Dict, Any
from kwargify_core.core.block import Block
import litellm
import json
import re


class AIExtractorBlock(Block):
    """
    Block to extract structured data from text using an LLM via litellm.

    Config:
        - model (str): Model to use (e.g., 'gpt-4o', 'claude-3.5-sonnet').
        - temperature (float): Optional, defaults to 0.2

    Inputs:
        - content (str): Text from which to extract data.
        - extraction_fields (Dict[str, Dict[str, str]]): Fields to extract with their properties.
          Format: {
              "field_name": {
                  "type": "string|number|boolean|array",
                  "description": "Description of what to extract"
              }
          }

    Outputs:
        - extracted_data (Dict[str, Any]): Structured data extracted from the content.
        - raw_response (str): Optional raw LLM response for debugging.
    """

    def _clean_json_response(self, response: str) -> str:
        """Clean the LLM response to extract valid JSON."""
        # Try to find JSON-like structure using regex
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            potential_json = json_match.group(0)
            try:
                # Verify it's valid JSON
                json.loads(potential_json)
                return potential_json
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Could not find valid JSON in response: {response}")

    def _generate_extraction_prompt(self, content: str, fields: Dict[str, Dict[str, str]]) -> str:
        fields_description = "\n".join([
            f"- {field}: {props['type']} - {props['description']}"
            for field, props in fields.items()
        ])
        
        return f"""Extract the following fields from the given content.
        
Fields to extract:
{fields_description}

IMPORTANT: You must respond with ONLY a valid JSON object. Do not include any explanations or additional text.
If a field cannot be extracted, use null as the value.

Content to process:
{content}

Required output format:
{{
    "field1": "value1",
    "field2": 42,
    "field3": null
}}"""

    def run(self) -> None:
        model = self.config.get("model", "gpt-4o-mini")
        temperature = self.config.get("temperature", 0.2)

        content: Optional[str] = self.inputs.get("content")
        if not content:
            raise ValueError("Missing 'content' input for AIExtractorBlock")

        extraction_fields = self.inputs.get("extraction_fields")
        if not extraction_fields:
            raise ValueError("Missing 'extraction_fields' input for AIExtractorBlock")

        prompt = self._generate_extraction_prompt(content, extraction_fields)

        try:
            response = litellm.completion(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data extraction assistant. Your ONLY task is to extract the requested information and return it as a valid JSON object. DO NOT include any other text or explanation in your response."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature
            )

            raw_response = response.choices[0].message["content"]
            
            # Store raw response for debugging
            self.outputs["raw_response"] = raw_response

            if not raw_response.strip():
                raise ValueError("Empty response received from LLM")
            
            # Try to clean and extract JSON from the response
            try:
                cleaned_response = self._clean_json_response(raw_response)
                extracted_data = json.loads(cleaned_response)
                self.outputs["extracted_data"] = extracted_data
            except (ValueError, json.JSONDecodeError) as e:
                raise ValueError(f"Failed to extract valid JSON from LLM response: {str(e)}\nRaw response: {raw_response}")

        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            raise RuntimeError(f"LLM call failed: {str(e)}")