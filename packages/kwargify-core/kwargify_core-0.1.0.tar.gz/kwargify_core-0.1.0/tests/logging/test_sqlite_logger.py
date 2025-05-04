"""Unit tests for SQLiteLogger class."""

import pytest
import json
from datetime import datetime
from kwargify_core.logging.sqlite_logger import SQLiteLogger


@pytest.fixture
def logger():
    """Create a SQLiteLogger instance with in-memory database."""
    logger = SQLiteLogger(":memory:")
    yield logger
    logger.conn.close()


@pytest.fixture
def sample_workflow_run(logger):
    """Create a sample workflow run with multiple blocks."""
    run_id = "test-workflow-1"
    workflow_name = "TestWorkflow"
    
    # Start workflow
    logger.log_run_start(run_id, workflow_name)
    
    # Execute blocks
    block1_id = "block-1"
    block2_id = "block-2"
    
    logger.log_block_start(block1_id, run_id, "ProcessData", {"input": "data1"})
    logger.log_block_end(block1_id, "COMPLETED", {"output": "result1"})
    
    logger.log_block_start(block2_id, run_id, "SaveResults", {"input": "result1"})
    logger.log_block_end(block2_id, "COMPLETED", {"status": "saved"})
    
    logger.log_run_end(run_id, "COMPLETED")
    
    return run_id


def test_init_creates_tables(logger):
    """Test that tables are created during initialization."""
    cursor = logger.conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    assert "run_summary" in tables
    assert "run_details" in tables
    assert "run_logs" in tables


def test_list_runs_default_limit(logger, sample_workflow_run):
    """Test listing workflow runs with default limit."""
    # Create additional runs
    for i in range(3):
        run_id = f"test-run-{i}"
        logger.log_run_start(run_id, "TestWorkflow")
        logger.log_run_end(run_id, "COMPLETED")
    
    runs = logger.list_runs()
    
    assert len(runs) <= 50  # Default limit
    assert len(runs) == 4  # Sample run + 3 additional runs
    
    # Verify run structure
    first_run = runs[0]
    assert "run_id" in first_run
    assert "workflow_name" in first_run
    assert "start_time" in first_run
    assert "end_time" in first_run
    assert "status" in first_run


def test_list_runs_with_custom_limit(logger):
    """Test listing workflow runs with custom limit."""
    # Create 5 runs
    for i in range(5):
        run_id = f"test-run-{i}"
        logger.log_run_start(run_id, "TestWorkflow")
        logger.log_run_end(run_id, "COMPLETED")
    
    runs = logger.list_runs(limit=3)
    
    assert len(runs) == 3
    # Verify runs are ordered by start_time desc
    assert runs[0]["run_id"] == "test-run-4"
    assert runs[2]["run_id"] == "test-run-2"


def test_get_run_details_existing_run(logger, sample_workflow_run):
    """Test getting details for an existing workflow run."""
    details = logger.get_run_details(sample_workflow_run)
    
    assert details is not None
    assert "run_id" in details
    assert "workflow_name" in details
    assert "start_time" in details
    assert "end_time" in details
    assert "status" in details
    assert "blocks" in details
    
    blocks = details["blocks"]
    assert len(blocks) == 2
    
    first_block = blocks[0]
    assert first_block["block_name"] == "ProcessData"
    assert first_block["status"] == "COMPLETED"
    assert first_block["inputs"] == {"input": "data1"}
    assert first_block["outputs"] == {"output": "result1"}


def test_get_run_details_nonexistent_run(logger):
    """Test getting details for a non-existent workflow run."""
    details = logger.get_run_details("nonexistent-run")
    assert details is None


def test_list_runs_empty_database(logger):
    """Test listing runs when database is empty."""
    runs = logger.list_runs()
    assert len(runs) == 0


def test_get_run_details_with_failed_block(logger):
    """Test getting run details for a workflow with a failed block."""
    run_id = "test-failed-run"
    logger.log_run_start(run_id, "TestWorkflow")
    
    block_id = "failed-block"
    error_msg = "Test error occurred"
    
    logger.log_block_start(block_id, run_id, "FailingBlock", {"input": "data"})
    logger.log_block_end(block_id, "FAILED", None, error_msg)
    logger.log_run_end(run_id, "FAILED")
    
    details = logger.get_run_details(run_id)
    assert details["status"] == "FAILED"
    
    failed_block = details["blocks"][0]
    assert failed_block["status"] == "FAILED"
    assert failed_block["error_message"] == error_msg


def test_log_run_start(logger):
    """Test logging the start of a workflow run."""
    run_id = "test-run-1"
    workflow_name = "TestWorkflow"
    
    logger.log_run_start(run_id, workflow_name)
    
    cursor = logger.conn.cursor()
    cursor.execute("SELECT run_id, workflow_name, status FROM run_summary")
    result = cursor.fetchone()
    
    assert result[0] == run_id
    assert result[1] == workflow_name
    assert result[2] == "STARTED"


def test_log_run_start_with_resume(logger):
    """Test logging the start of a resumed workflow run."""
    run_id = "test-run-2"
    workflow_name = "TestWorkflow"
    resumed_from = "test-run-1"
    
    logger.log_run_start(run_id, workflow_name, resumed_from)
    
    cursor = logger.conn.cursor()
    cursor.execute("SELECT resumed_from_run_id FROM run_summary WHERE run_id = ?", (run_id,))
    result = cursor.fetchone()
    
    assert result[0] == resumed_from


def test_log_run_end(logger):
    """Test logging the end of a workflow run."""
    run_id = "test-run-1"
    workflow_name = "TestWorkflow"
    
    logger.log_run_start(run_id, workflow_name)
    logger.log_run_end(run_id, "COMPLETED")
    
    cursor = logger.conn.cursor()
    cursor.execute("SELECT status, end_time FROM run_summary WHERE run_id = ?", (run_id,))
    status, end_time = cursor.fetchone()
    
    assert status == "COMPLETED"
    assert end_time is not None


def test_log_block_start(logger):
    """Test logging the start of a block execution."""
    run_id = "test-run-1"
    block_execution_id = "block-exec-1"
    block_name = "TestBlock"
    inputs = {"param1": "value1", "param2": 42}
    
    logger.log_run_start(run_id, "TestWorkflow")
    logger.log_block_start(block_execution_id, run_id, block_name, inputs)
    
    cursor = logger.conn.cursor()
    cursor.execute("SELECT status, inputs FROM run_details WHERE block_execution_id = ?", 
                  (block_execution_id,))
    status, inputs_json = cursor.fetchone()
    
    assert status == "STARTED"
    assert json.loads(inputs_json) == inputs


def test_log_block_end(logger):
    """Test logging the end of a block execution."""
    run_id = "test-run-1"
    block_execution_id = "block-exec-1"
    block_name = "TestBlock"
    outputs = {"result": "success", "value": 42}
    
    logger.log_run_start(run_id, "TestWorkflow")
    logger.log_block_start(block_execution_id, run_id, block_name, {})
    logger.log_block_end(block_execution_id, "COMPLETED", outputs)
    
    cursor = logger.conn.cursor()
    cursor.execute("""
        SELECT status, outputs, error_message 
        FROM run_details 
        WHERE block_execution_id = ?
    """, (block_execution_id,))
    status, outputs_json, error_message = cursor.fetchone()
    
    assert status == "COMPLETED"
    assert json.loads(outputs_json) == outputs
    assert error_message is None


def test_log_block_end_with_error(logger):
    """Test logging a failed block execution."""
    run_id = "test-run-1"
    block_execution_id = "block-exec-1"
    block_name = "TestBlock"
    error_msg = "Test error message"
    
    logger.log_run_start(run_id, "TestWorkflow")
    logger.log_block_start(block_execution_id, run_id, block_name, {})
    logger.log_block_end(block_execution_id, "FAILED", None, error_msg)
    
    cursor = logger.conn.cursor()
    cursor.execute("""
        SELECT status, error_message 
        FROM run_details 
        WHERE block_execution_id = ?
    """, (block_execution_id,))
    status, error_message = cursor.fetchone()
    
    assert status == "FAILED"
    assert error_message == error_msg


def test_log_block_skipped(logger):
    """Test logging a skipped block execution."""
    run_id = "test-run-1"
    block_execution_id = "block-exec-1"
    block_name = "TestBlock"
    outputs = {"cached_result": "value"}
    
    logger.log_run_start(run_id, "TestWorkflow")
    logger.log_block_skipped(block_execution_id, run_id, block_name, outputs)
    
    cursor = logger.conn.cursor()
    cursor.execute("""
        SELECT status, outputs 
        FROM run_details 
        WHERE block_execution_id = ?
    """, (block_execution_id,))
    status, outputs_json = cursor.fetchone()
    
    assert status == "SKIPPED"
    assert json.loads(outputs_json) == outputs


def test_log_message(logger):
    """Test logging messages during block execution."""
    run_id = "test-run-1"
    block_execution_id = "block-exec-1"
    message = "Test log message"
    level = "INFO"
    
    logger.log_run_start(run_id, "TestWorkflow")
    logger.log_block_start(block_execution_id, run_id, "TestBlock", {})
    logger.log_message(block_execution_id, run_id, level, message)
    
    cursor = logger.conn.cursor()
    cursor.execute("""
        SELECT level, message 
        FROM run_logs 
        WHERE block_execution_id = ?
    """, (block_execution_id,))
    result_level, result_message = cursor.fetchone()
    
    assert result_level == level
    assert result_message == message


def test_get_run_outputs(logger):
    """Test retrieving outputs from completed blocks."""
    run_id = "test-run-1"
    block1_id = "block-exec-1"
    block2_id = "block-exec-2"
    outputs1 = {"result": "value1"}
    outputs2 = {"result": "value2"}
    
    # Set up test data
    logger.log_run_start(run_id, "TestWorkflow")
    
    # Block 1 - completed
    logger.log_block_start(block1_id, run_id, "Block1", {})
    logger.log_block_end(block1_id, "COMPLETED", outputs1)
    
    # Block 2 - completed
    logger.log_block_start(block2_id, run_id, "Block2", {})
    logger.log_block_end(block2_id, "COMPLETED", outputs2)
    
    run_outputs = logger.get_run_outputs(run_id)
    
    assert len(run_outputs) == 2
    assert run_outputs["Block1"] == outputs1
    assert run_outputs["Block2"] == outputs2


def test_get_block_status(logger):
    """Test retrieving block status."""
    run_id = "test-run-1"
    block_id = "block-exec-1"
    block_name = "TestBlock"
    
    # Test non-existent block
    assert logger.get_block_status(run_id, block_name) is None
    
    # Test existing block
    logger.log_run_start(run_id, "TestWorkflow")
    logger.log_block_start(block_id, run_id, block_name, {})
    logger.log_block_end(block_id, "COMPLETED", {})
    
    assert logger.get_block_status(run_id, block_name) == "COMPLETED"


def test_json_serialization_error_handling(logger):
    """Test handling of JSON serialization errors."""
    run_id = "test-run-1"
    block_id = "block-exec-1"
    block_name = "TestBlock"
    
    # Create an object that can't be JSON serialized
    class UnserializableObject:
        pass
    
    bad_inputs = {"obj": UnserializableObject()}
    
    logger.log_run_start(run_id, "TestWorkflow")
    logger.log_block_start(block_id, run_id, block_name, bad_inputs)
    
    cursor = logger.conn.cursor()
    cursor.execute("SELECT inputs FROM run_details WHERE block_execution_id = ?", (block_id,))
    inputs_json = cursor.fetchone()[0]
    
    # Verify that error was properly handled
    inputs_dict = json.loads(inputs_json)
    assert "error" in inputs_dict
    assert "Failed to serialize inputs" in inputs_dict["error"]