import tempfile
import os
import litellm
from typing import Dict, Any

from kwargify_core.core.workflow import Workflow
from kwargify_core.blocks.read_file import ReadFileBlock
from kwargify_core.blocks.write_file import WriteFileBlock
from kwargify_core.blocks.ai_processor import AIProcessorBlock
from kwargify_core.blocks.ai_extractor import AIExtractorBlock
from kwargify_core.blocks.document_template import DocumentTemplateBlock
from dotenv import load_dotenv

# Set your OpenAI API Key
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Step 1: Create temporary input file with sample contract data
sample_contract = """
CONSULTING AGREEMENT

This Consulting Agreement (the "Agreement") is made on April 19, 2024, between:

Company XYZ Inc., a corporation with its principal place of business at 123 Business St, 
(hereinafter referred to as the "Company")

and

John Doe, an individual residing at 456 Consultant Ave,
(hereinafter referred to as the "Consultant")

1. SERVICES
The Consultant shall provide technology consulting services to the Company.

2. COMPENSATION
The Company shall pay the Consultant $150 per hour for services rendered.

3. TERM
This Agreement shall commence on May 1, 2024 and continue for 12 months.

4. CONFIDENTIALITY
The Consultant agrees to maintain the confidentiality of all Company information.
"""

# Create input contract file
with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp_in:
    tmp_in.write(sample_contract)
    tmp_in.flush()
    input_path = tmp_in.name

# Create output file path
output_fd, output_path = tempfile.mkstemp(suffix=".txt")  # Changed from .json to .txt
os.close(output_fd)

# Step 2: Create the blocks for the workflow

# Block 1: File Reader for input
read_block = ReadFileBlock(name="ContractReader", config={"path": input_path})

# Block 2: AI Processor for initial analysis
analysis_prompt = """
Analyze the contract provided and give a comprehensive analysis including:
1. Type of agreement
2. Parties involved
3. Key terms and conditions
4. Important dates
5. Financial terms
6. Notable obligations

Format your response as a clear, well-structured analysis that will be processed further.
"""

ai_processor = AIProcessorBlock(
    name="ContractAnalyzer",
    config={
        "model": "gpt-4o-mini",
        "api_key": api_key,
        "system_prompt": "You are a legal contract analyzer. Provide detailed analysis of contracts.",
        "user_prompt": analysis_prompt
    }
)

# Block 3: AI Extractor for structured data
ai_extractor = AIExtractorBlock(
    name="DataExtractor",
    config={
        "model": "gpt-4o-mini",
        "api_key": api_key,
        "temperature": 0.2
    }
)

# Define extraction fields
extraction_fields = {
    "agreement_type": {
        "type": "string",
        "description": "The type of agreement (e.g., Consulting Agreement, Employment Contract)"
    },
    "company_name": {
        "type": "string",
        "description": "Name of the company party to the agreement"
    },
    "consultant_name": {
        "type": "string",
        "description": "Name of the consultant party to the agreement"
    },
    "start_date": {
        "type": "string",
        "description": "Start date of the agreement"
    },
    "duration": {
        "type": "string",
        "description": "Duration or term of the agreement"
    },
    "hourly_rate": {
        "type": "number",
        "description": "Hourly rate for consulting services"
    },
    "services_description": {
        "type": "string",
        "description": "Description of services to be provided"
    },
    "key_obligations": {
        "type": "array",
        "description": "List of key obligations and responsibilities"
    }
}

# Block 4: Document Template for formatting the report
report_template = """
Contract Analysis Report
=======================

AGREEMENT DETAILS
----------------
Agreement Type: {{ agreement_type | default('N/A') }}
Date of Agreement: {{ start_date | default('N/A') }}
Duration: {{ duration | default('N/A') }}

PARTIES
-------
Company: {{ company_name | default('N/A') }}
Consultant: {{ consultant_name | default('N/A') }}

FINANCIAL TERMS
--------------
Hourly Rate: ${{ hourly_rate | default('N/A') }}

SERVICES
--------
{{ services_description | default('N/A') }}

KEY OBLIGATIONS
--------------
{% if key_obligations %}
{% for obligation in key_obligations %}
- {{ obligation }}
{% endfor %}
{% else %}
No specific obligations listed.
{% endif %}
"""

doc_template_block = DocumentTemplateBlock(name="TemplateFormatter")

# Block 5: Write output to file
write_block = WriteFileBlock(name="ReportGenerator", config={"path": output_path})

# Define sequential dependencies
ai_processor.add_dependency(read_block)
ai_extractor.add_dependency(ai_processor)
doc_template_block.add_dependency(ai_extractor)
write_block.add_dependency(doc_template_block)

# Wire the block inputs
ai_processor.input_map = {"content": (read_block, "content")}
ai_extractor.input_map = {"content": (ai_processor, "response")}
ai_extractor.inputs["extraction_fields"] = extraction_fields
doc_template_block.input_map = {"data": (ai_extractor, "extracted_data")}
doc_template_block.inputs["template"] = report_template
write_block.input_map = {"content": (doc_template_block, "document")}

# Step 3: Create and run the workflow
wf = Workflow()
wf.add_block(read_block)
wf.add_block(ai_processor)
wf.add_block(ai_extractor)
wf.add_block(doc_template_block)
wf.add_block(write_block)

# Generate and display workflow diagram
mermaid_output = wf.to_mermaid()
print("\nWorkflow Diagram:")
print(mermaid_output)

# Run the workflow
wf.run()

# Step 4: Read and output the analysis report
print("\nGenerated Contract Report:")
with open(output_path, "r") as f:
    output_content = f.read()
print(output_content)

# Cleanup temporary files
os.unlink(input_path)
os.unlink(output_path)