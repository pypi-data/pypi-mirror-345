import os
from typing import Optional
from kwargify_core.core.block import Block


class ReadFileBlock(Block):
    """
    Block to read plain text or markdown files.

    Config:
        - path (str): Path to the file to read.
        - encoding (str, optional): File encoding (default is 'utf-8').

    Outputs:
        - content (str): The full contents of the file.
        - filename (str): Name of the file (basename only).
    """

    def run(self) -> None:
        path: Optional[str] = self.config.get("path")
        encoding: str = self.config.get("encoding", "utf-8")

        if not path:
            raise ValueError("Missing 'path' in config for ReadFileBlock")

        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read file {path}: {str(e)}")

        self.outputs["content"] = content
        self.outputs["filename"] = os.path.basename(path)
