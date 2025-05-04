from typing import Optional
from kwargify_core.core.block import Block
import litellm


class AIProcessorBlock(Block):
    """
    Block to process input text using an LLM via litellm.

    Config:
        - model (str): Model to use (e.g., 'gpt-4o', 'claude-3.5-sonnet').
        - temperature (float): Optional, defaults to 0.2

    Inputs:
        - content (str): Text to send to the LLM.
        - instructions (str): Optional, system-level instruction for the LLM.

    Outputs:
        - response (str): LLM's generated response.
    """

    def run(self) -> None:
        model = self.config.get("model", "gpt-4o-mini")
        temperature = self.config.get("temperature", 0.2)

        content: Optional[str] = self.inputs.get("content")
        if not content:
            raise ValueError("Missing 'content' input for AIProcessorBlock")

        instructions = self.inputs.get("instructions") or self.config.get("instructions", "You are a helpful assistant.")

        try:
            response = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": content},
                ],
                temperature=temperature
            )
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {str(e)}")

        self.outputs["response"] = response.choices[0].message["content"]
