import tempfile
from kwargify_core.blocks.read_file import ReadFileBlock


def test_read_file_block_reads_text():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp:
        tmp.write("Hello from test file!")
        tmp.flush()

        block = ReadFileBlock(config={"path": tmp.name})
        block.run()

        assert "content" in block.outputs
        assert block.outputs["content"] == "Hello from test file!"
        assert block.outputs["filename"] == tmp.name.split("/")[-1]
