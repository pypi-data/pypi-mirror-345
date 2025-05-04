# Kwargify Core: A Python Workflow Framework

A powerful Python framework for building and managing workflow pipelines with AI integration capabilities. Kwargify Core enables you to create modular, reusable workflows by connecting specialized blocks that handle various tasks like file operations, AI processing, data transformation, and document generation.

## Features

- **DAG-based Workflow Definition:** Create complex workflows using a directed acyclic graph structure
- **Modular Block System:** Pre-built blocks for common tasks with ability to create custom blocks
- **Flexible Data Flow:** Wire outputs from one block to inputs of another using intuitive mapping
- **Command Line Interface:** Run, manage, register, and visualize workflows from the command line
- **Workflow Registry:** Version and catalog your workflows for easy reuse
- **Built-in Logging:** Comprehensive SQLite-based logging of workflow execution details
- **Resume Capability:** Continue interrupted workflows from where they left off
- **Retry Mechanism:** Automatically retry failed blocks to handle transient errors
- **AI Integration:** Seamlessly integrate with AI models using built-in blocks
- **Template Processing:** Generate documents using dynamic templates

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/kwargify-core.git
cd kwargify-core

# Install using Poetry
poetry install
```

## Core Concepts

### Workflows

A workflow in Kwargify Core is a directed acyclic graph (DAG) of connected blocks. Each workflow:
- Manages the execution order based on block dependencies
- Provides retry capabilities for error handling
- Supports resuming from previous runs
- Automatically logs execution details

Example of creating a workflow:

```python
from kwargify_core.core.workflow import Workflow
from kwargify_core.blocks import ReadFileBlock, AIProcessorBlock, WriteFileBlock

# Create workflow with default retry count of 2
workflow = Workflow(default_max_retries=2)
workflow.name = "DocumentProcessor"

# Add blocks
reader = ReadFileBlock(name="FileReader", config={"path": "input.txt"})
processor = AIProcessorBlock(name="AIProcessor")
writer = WriteFileBlock(name="FileWriter", config={"path": "output.txt"})

# Add dependencies
processor.add_dependency(reader)
writer.add_dependency(processor)

# Wire block inputs/outputs
processor.input_map = {"content": (reader, "content")}
writer.input_map = {"content": (processor, "response")}

# Add blocks to workflow
workflow.add_block(reader)
workflow.add_block(processor)
workflow.add_block(writer)

# Run the workflow
workflow.run()
```

### Blocks

Blocks are the fundamental units of work in a workflow. Each block:
- Encapsulates specific functionality
- Can have configurable parameters
- Has defined inputs and outputs
- Can depend on other blocks
- Can specify retry behavior

Block inputs can be wired to outputs of other blocks using `input_map`, enabling flexible data flow through the workflow.

## Command Line Interface (CLI)

Kwargify provides a powerful command-line interface for running and managing workflows. For detailed information, examples, and best practices, see our [CLI Usage Guide](docs/cli_usage_guide.md).

Here are some common commands to get started:

```bash
# Show CLI help
kwargify --help

# Show version
kwargify --version

# Run a workflow from a file
kwargify run path/to/workflow.py

# Run a registered workflow
kwargify run --name my-workflow [--version 1]

# Register a workflow
kwargify register path/to/workflow.py

# List registered workflows
kwargify list

# Validate a workflow
kwargify validate path/to/workflow.py

# Show workflow structure
kwargify show path/to/workflow.py
kwargify show path/to/workflow.py --diagram  # Show as Mermaid diagram
```

### Example: Contract Analysis Workflow

The `examples/contract_report_workflow_cli.py` demonstrates a workflow that analyzes contracts using AI and generates reports.

1. Set up environment variables:
```bash
# Create .env file from example
cp .env.example .env

# Edit .env to add your OpenAI API key
OPENAI_API_KEY=your-api-key-here

# Set input/output paths (optional)
export CONTRACT_INPUT_PATH=/path/to/contract.txt
export CONTRACT_OUTPUT_PATH=/path/to/report.txt
```

2. Run the workflow:
```bash
# Using default paths (contract.txt and report.txt)
kwargify run examples/contract_report_workflow_cli.py

# Or with custom paths via environment variables
CONTRACT_INPUT_PATH=input.txt CONTRACT_OUTPUT_PATH=output.txt kwargify run examples/contract_report_workflow_cli.py
```

## Creating CLI-Compatible Workflows

For complete workflow creation guidelines and best practices, see our [CLI Usage Guide](docs/cli_usage_guide.md#creating-cli-compatible-workflows).

Basic workflow structure:

### File Structure
Workflows are defined in Python files with a specific structure:

1. Required Components:
   - A `get_workflow()` function that returns a `Workflow` instance
   - Clear naming for the workflow using `workflow.name`
   - Properly configured blocks with dependencies

2. Example Structure:
```python
from kwargify_core.core.workflow import Workflow
from kwargify_core.core.block import Block
from kwargify_core.blocks import ReadFileBlock, AIProcessorBlock, WriteFileBlock

def get_workflow() -> Workflow:
    # Create workflow
    workflow = Workflow()
    workflow.name = "ContractAnalysis"
    
    # Create blocks
    reader = ReadFileBlock(
        name="contract_reader",
        config={"path": os.getenv("CONTRACT_INPUT_PATH", "contract.txt")}
    )
    
    analyzer = AIProcessorBlock(
        name="contract_analyzer",
        config={"model": "gpt-4o-mini"}
    )
    analyzer.add_dependency(reader)
    
    writer = WriteFileBlock(
        name="report_writer",
        config={"path": os.getenv("OUTPUT_PATH", "report.txt")}
    )
    writer.add_dependency(analyzer)
    
    # Add blocks to workflow
    workflow.add_block(reader)
    workflow.add_block(analyzer)
    workflow.add_block(writer)
    
    return workflow
```

### Best Practices
1. Configuration:
   - Use environment variables for configurable paths and settings
   - Provide sensible defaults for optional configurations
   - Keep sensitive data (API keys, credentials) in environment variables

2. Naming and Structure:
   - Use descriptive names for workflows and blocks
   - Organize blocks logically with clear dependencies
   - Comment complex configurations or dependencies

3. Error Handling:
   - Implement proper error handling in custom blocks
   - Validate inputs and configurations
   - Provide meaningful error messages

### Workflow Registry
The registry allows you to catalog and version your workflows:

1. Registering a Workflow:
```bash
# Register a workflow
kwargify register path/to/workflow.py

# List registered workflows
kwargify list

# Run a registered workflow by name
kwargify run --name my-workflow
```

2. Version Control:
   - Each registration creates a new version
   - Run specific versions using `--version`
   - Registry tracks metadata and execution history

## Logging

Kwargify Core automatically logs workflow execution details to an SQLite database (default: `kwargify_runs.db`). This logging system:

### What is Logged
- Workflow runs (start time, end time, status)
- Block executions (inputs, outputs, status)
- Error messages and stack traces
- Number of retry attempts
- Resume information

### Database Structure
- `run_summary`: Overall workflow run information
- `run_details`: Individual block execution details
- `run_logs`: Detailed log messages
- `workflows`: Registered workflow information
- `workflow_versions`: Version history of registered workflows

### Log Data Usage
- Debugging workflow execution
- Monitoring block performance
- Supporting the resume functionality
- Analyzing workflow history

## Resume and Retry

### Retry Mechanism
Blocks can automatically retry on failure:

```python
# Set workflow-wide default
workflow = Workflow(default_max_retries=3)

# Or set per-block
block = MyBlock(name="RetryBlock")
block.max_retries = 5  # Overrides workflow default
```

When a block fails:
1. The error is logged
2. The block waits 1 second
3. Execution is retried up to the specified limit
4. If all retries fail, the workflow fails

### Resume Capability
Failed or interrupted workflows can be resumed:

```bash
# Resume a workflow after a specific block
kwargify run workflow.py --resume-from <run_id> --resume-after <block_name>
```

When resuming:
1. The system validates the previous run's state
2. Successfully completed blocks are skipped
3. Their outputs are loaded from the log
4. Execution continues from the specified point

Example workflow with resume:
```python
# Create workflow that can be resumed
workflow = Workflow()
workflow.name = "ResumableFlow"

# Add blocks as normal
workflow.add_block(block1)
workflow.add_block(block2)
workflow.add_block(block3)

# Run with resume capability
workflow.run(
    resume_from_run_id="previous_run_id",
    resume_after_block_name="block1"
)
```

This will:
- Skip block1 if it completed successfully in the previous run
- Use block1's logged outputs
- Continue execution from block2

## Documentation

See our comprehensive documentation for detailed information:

- [CLI Usage Guide](docs/cli_usage_guide.md) - Complete guide for using the CLI
- Examples:
  - [Contract Analysis](examples/contract_report_workflow.py)
  - [Simple Workflow](examples/simple_workflow.py)
- [Block Documentation](docs/blocks.md) - Details on available blocks

## Available Built-in Blocks

### ReadFileBlock
Reads content from a file.
```python
reader = ReadFileBlock(
    name="MyReader",
    config={
        "path": "input.txt"  # Required: Path to the file to read
    }
)
# Outputs: {"content": str}  # The file contents
```

### WriteFileBlock
Writes content to a file.
```python
writer = WriteFileBlock(
    name="MyWriter",
    config={
        "path": "output.txt"  # Required: Path where to write
    }
)
# Inputs: {"content": str}  # The content to write
```

### AIProcessorBlock
Processes text using an AI model.
```python
processor = AIProcessorBlock(
    name="MyAIProcessor",
    config={
        "model": "gpt-4o-mini",        # Required: Model name
        "api_key": "your-api-key",     # Required: API key
        "system_prompt": "You are...",  # Optional: System context
        "user_prompt": "Analyze...",    # Optional: User instruction
        "temperature": 0.7              # Optional: Model temperature
    }
)
# Inputs: {"content": str}  # Text to process
# Outputs: {"response": str}  # AI model's response
```

### AIExtractorBlock
Extracts structured data using an AI model.
```python
extractor = AIExtractorBlock(
    name="MyExtractor",
    config={
        "model": "gpt-4o-mini",
        "api_key": "your-api-key",
        "temperature": 0.2
    }
)
# Set extraction fields schema
extractor.inputs["extraction_fields"] = {
    "title": {
        "type": "string",
        "description": "The document title"
    },
    "author": {
        "type": "string",
        "description": "The document author"
    },
    "topics": {
        "type": "array",
        "description": "List of main topics covered"
    }
}
# Inputs: {
#   "content": str,  # Text to analyze
#   "extraction_fields": dict  # Schema for extraction
# }
# Outputs: {"extracted_data": dict}  # Structured data matching schema
```

### DocumentTemplateBlock
Generates documents using templates.
```python
template = DocumentTemplateBlock(name="MyTemplate")
template.inputs["template"] = """
Report
======
Title: {{ title }}
Author: {{ author }}

Topics:
{% for topic in topics %}
- {{ topic }}
{% endfor %}
"""
# Inputs: {
#   "template": str,  # The template string
#   "data": dict     # Data to populate template
# }
# Outputs: {"document": str}  # The rendered document
```

### JsonToStringBlock
Converts JSON data to formatted strings.
```python
formatter = JsonToStringBlock(name="MyFormatter")
# Inputs: {
#   "json_data": dict,  # Data to format
#   "format": str       # Optional: "json", "yaml", "pretty_json"
# }
# Outputs: {"output_string": str}  # Formatted string
```

## Command Line Interface (CLI)

If you encounter any issues:

1. Check the [CLI Usage Guide](docs/cli_usage_guide.md#error-resolution) for common error solutions
2. Review the error message for specific guidance
3. Ensure your workflow follows the [best practices](docs/cli_usage_guide.md#best-practices)
4. Report bugs on our issue tracker

Common issues:
- Workflow file not found: Check the file path and extension
- Invalid workflow structure: Verify get_workflow() function exists
- Registry errors: Check permissions and workflow names
- Runtime errors: Review block configurations and dependencies

For detailed troubleshooting steps, see the [Error Resolution](docs/cli_usage_guide.md#error-resolution) section in our CLI guide.

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

Please follow our coding standards and include appropriate documentation.

## License

[License details]