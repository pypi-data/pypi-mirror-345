"""Tests for the workflow loader module."""

import pytest
from pathlib import Path
import tempfile
import os

from kwargify_core.loader import load_workflow_from_py, WorkflowLoadError
from kwargify_core.core.workflow import Workflow


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def valid_workflow_file(temp_dir):
    """Create a valid workflow file for testing."""
    content = '''
from kwargify_core.core.workflow import Workflow
from kwargify_core.core.block import Block

class SimpleBlock(Block):
    def run(self) -> None:
        self.outputs = {"result": "success"}

def get_workflow():
    workflow = Workflow()
    workflow.name = "test_workflow"
    block = SimpleBlock(name="test_block")
    workflow.add_block(block)
    return workflow
'''
    file_path = temp_dir / "valid_workflow.py"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def invalid_workflow_file(temp_dir):
    """Create an invalid workflow file (missing get_workflow function)."""
    content = '''
from kwargify_core.core.workflow import Workflow

# No get_workflow function defined
'''
    file_path = temp_dir / "invalid_workflow.py"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def wrong_return_type_file(temp_dir):
    """Create a workflow file that returns wrong type."""
    content = '''
def get_workflow():
    return "not a workflow object"
'''
    file_path = temp_dir / "wrong_return_type.py"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


def test_load_valid_workflow(valid_workflow_file):
    """Test loading a valid workflow file."""
    workflow = load_workflow_from_py(str(valid_workflow_file))
    assert isinstance(workflow, Workflow)
    assert workflow.name == "test_workflow"
    assert len(workflow.blocks) == 1
    assert workflow.blocks[0].name == "test_block"


def test_load_nonexistent_file():
    """Test loading a non-existent file."""
    with pytest.raises(WorkflowLoadError, match="File not found"):
        load_workflow_from_py("nonexistent.py")


def test_load_invalid_workflow(invalid_workflow_file):
    """Test loading a file without get_workflow function."""
    with pytest.raises(WorkflowLoadError, match="must contain a function named 'get_workflow'"):
        load_workflow_from_py(str(invalid_workflow_file))


def test_load_wrong_return_type(wrong_return_type_file):
    """Test loading a file where get_workflow returns wrong type."""
    with pytest.raises(WorkflowLoadError, match="must return a Workflow object"):
        load_workflow_from_py(str(wrong_return_type_file))


def test_load_non_python_file(temp_dir):
    """Test loading a non-Python file."""
    file_path = temp_dir / "not_python.txt"
    file_path.touch()
    with pytest.raises(WorkflowLoadError, match="must be a Python file"):
        load_workflow_from_py(str(file_path))