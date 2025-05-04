"""Contract Analysis and Report Generation Workflow."""

import os
from typing import Dict, Any
from pathlib import Path

from kwargify_core.core.workflow import Workflow
from kwargify_core.blocks.read_file import ReadFileBlock
from kwargify_core.blocks.write_file import WriteFileBlock
from kwargify_core.blocks.ai_processor import AIProcessorBlock
from kwargify_core.blocks.ai_extractor import AIExtractorBlock
from kwargify_core.blocks.document_template import DocumentTemplateBlock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Define extraction fields for contract analysis
EXTRACTION_FIELDS = {
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

# Define report template
REPORT_TEMPLATE = """
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

# Define analysis prompt
ANALYSIS_PROMPT = """
Analyze the contract provided and give a comprehensive analysis including:
1. Type of agreement
2. Parties involved
3. Key terms and conditions
4. Important dates
5. Financial terms
6. Notable obligations

Format your response as a clear, well-structured analysis that will be processed further.
"""


def get_workflow() -> Workflow:
    """Create and configure the contract analysis workflow.
    
    Returns:
        Workflow: Configured workflow ready to execute
    """
    # Create blocks
    read_block = ReadFileBlock(
        name="ContractReader", 
        config={"path": os.getenv('CONTRACT_INPUT_PATH', 'contract.txt')}
    )

    ai_processor = AIProcessorBlock(
        name="ContractAnalyzer",
        config={
            "model": "gpt-4o-mini",
            "api_key": api_key,
            "system_prompt": "You are a legal contract analyzer. Provide detailed analysis of contracts.",
            "user_prompt": ANALYSIS_PROMPT
        }
    )

    ai_extractor = AIExtractorBlock(
        name="DataExtractor",
        config={
            "model": "gpt-4o-mini",
            "api_key": api_key,
            "temperature": 0.2
        }
    )

    doc_template_block = DocumentTemplateBlock(name="TemplateFormatter")

    write_block = WriteFileBlock(
        name="ReportGenerator", 
        config={"path": os.getenv('CONTRACT_OUTPUT_PATH', 'report.txt')}
    )

    # Define sequential dependencies
    ai_processor.add_dependency(read_block)
    ai_extractor.add_dependency(ai_processor)
    doc_template_block.add_dependency(ai_extractor)
    write_block.add_dependency(doc_template_block)

    # Wire the block inputs
    ai_processor.input_map = {"content": (read_block, "content")}
    ai_extractor.input_map = {"content": (ai_processor, "response")}
    ai_extractor.inputs["extraction_fields"] = EXTRACTION_FIELDS
    doc_template_block.input_map = {"data": (ai_extractor, "extracted_data")}
    doc_template_block.inputs["template"] = REPORT_TEMPLATE
    write_block.input_map = {"content": (doc_template_block, "document")}

    # Create workflow and add blocks
    workflow = Workflow()
    workflow.name = "ContractAnalysisWorkflow"
    workflow.add_block(read_block)
    workflow.add_block(ai_processor)
    workflow.add_block(ai_extractor)
    workflow.add_block(doc_template_block)
    workflow.add_block(write_block)

    return workflow


if __name__ == "__main__":
    # This section is for local testing
    import tempfile

    # Create a sample contract file
    sample_contract = """
    CONSULTING AGREEMENT
    
    This Consulting Agreement (the "Agreement") is made on April 19, 2024, between:
    
    Company XYZ Inc., a corporation with its principal place of business at 123 Business St, 
    (hereinafter referred to as the "Company")
    
    and
    
    John Doe, an individual residing at 456 Consultant Ave,
    (hereinafter referred to as the "Consultant")
    """

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp_in:
        tmp_in.write(sample_contract)
        tmp_in.flush()
        os.environ['CONTRACT_INPUT_PATH'] = tmp_in.name

    # Set output path
    output_fd, output_path = tempfile.mkstemp(suffix=".txt")
    os.close(output_fd)
    os.environ['CONTRACT_OUTPUT_PATH'] = output_path

    # Run the workflow
    workflow = get_workflow()
    workflow.run()

    # Display results
    print("\nGenerated Contract Report:")
    with open(output_path, "r") as f:
        print(f.read())

    # Cleanup
    os.unlink(os.environ['CONTRACT_INPUT_PATH'])
    os.unlink(output_path)