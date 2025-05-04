import os
from typing import Optional
from kwargify_core.core.block import Block


class WriteFileBlock(Block):
    """
    Block to write content to a file.

    Config:
        - path (str): Destination file path.
        - encoding (str, optional): Encoding to use (default: 'utf-8').
        - mode (str, optional): File mode - 'w' (overwrite) or 'a' (append). Default is 'w'.

    Inputs:
        - content (str): The content to write.

    Outputs:
        - path (str): The full path of the written file.
    """

    def run(self) -> None:
        path: Optional[str] = self.config.get("path")
        encoding: str = self.config.get("encoding", "utf-8")
        mode: str = self.config.get("mode", "w")

        if not path:
            raise ValueError("Missing 'path' in config for WriteFileBlock")

        content = self.inputs.get("content")
        if content is None:
            raise ValueError("No 'content' found in inputs for WriteFileBlock")

        try:
            with open(path, mode, encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            raise RuntimeError(f"Failed to write to file {path}: {str(e)}")

        self.outputs["path"] = os.path.abspath(path)
