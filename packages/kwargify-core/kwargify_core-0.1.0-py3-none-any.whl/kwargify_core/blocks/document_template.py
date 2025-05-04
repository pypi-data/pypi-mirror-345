from typing import Dict, Any
import jinja2
from kwargify_core.core.block import Block


class DocumentTemplateBlock(Block):
    """
    Block to generate formatted documents using Jinja2 templates.

    This block takes a Jinja2 template string and a dictionary of data,
    and produces a formatted document by rendering the template with the provided data.

    Config:
        No specific configuration needed. Uses default Jinja2 Environment settings with StrictUndefined
        to catch missing variable errors.

    Inputs:
        - template (str): The Jinja2 template string. Can include variables, filters, loops, conditionals, etc.
        - data (Dict[str, Any]): Dictionary containing the data to be rendered into the template.
          The keys in this dictionary should match the variable names used in the template.

    Outputs:
        - document (str): The rendered document string after applying the template with the provided data.

    Example:
        template = '''
        Report for {{ name }}
        ===================
        Age: {{ age }}
        Skills:
        {% for skill in skills %}
        - {{ skill }}
        {% endfor %}
        '''
        
        data = {
            'name': 'John Doe',
            'age': 30,
            'skills': ['Python', 'JavaScript', 'SQL']
        }
    """

    def run(self) -> None:
        """
        Execute the document template block to generate a formatted document.

        Raises:
            ValueError: If template or data inputs are missing, or if data is not a dictionary.
            RuntimeError: If template rendering fails due to syntax errors or undefined variables.
        """
        # Get required inputs
        template_string = self.inputs.get("template")
        render_data = self.inputs.get("data")

        # Validate inputs
        if not template_string:
            raise ValueError("Missing 'template' input for DocumentTemplateBlock")
        
        # Create Jinja2 environment with strict undefined checking
        env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,     # Remove first newline after a block
            lstrip_blocks=True,   # Strip tabs and spaces from the start of a line to the start of a block
        )

        try:
            # First, try to parse the template to catch syntax errors
            try:
                jinja_template = env.from_string(template_string)
            except jinja2.exceptions.TemplateSyntaxError as e:
                raise RuntimeError(f"Template syntax error: {str(e)}")

            # Now check data input
            if not render_data:
                raise ValueError("Missing 'data' input for DocumentTemplateBlock")
            if not isinstance(render_data, dict):
                raise ValueError("'data' input must be a dictionary for DocumentTemplateBlock")

            # Try to render the template
            try:
                rendered_document = jinja_template.render(**render_data)
                self.outputs["document"] = rendered_document
            except jinja2.exceptions.UndefinedError as e:
                raise RuntimeError(f"Undefined variable in template: {str(e)}")
            except Exception as e:
                raise RuntimeError(f"Template rendering failed: {str(e)}")

        except ValueError:
            raise
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Unexpected error during template processing: {str(e)}")