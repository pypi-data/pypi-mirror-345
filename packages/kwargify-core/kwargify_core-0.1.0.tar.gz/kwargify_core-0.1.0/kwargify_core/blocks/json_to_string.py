import json
from typing import Any, Dict, Optional

from kwargify_core.core.block import Block


class JsonToStringBlock(Block):
    """
    Block to convert a Python object to a JSON string.

    Config:
        - indent (int, optional): Number of spaces for indentation (default: None)
        - ensure_ascii (bool, optional): If true, non-ASCII characters are escaped (default: True)

    Inputs:
        - data (Any): The Python object (dict, list, etc.) to convert to JSON string

    Outputs:
        - json_string (str): The resulting JSON string
    """

    def run(self) -> None:
        data: Optional[Any] = self.inputs.get("data")
        indent: Optional[int] = self.config.get("indent")
        ensure_ascii: bool = self.config.get("ensure_ascii", True)

        if data is None:
            raise ValueError("Missing required input 'data' for JsonToStringBlock")

        try:
            json_string = json.dumps(
                data,
                indent=indent,
                ensure_ascii=ensure_ascii
            )
        except Exception as e:
            raise RuntimeError(f"Failed to convert data to JSON string: {str(e)}")

        self.outputs["json_string"] = json_string