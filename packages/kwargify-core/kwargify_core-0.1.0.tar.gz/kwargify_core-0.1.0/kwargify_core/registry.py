"""Module for workflow registry functionality."""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any

from kwargify_core.core.workflow import Workflow
from kwargify_core.loader import load_workflow_from_py
from kwargify_core.logging.sqlite_logger import SQLiteLogger


class WorkflowRegistryError(Exception):
    """Raised when workflow registry operations fail."""
    pass


class WorkflowRegistry:
    """Manages the registration and versioning of workflows."""

    def __init__(self, db_path: str = "kwargify_runs.db"):
        """Initialize the registry using SQLiteLogger.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.logger = SQLiteLogger(db_path)

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file's contents.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Hexadecimal hash of the file contents
        """
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _serialize_workflow(self, workflow: Workflow) -> str:
        """Create a JSON snapshot of the workflow definition.
        
        Args:
            workflow (Workflow): The workflow to serialize
            
        Returns:
            str: JSON representation of the workflow
        """
        snapshot = {
            "name": workflow.name,
            "blocks": []
        }

        for block in workflow.blocks:
            block_data = {
                "name": block.name,
                "type": block.__class__.__name__,
                "config": block.config if hasattr(block, 'config') else {},
                "dependencies": [dep.name for dep in block.dependencies],
                "input_map": {
                    k: (v[0].name, v[1]) 
                    for k, v in block.input_map.items()
                } if hasattr(block, 'input_map') else {}
            }
            snapshot["blocks"].append(block_data)

        return json.dumps(snapshot, indent=2)

    def register(self, workflow_path: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Register a new workflow or create a new version if it already exists.
        
        Args:
            workflow_path (str): Path to the workflow Python file
            description (Optional[str]): Optional description of the workflow
            
        Returns:
            Dict[str, Any]: Registration details including workflow ID and version
            
        Raises:
            WorkflowRegistryError: If registration fails
        """
        try:
            # Load and validate the workflow
            workflow = load_workflow_from_py(workflow_path)
            source_hash = self._calculate_file_hash(workflow_path)
            mermaid_diagram = workflow.to_mermaid()
            definition_snapshot = self._serialize_workflow(workflow)

            cursor = self.logger.conn.cursor()

            # Find or create workflow entry
            cursor.execute(
                "SELECT id FROM workflows WHERE name = ?",
                (workflow.name,)
            )
            result = cursor.fetchone()

            if result:
                workflow_id = result[0]
                # Get next version number
                cursor.execute(
                    """
                    SELECT MAX(version_number)
                    FROM workflow_versions
                    WHERE workflow_id = ?
                    """,
                    (workflow_id,)
                )
                current_version = cursor.fetchone()[0] or 0
                version_number = current_version + 1
            else:
                # Create new workflow entry
                cursor.execute(
                    "INSERT INTO workflows (name, description) VALUES (?, ?)",
                    (workflow.name, description)
                )
                workflow_id = cursor.lastrowid
                version_number = 1

            # Insert new version
            cursor.execute(
                """
                INSERT INTO workflow_versions (
                    workflow_id, version_number, definition_snapshot,
                    mermaid_diagram, source_path, source_hash
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    workflow_id, version_number, definition_snapshot,
                    mermaid_diagram, workflow_path, source_hash
                )
            )

            self.logger.conn.commit()

            return {
                "workflow_id": workflow_id,
                "workflow_name": workflow.name,
                "version": version_number,
                "source_hash": source_hash
            }

        except Exception as e:
            self.logger.conn.rollback()
            raise WorkflowRegistryError(f"Failed to register workflow: {str(e)}")

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all registered workflows.
        
        Returns:
            List[Dict[str, Any]]: List of workflow details including latest version
        """
        cursor = self.logger.conn.cursor()
        cursor.execute("""
            SELECT 
                w.id, w.name, w.description, w.created_at,
                MAX(v.version_number) as latest_version,
                v.source_path
            FROM workflows w
            LEFT JOIN workflow_versions v ON w.id = v.workflow_id
            GROUP BY w.id
            ORDER BY w.name
        """)
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "latest_version": row[4],
                "source_path": row[5]
            }
            for row in cursor.fetchall()
        ]

    def list_versions(self, workflow_name: str) -> List[Dict[str, Any]]:
        """List all versions of a specific workflow.
        
        Args:
            workflow_name (str): Name of the workflow
            
        Returns:
            List[Dict[str, Any]]: List of version details
            
        Raises:
            WorkflowRegistryError: If workflow not found
        """
        cursor = self.logger.conn.cursor()
        cursor.execute(
            """
            SELECT 
                v.id, v.version_number, v.source_path,
                v.source_hash, v.created_at
            FROM workflow_versions v
            JOIN workflows w ON v.workflow_id = w.id
            WHERE w.name = ?
            ORDER BY v.version_number DESC
            """,
            (workflow_name,)
        )
        
        versions = [
            {
                "id": row[0],
                "version": row[1],
                "source_path": row[2],
                "source_hash": row[3],
                "created_at": row[4]
            }
            for row in cursor.fetchall()
        ]
        
        if not versions:
            raise WorkflowRegistryError(f"Workflow '{workflow_name}' not found")
        
        return versions

    def get_version_details(
        self,
        workflow_name: str,
        version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get details about a specific workflow version.
        
        Args:
            workflow_name (str): Name of the workflow
            version (Optional[int]): Version number (latest if None)
            
        Returns:
            Dict[str, Any]: Version details including snapshot
            
        Raises:
            WorkflowRegistryError: If version not found
        """
        cursor = self.logger.conn.cursor()
        
        if version is None:
            # Get latest version
            cursor.execute(
                """
                SELECT 
                    v.id, v.version_number, v.definition_snapshot,
                    v.mermaid_diagram, v.source_path, v.source_hash,
                    v.created_at
                FROM workflow_versions v
                JOIN workflows w ON v.workflow_id = w.id
                WHERE w.name = ?
                ORDER BY v.version_number DESC
                LIMIT 1
                """,
                (workflow_name,)
            )
        else:
            cursor.execute(
                """
                SELECT 
                    v.id, v.version_number, v.definition_snapshot,
                    v.mermaid_diagram, v.source_path, v.source_hash,
                    v.created_at
                FROM workflow_versions v
                JOIN workflows w ON v.workflow_id = w.id
                WHERE w.name = ? AND v.version_number = ?
                """,
                (workflow_name, version)
            )
            
        row = cursor.fetchone()
        if not row:
            raise WorkflowRegistryError(
                f"Version {version or 'latest'} of workflow '{workflow_name}' not found"
            )
            
        return {
            "id": row[0],
            "version": row[1],
            "definition_snapshot": json.loads(row[2]),
            "mermaid_diagram": row[3],
            "source_path": row[4],
            "source_hash": row[5],
            "created_at": row[6]
        }