import tempfile
import os
from kwargify_core.blocks.write_file import WriteFileBlock


def test_write_file_block_writes_text():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        path = tmp.name

    block = WriteFileBlock(config={"path": path})
    block.set_input("content", "Hello world from test!")
    block.run()

    with open(path, "r") as f:
        content = f.read()

    assert content == "Hello world from test!"
    assert os.path.exists(block.outputs["path"])
