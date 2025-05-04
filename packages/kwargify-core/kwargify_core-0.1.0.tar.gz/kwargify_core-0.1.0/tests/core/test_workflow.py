import tempfile
import os
import uuid
import litellm
import time
from datetime import datetime
from unittest.mock import Mock, patch

from kwargify_core.core.workflow import Workflow
from kwargify_core.blocks.read_file import ReadFileBlock
from kwargify_core.blocks.write_file import WriteFileBlock
from kwargify_core.blocks.ai_processor import AIProcessorBlock
from kwargify_core.logging.sqlite_logger import SQLiteLogger


def test_workflow_read_ai_write(monkeypatch):
    # --- Setup: mock LLM response ---
    def mock_completion(*args, **kwargs):
        class MockChoice:
            def __init__(self):
                self.message = {"content": "This is the summary."}

        class MockResponse:
            def __init__(self):
                self.choices = [MockChoice()]
        return MockResponse()

    monkeypatch.setattr(litellm, "completion", mock_completion)

    # --- Setup: temp input and output files ---
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp_in:
        tmp_in.write("Python is a popular language for AI and automation.")
        tmp_in.flush()
        input_path = tmp_in.name

    output_fd, output_path = tempfile.mkstemp(suffix=".txt")
    os.close(output_fd)  # Close so WriteFileBlock can overwrite

    # --- Setup blocks ---
    read_block = ReadFileBlock(config={"path": input_path})
    ai_block = AIProcessorBlock(config={"model": "mock-model"})
    write_block = WriteFileBlock(config={"path": output_path})

    ai_block.add_dependency(read_block)
    write_block.add_dependency(ai_block)

    # Manually wire ai_block.output["response"] → write_block.input["content"]
    write_block.input_map = {"content": (ai_block, "response")}

    # --- Build and run workflow ---
    wf = Workflow()
    wf.logger = SQLiteLogger(":memory:")
    wf.add_block(read_block)
    wf.add_block(ai_block)
    wf.add_block(write_block)
    wf.run()

    # --- Assert output content written matches mock LLM response ---
    with open(output_path, "r") as f:
        content = f.read()

    assert content == "This is the summary."

def test_workflow_to_mermaid():
    """Test the to_mermaid method generates the correct structure."""
    # --- Setup blocks ---
    read_block = ReadFileBlock(name="MyReadFile")
    ai_block = AIProcessorBlock(name="MyAIProcessor")
    write_block = WriteFileBlock(name="MyWriteFile")

    # --- Setup dependencies and input map ---
    ai_block.add_dependency(read_block)
    write_block.add_dependency(ai_block)
    # ai_block.output["response"] -> write_block.input["content"]
    write_block.input_map = {"content": (ai_block, "response")}

    # --- Build workflow ---
    wf = Workflow()
    wf.logger = SQLiteLogger(":memory:")
    wf.add_block(read_block)
    wf.add_block(ai_block)
    wf.add_block(write_block)

    # --- Generate Mermaid output ---
    mermaid_output = wf.to_mermaid()
    print(f"\nGenerated Mermaid:\n{mermaid_output}")  # Debug output

    # --- Assertions ---
    # Basic structure
    assert "graph TD;" in mermaid_output

    # Node definitions (check for names)
    assert '["MyReadFile"]' in mermaid_output
    assert '["MyAIProcessor"]' in mermaid_output
    assert '["MyWriteFile"]' in mermaid_output

    # Edges
    # Check for the labeled edge from input_map
    assert '-- "response -> content" -->' in mermaid_output

    # Count unique edges by looking at each line
    edge_lines = [line.strip() for line in mermaid_output.split('\n') if '-->' in line]
    assert len(edge_lines) == 2, f"Expected 2 edges, found {len(edge_lines)}:\n{edge_lines}"

    # Check escaping (if a block name had quotes)
    quote_block = ReadFileBlock(name='Block With "Quotes"')
    wf_quote = Workflow()
    wf_quote.logger = SQLiteLogger(":memory:")
    wf_quote.add_block(quote_block)
    mermaid_quote = wf_quote.to_mermaid()
    assert '["Block With #quot;Quotes#quot;"]' in mermaid_quote


def test_workflow_with_logging(monkeypatch):
    """Test workflow execution with SQLite logging."""
    # Mock LLM response
    def mock_completion(*args, **kwargs):
        class MockChoice:
            def __init__(self):
                self.message = {"content": "This is the summary."}
        class MockResponse:
            def __init__(self):
                self.choices = [MockChoice()]
        return MockResponse()

    monkeypatch.setattr(litellm, "completion", mock_completion)

    # Setup temporary files
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp_in:
        tmp_in.write("Test input content")
        tmp_in.flush()
        input_path = tmp_in.name

    output_fd, output_path = tempfile.mkstemp(suffix=".txt")
    os.close(output_fd)

    try:
        # Setup workflow with logging
        wf = Workflow()
        wf.logger = SQLiteLogger(":memory:")
        wf.name = "TestWorkflow"

        # Create and configure blocks
        read_block = ReadFileBlock(name="ReadInput", config={"path": input_path})
        ai_block = AIProcessorBlock(name="ProcessContent", config={"model": "mock-model"})
        write_block = WriteFileBlock(name="WriteOutput", config={"path": output_path})

        ai_block.add_dependency(read_block)
        write_block.add_dependency(ai_block)
        write_block.input_map = {"content": (ai_block, "response")}

        wf.add_block(read_block)
        wf.add_block(ai_block)
        wf.add_block(write_block)

        # Run workflow
        wf.run()

        # Verify run summary
        cursor = wf.logger.conn.cursor()
        cursor.execute("SELECT workflow_name, status FROM run_summary WHERE run_id = ?", (wf.run_id,))
        workflow_name, status = cursor.fetchone()
        assert workflow_name == "TestWorkflow"
        assert status == "COMPLETED"

        # Verify block executions
        cursor.execute("""
            SELECT block_name, status
            FROM run_details
            WHERE run_id = ?
            ORDER BY start_time
        """, (wf.run_id,))
        block_results = cursor.fetchall()
        
        assert len(block_results) == 3
        assert block_results[0] == ("ReadInput", "COMPLETED")
        assert block_results[1] == ("ProcessContent", "COMPLETED")
        assert block_results[2] == ("WriteOutput", "COMPLETED")

    finally:
        # Cleanup
        os.unlink(input_path)
        os.unlink(output_path)


def test_workflow_resume(monkeypatch):
    """Test workflow resume functionality with logging."""
    # Mock LLM response
    def mock_completion(*args, **kwargs):
        class MockChoice:
            def __init__(self):
                self.message = {"content": "Processed content"}
        class MockResponse:
            def __init__(self):
                self.choices = [MockChoice()]
        return MockResponse()

    monkeypatch.setattr(litellm, "completion", mock_completion)

    # Setup workflow with logging
    logger = SQLiteLogger(":memory:")
    
    # Create first workflow run that will be "interrupted" after AI processing
    wf1 = Workflow()
    wf1.logger = logger
    wf1.name = "ResumeTestWorkflow"
    
    # Setup blocks for first run
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tmp_in:
        tmp_in.write("Test input content")
        tmp_in.flush()
        input_path = tmp_in.name

    output_fd, output_path = tempfile.mkstemp(suffix=".txt")
    os.close(output_fd)

    try:
        read_block = ReadFileBlock(name="ReadInput", config={"path": input_path})
        ai_block = AIProcessorBlock(name="ProcessContent", config={"model": "mock-model"})
        write_block = WriteFileBlock(name="WriteOutput", config={"path": output_path})

        ai_block.add_dependency(read_block)
        write_block.add_dependency(ai_block)
        write_block.input_map = {"content": (ai_block, "response")}

        wf1.add_block(read_block)
        wf1.add_block(ai_block)
        wf1.add_block(write_block)

        # Run first workflow but simulate interruption after AI block
        class SimulatedInterruption(Exception):
            pass

        def mock_write_file(*args, **kwargs):
            raise SimulatedInterruption("Simulated interruption")

        original_run = WriteFileBlock.run
        WriteFileBlock.run = mock_write_file

        try:
            wf1.run()
        except SimulatedInterruption:
            # Expected interruption
            pass
        finally:
            WriteFileBlock.run = original_run

        # Store the run_id for resume
        interrupted_run_id = wf1.run_id

        # Verify the state of the interrupted run
        cursor = logger.conn.cursor()
        cursor.execute("SELECT status FROM run_summary WHERE run_id = ?", (interrupted_run_id,))
        assert cursor.fetchone()[0] == "FAILED"

        # Create new workflow to resume from the interrupted one
        wf2 = Workflow()
        wf2.logger = logger
        wf2.name = "ResumeTestWorkflow"
        
        # Add same blocks
        read_block2 = ReadFileBlock(name="ReadInput", config={"path": input_path})
        ai_block2 = AIProcessorBlock(name="ProcessContent", config={"model": "mock-model"})
        write_block2 = WriteFileBlock(name="WriteOutput", config={"path": output_path})

        ai_block2.add_dependency(read_block2)
        write_block2.add_dependency(ai_block2)
        write_block2.input_map = {"content": (ai_block2, "response")}

        wf2.add_block(read_block2)
        wf2.add_block(ai_block2)
        wf2.add_block(write_block2)

        # Resume the workflow
        wf2.run(resume_from_run_id=interrupted_run_id, resume_after_block_name="ProcessContent")

        # Verify the resumed run
        cursor.execute("SELECT status FROM run_summary WHERE run_id = ?", (wf2.run_id,))
        assert cursor.fetchone()[0] == "COMPLETED"

        # Verify block statuses in resumed run
        cursor.execute("""
            SELECT block_name, status
            FROM run_details
            WHERE run_id = ?
            ORDER BY start_time
        """, (wf2.run_id,))
        block_results = cursor.fetchall()

        assert len(block_results) == 3
        # Verify all blocks up through ProcessContent are skipped
        assert len(block_results) == 3, "Expected exactly 3 blocks"
        assert block_results[0] == ("ReadInput", "SKIPPED"), "ReadInput should be skipped"
        assert block_results[1] == ("ProcessContent", "SKIPPED"), "ProcessContent should be skipped"
        assert block_results[2] == ("WriteOutput", "COMPLETED")

        # Verify the final output was written
        with open(output_path, 'r') as f:
            content = f.read()
        assert content == "Processed content"

    finally:
        # Cleanup
        os.unlink(input_path)
        os.unlink(output_path)


def test_workflow_failed_block(monkeypatch):
    """Test workflow execution with a failed block and proper logging."""
    # Setup workflow with logging
    wf = Workflow()
    wf.logger = SQLiteLogger(":memory:")
    wf.name = "FailureTestWorkflow"

    # Create a block that will fail
    read_block = ReadFileBlock(name="ReadInput", config={"path": "nonexistent_file.txt"})
    wf.add_block(read_block)

    # Run workflow (should fail)
    try:
        wf.run()
    except FileNotFoundError:
        pass  # Expected error

    # Verify run summary shows failure
    cursor = wf.logger.conn.cursor()
    cursor.execute("SELECT status FROM run_summary WHERE run_id = ?", (wf.run_id,))
    assert cursor.fetchone()[0] == "FAILED"

    # Verify block execution details
    cursor.execute("""
        SELECT status, error_message
        FROM run_details
        WHERE run_id = ? AND block_name = 'ReadInput'
    """, (wf.run_id,))
    status, error_message = cursor.fetchone()
    
    assert status == "FAILED"
    assert "File not found:" in error_message

def test_retry_functionality():
    """Test the retry functionality in workflow execution."""
    # Create a test block that fails a specific number of times
    class RetryTestBlock:
        def __init__(self, name="RetryBlock", fail_count=2, max_retries=None):
            self.name = name
            self.fail_count = fail_count
            self.attempt_count = 0
            self.has_run = False
            self.outputs = {}
            self.dependencies = []
            self.inputs = {}
            self.max_retries = max_retries

        def add_dependency(self, block):
            self.dependencies.append(block)

        def collect_inputs_from_dependencies(self):
            pass  # No-op for test

        def run(self):
            self.attempt_count += 1
            if self.attempt_count <= self.fail_count:
                raise ValueError(f"Simulated failure on attempt {self.attempt_count}")
            self.has_run = True

    # Use a temporary database for testing
    # Test Case 1: Block succeeds on first try (0 retries)
    wf1 = Workflow(default_max_retries=3)
    wf1.logger = SQLiteLogger(":memory:")
    block1 = RetryTestBlock(fail_count=0)
    wf1.add_block(block1)
    wf1.run()
    
    assert block1.attempt_count == 1
    cursor = wf1.logger.conn.cursor()
    cursor.execute("SELECT retries_attempted FROM run_details WHERE run_id = ?", (wf1.run_id,))
    assert cursor.fetchone()[0] == 0

    # Test Case 2: Block fails once, succeeds on retry
    wf2 = Workflow(default_max_retries=3)
    wf2.logger = SQLiteLogger(":memory:")
    block2 = RetryTestBlock(fail_count=1)
    wf2.add_block(block2)
    wf2.run()
    
    assert block2.attempt_count == 2
    cursor = wf2.logger.conn.cursor()
    cursor.execute("SELECT retries_attempted FROM run_details WHERE run_id = ?", (wf2.run_id,))
    assert cursor.fetchone()[0] == 1

    # Test Case 3: Block fails twice, succeeds on third try
    wf3 = Workflow(default_max_retries=3)
    wf3.logger = SQLiteLogger(":memory:")
    block3 = RetryTestBlock(fail_count=2)
    wf3.add_block(block3)
    wf3.run()
    
    assert block3.attempt_count == 3
    cursor = wf3.logger.conn.cursor()
    cursor.execute("SELECT retries_attempted FROM run_details WHERE run_id = ?", (wf3.run_id,))
    assert cursor.fetchone()[0] == 2

    # Test Case 4: Block fails more times than max_retries
    wf4 = Workflow(default_max_retries=2)
    wf4.logger = SQLiteLogger(":memory:")
    block4 = RetryTestBlock(fail_count=3)
    wf4.add_block(block4)
    
    try:
        wf4.run()
        assert False, "Expected workflow to fail"
    except ValueError as e:
        assert "Simulated failure on attempt 3" in str(e)
    
    cursor = wf4.logger.conn.cursor()
    cursor.execute("SELECT status, retries_attempted FROM run_details WHERE run_id = ?", (wf4.run_id,))
    status, retries = cursor.fetchone()
    assert status == "FAILED"
    assert retries == 2

    # Test Case 5: Block-specific max_retries overrides workflow default
    wf5 = Workflow(default_max_retries=1)
    wf5.logger = SQLiteLogger(":memory:")
    block5 = RetryTestBlock(fail_count=2, max_retries=3)  # Override workflow default
    wf5.add_block(block5)
    wf5.run()
    
    assert block5.attempt_count == 3
    cursor = wf5.logger.conn.cursor()
    cursor.execute("SELECT retries_attempted FROM run_details WHERE run_id = ?", (wf5.run_id,))
    assert cursor.fetchone()[0] == 2
