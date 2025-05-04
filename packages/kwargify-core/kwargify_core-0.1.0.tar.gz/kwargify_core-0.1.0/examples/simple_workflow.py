import tempfile
import os
import litellm

from kwargify_core.core.workflow import Workflow
from kwargify_core.blocks.read_file import ReadFileBlock
from kwargify_core.blocks.write_file import WriteFileBlock
from kwargify_core.blocks.ai_processor import AIProcessorBlock
from dotenv import load_dotenv

# Set your OpenAI API Key
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Step 1: Create temporary input file with some text data
with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp_in:
    tmp_in.write("Python is a powerful language often used for data science and AI.")
    tmp_in.flush()
    input_path = tmp_in.name

# Create output file path
output_fd, output_path = tempfile.mkstemp(suffix=".txt")
os.close(output_fd)  # Close so WriteFileBlock can overwrite

# Step 2: Create the blocks for the workflow

read_block = ReadFileBlock(name="MyReadFile", config={"path": input_path})
ai_block = AIProcessorBlock(name="MyAIProcessor", config={"model": "gpt-4o-mini", "api_key": api_key})
write_block = WriteFileBlock(name="MyWriteFile", config={"path": output_path})

# Define dependencies
ai_block.add_dependency(read_block)
write_block.add_dependency(ai_block)

# Manually wire AI block's output to write block's input
write_block.input_map = {"content": (ai_block, "response")}

# Step 3: Create and run the workflow
wf = Workflow()
wf.add_block(read_block)
wf.add_block(ai_block)
wf.add_block(write_block)

mermaid_output = wf.to_mermaid()
print("Mermaid Output:")
print(mermaid_output)

# Run the workflow
wf.run()

# Step 4: Read and output the content from the output file
with open(output_path, "r") as f:
    output_content = f.read()

print("Output Content:")
print(output_content)  # Should print the AI-generated summary