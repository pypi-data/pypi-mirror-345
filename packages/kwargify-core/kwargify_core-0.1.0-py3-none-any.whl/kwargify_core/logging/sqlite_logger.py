"""SQLite-based logging implementation for Kwargify workflows."""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Union, List


class SQLiteLogger:
    """Logger class that uses SQLite to store workflow execution details."""

    def __init__(self, db_path: str):
        """Initialize SQLiteLogger with the database path.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create the required database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Create workflows table for registering workflows
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create workflow_versions table for version tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                definition_snapshot TEXT NOT NULL,
                mermaid_diagram TEXT,
                source_path TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows (id),
                UNIQUE (workflow_id, version_number)
            )
        """)

        # Create run_summary table with workflow_version_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_summary (
                run_id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                workflow_version_id INTEGER,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT NOT NULL,
                resumed_from_run_id TEXT,
                FOREIGN KEY (workflow_version_id) REFERENCES workflow_versions (id)
            )
        """)

        # Create run_details table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_details (
                block_execution_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                block_name TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT NOT NULL,
                inputs TEXT,
                outputs TEXT,
                error_message TEXT,
                retries_attempted INTEGER DEFAULT 0,
                FOREIGN KEY (run_id) REFERENCES run_summary(run_id)
            )
        """)

        # Create run_logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_execution_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                FOREIGN KEY (block_execution_id) REFERENCES run_details(block_execution_id),
                FOREIGN KEY (run_id) REFERENCES run_summary(run_id)
            )
        """)

        self.conn.commit()

    def log_run_start(
        self,
        run_id: str,
        workflow_name: str,
        resumed_from_run_id: Optional[str] = None,
        workflow_version_id: Optional[int] = None
    ) -> None:
        """Log the start of a workflow run.

        Args:
            run_id (str): Unique identifier for this run
            workflow_name (str): Name of the workflow
            resumed_from_run_id (Optional[str]): ID of the run being resumed, if any
            workflow_version_id (Optional[int]): ID of the workflow version being run, if from registry
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO run_summary (
                run_id, workflow_name, workflow_version_id,
                start_time, status, resumed_from_run_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (run_id, workflow_name, workflow_version_id,
             datetime.now(), "STARTED", resumed_from_run_id)
        )
        self.conn.commit()

    def log_run_end(self, run_id: str, status: str) -> None:
        """Log the end of a workflow run.

        Args:
            run_id (str): Unique identifier for this run
            status (str): Final status of the run ('COMPLETED', 'FAILED', 'PARTIAL')
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE run_summary
            SET end_time = ?, status = ?
            WHERE run_id = ?
            """,
            (datetime.now(), status, run_id)
        )
        self.conn.commit()

    def log_block_start(self, block_execution_id: str, run_id: str, block_name: str, inputs: Dict) -> None:
        """Log the start of a block execution.

        Args:
            block_execution_id (str): Unique identifier for this block execution
            run_id (str): ID of the workflow run
            block_name (str): Name of the block
            inputs (Dict): Input parameters for the block
        """
        cursor = self.conn.cursor()
        try:
            inputs_json = json.dumps(inputs)
        except Exception as e:
            inputs_json = json.dumps({"error": f"Failed to serialize inputs: {str(e)}"})

        cursor.execute(
            """
            INSERT INTO run_details (
                block_execution_id, run_id, block_name, start_time,
                status, inputs
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (block_execution_id, run_id, block_name, datetime.now(), "STARTED", inputs_json)
        )
        self.conn.commit()

    def log_block_end(
        self,
        block_execution_id: str,
        status: str,
        outputs: Optional[Dict] = None,
        error_message: Optional[str] = None,
        retries_attempted: int = 0
    ) -> None:
        """Log the end of a block execution.

        Args:
            block_execution_id (str): Unique identifier for this block execution
            status (str): Final status of the block ('COMPLETED', 'FAILED')
            outputs (Optional[Dict]): Output data from the block
            error_message (Optional[str]): Error message if the block failed
            retries_attempted (int): Number of retries attempted before final status
        """
        cursor = self.conn.cursor()
        try:
            outputs_json = json.dumps(outputs) if outputs is not None else None
        except Exception as e:
            outputs_json = json.dumps({"error": f"Failed to serialize outputs: {str(e)}"})

        cursor.execute(
            """
            UPDATE run_details
            SET end_time = ?, status = ?, outputs = ?, error_message = ?, retries_attempted = ?
            WHERE block_execution_id = ?
            """,
            (datetime.now(), status, outputs_json, error_message, retries_attempted, block_execution_id)
        )
        self.conn.commit()

    def log_block_skipped(
        self,
        block_execution_id: str,
        run_id: str,
        block_name: str,
        outputs: Dict
    ) -> None:
        """Log a skipped block execution (used during workflow resume).

        Args:
            block_execution_id (str): Unique identifier for this block execution
            run_id (str): ID of the workflow run
            block_name (str): Name of the block
            outputs (Dict): Previously computed outputs for this block
        """
        cursor = self.conn.cursor()
        now = datetime.now()
        try:
            outputs_json = json.dumps(outputs)
        except Exception as e:
            outputs_json = json.dumps({"error": f"Failed to serialize outputs: {str(e)}"})

        cursor.execute(
            """
            INSERT INTO run_details (
                block_execution_id, run_id, block_name,
                start_time, end_time, status, outputs
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (block_execution_id, run_id, block_name, now, now, "SKIPPED", outputs_json)
        )
        self.conn.commit()

    def log_message(
        self,
        block_execution_id: str,
        run_id: str,
        level: str,
        message: str
    ) -> None:
        """Log a message during block execution.

        Args:
            block_execution_id (str): ID of the block execution
            run_id (str): ID of the workflow run
            level (str): Log level ('INFO', 'DEBUG', 'WARNING', 'ERROR')
            message (str): The log message
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO run_logs (
                block_execution_id, run_id, timestamp, level, message
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (block_execution_id, run_id, datetime.now(), level, message)
        )
        self.conn.commit()

    def get_run_outputs(self, run_id: str) -> Dict[str, Dict]:
        """Retrieve outputs from all completed blocks in a run.

        Args:
            run_id (str): ID of the workflow run

        Returns:
            Dict[str, Dict]: Mapping of block names to their outputs
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT block_name, outputs
            FROM run_details
            WHERE run_id = ? AND status = 'COMPLETED'
            """,
            (run_id,)
        )
        
        results = {}
        for block_name, outputs_json in cursor.fetchall():
            try:
                results[block_name] = json.loads(outputs_json) if outputs_json else {}
            except json.JSONDecodeError:
                results[block_name] = {"error": "Failed to deserialize outputs"}
        return results

    def get_block_status(self, run_id: str, block_name: str) -> Optional[str]:
        """Get the status of a specific block's most recent execution in a run.

        Args:
            run_id (str): ID of the workflow run
            block_name (str): Name of the block

        Returns:
            Optional[str]: Status of the block or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT status
            FROM run_details
            WHERE run_id = ? AND block_name = ?
            ORDER BY start_time DESC
            LIMIT 1
            """,
            (run_id, block_name)
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def list_runs(self, limit: int = 50) -> List[Dict]:
        """List recent workflow runs.

        Args:
            limit (int, optional): Maximum number of runs to return. Defaults to 50.

        Returns:
            List[Dict]: List of workflow runs, each containing run_id, workflow_name,
                       start_time, end_time, and status.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT run_id, workflow_name, start_time, end_time, status
            FROM run_summary
            ORDER BY start_time DESC
            LIMIT ?
            """,
            (limit,)
        )
        
        runs = []
        for row in cursor.fetchall():
            runs.append({
                "run_id": row[0],
                "workflow_name": row[1],
                "start_time": row[2],
                "end_time": row[3],
                "status": row[4]
            })
        return runs

    def get_run_details(self, run_id: str) -> Optional[Dict]:
        """Get detailed information about a specific workflow run.

        Args:
            run_id (str): ID of the workflow run

        Returns:
            Optional[Dict]: Run details including run info and block executions,
                          or None if run not found
        """
        cursor = self.conn.cursor()
        
        # Get run summary
        cursor.execute(
            """
            SELECT workflow_name, start_time, end_time, status
            FROM run_summary
            WHERE run_id = ?
            """,
            (run_id,)
        )
        run_info = cursor.fetchone()
        if not run_info:
            return None
            
        # Get block executions
        cursor.execute(
            """
            SELECT block_name, start_time, end_time, status,
                   inputs, outputs, error_message, retries_attempted
            FROM run_details
            WHERE run_id = ?
            ORDER BY start_time ASC
            """,
            (run_id,)
        )
        
        blocks = []
        for row in cursor.fetchall():
            block = {
                "block_name": row[0],
                "start_time": row[1],
                "end_time": row[2],
                "status": row[3],
                "inputs": json.loads(row[4]) if row[4] else {},
                "outputs": json.loads(row[5]) if row[5] else {},
                "error_message": row[6],
                "retries_attempted": row[7]
            }
            blocks.append(block)
            
        return {
            "run_id": run_id,
            "workflow_name": run_info[0],
            "start_time": run_info[1],
            "end_time": run_info[2],
            "status": run_info[3],
            "blocks": blocks
        }

    def __del__(self):
        """Ensure database connection is closed when object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close()