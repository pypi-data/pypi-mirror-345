"""Module for loading workflow definitions from Python files."""

import importlib.util
from pathlib import Path
from typing import Any

from kwargify_core.core.workflow import Workflow


class WorkflowLoadError(Exception):
    """Exception raised when workflow loading fails."""
    pass


def load_workflow_from_py(file_path: str) -> Workflow:
    """Load a workflow from a Python file.

    The Python file must contain a function named 'get_workflow' that returns
    an instance of kwargify_core.core.Workflow.

    Args:
        file_path (str): Path to the Python file containing the workflow definition

    Returns:
        Workflow: The loaded workflow object

    Raises:
        WorkflowLoadError: If the file cannot be loaded or doesn't contain a valid workflow
        ImportError: If there are issues importing the module
        AttributeError: If get_workflow() function is not found
    """
    try:
        # Convert to Path object for robust path handling
        path = Path(file_path).resolve()
        if not path.exists():
            raise WorkflowLoadError(f"File not found: {file_path}")
        if not path.suffix == '.py':
            raise WorkflowLoadError(f"File must be a Python file (.py): {file_path}")

        # Create a unique module name from the file path
        module_name = f"workflow_module_{path.stem}"

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            raise WorkflowLoadError(f"Could not load module spec from {file_path}")
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for get_workflow function
        if not hasattr(module, 'get_workflow'):
            raise WorkflowLoadError(
                f"Module {file_path} must contain a function named 'get_workflow'"
            )

        # Get the workflow object
        workflow = module.get_workflow()

        # Validate the returned object
        if not isinstance(workflow, Workflow):
            raise WorkflowLoadError(
                f"get_workflow() must return a Workflow object, got {type(workflow)}"
            )

        return workflow

    except Exception as e:
        if isinstance(e, WorkflowLoadError):
            raise
        raise WorkflowLoadError(f"Failed to load workflow from {file_path}: {str(e)}")