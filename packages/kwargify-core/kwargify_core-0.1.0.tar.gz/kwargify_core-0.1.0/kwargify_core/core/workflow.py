import uuid
import time
from typing import List, Set, Optional, Dict
from kwargify_core.core.block import Block
from kwargify_core.logging import SQLiteLogger

class Workflow:
    """
    Represents a DAG-style workflow of connected Blocks.

    Usage:
        wf = Workflow()
        wf.add_block(block_a)
        wf.add_block(block_b)
        wf.run()  # Executes all blocks in dependency order
    """

    def __init__(self, default_max_retries: int = 1):
        """Initialize a new workflow.

        Args:
            default_max_retries: Default number of retries for blocks that don't specify their own max_retries.

        By default, creates a workflow with a SQLite logger using 'kwargify_runs.db' as the database file.
        The workflow name defaults to "DefaultWorkflow".
        """
        self.blocks: List[Block] = []
        self.name = "DefaultWorkflow"
        self.logger = SQLiteLogger(db_path="kwargify_runs.db")
        self.default_max_retries = default_max_retries
        self.run_id = uuid.uuid4().hex

    def add_block(self, block: Block) -> None:
        """Add a block to the workflow."""
        if block not in self.blocks:
            self.blocks.append(block)

    def run(
        self,
        resume_from_run_id: Optional[str] = None,
        resume_after_block_name: Optional[str] = None,
        workflow_version_id: Optional[int] = None
    ) -> None:
        """Run all blocks in topological order with optional resume capability.

        Args:
            resume_from_run_id: Optional ID of a previous run to resume from
            resume_after_block_name: Optional name of the block after which to resume execution
            workflow_version_id: Optional ID of the registered workflow version being run

        Raises:
            ValueError: If resume is requested but the previous run's block status is not valid
        """
        # Initialize resume-related variables
        previous_outputs: Dict = {}
        blocks_to_skip = set()
        is_resuming = bool(resume_from_run_id and resume_after_block_name)

        # Get sorted blocks for execution
        sorted_blocks = self.topological_sort()

        # Handle resume logic if needed
        if is_resuming:
            previous_outputs = self.logger.get_run_outputs(resume_from_run_id)
            
            # Validate blocks up to and including resume point and mark them for skipping
            resume_block_found = False
            for block in sorted_blocks:
                status = self.logger.get_block_status(resume_from_run_id, block.name)
                if status != 'COMPLETED':
                    raise ValueError(
                        f"Cannot resume: Block '{block.name}' in previous run "
                        f"'{resume_from_run_id}' has status '{status}', expected 'COMPLETED'"
                    )
                blocks_to_skip.add(block.name)
                
                if block.name == resume_after_block_name:
                    resume_block_found = True
                    break
                    
            if not resume_block_found:
                raise ValueError(
                    f"Cannot resume: Block '{resume_after_block_name}' not found in workflow"
                )

        # Log the start of the workflow run
        self.logger.log_run_start(
            self.run_id,
            self.name,
            workflow_version_id=workflow_version_id,
            resumed_from_run_id=resume_from_run_id if is_resuming else None
        )

        try:
            # Execute or skip blocks based on the workflow
            for block in sorted_blocks:
                block_execution_id = uuid.uuid4().hex

                if block.name in blocks_to_skip:
                    # Skip this block and use previous outputs
                    block.outputs = previous_outputs.get(block.name, {})
                    block.has_run = True
                    self.logger.log_block_skipped(
                        block_execution_id,
                        self.run_id,
                        block.name,
                        block.outputs
                    )
                    continue

                # Collect inputs from dependencies
                block.collect_inputs_from_dependencies()

                # Handle input_map for wiring outputs to inputs
                if hasattr(block, "input_map"):
                    for input_key, (source_block, output_key) in block.input_map.items():
                        if source_block.has_run:
                            block.set_input(input_key, source_block.outputs.get(output_key))
                        else:
                            raise ValueError(f"Source block {source_block.name} hasn't run yet.")

                # Determine effective retries and initialize retry tracking
                effective_max_retries = block.max_retries if block.max_retries is not None else self.default_max_retries
                last_exception = None
                final_status = "UNKNOWN"
                retries_attempted = 0

                # Log block start (outside retry loop)
                self.logger.log_block_start(
                    block_execution_id,
                    self.run_id,
                    block.name,
                    block.inputs
                )

                # Retry Loop
                for attempt in range(effective_max_retries + 1):
                    retries_attempted = attempt
                    try:
                        block.run()
                        final_status = "COMPLETED"
                        last_exception = None
                        block.has_run = True
                        break  # Success, exit retry loop
                    except Exception as e:
                        last_exception = e
                        final_status = "FAILED"
                        if attempt < effective_max_retries:
                            print(f"Attempt {attempt + 1}/{effective_max_retries + 1} failed for block {block.name}. Retrying...")
                            time.sleep(1)  # Simple delay
                        else:
                            print(f"Block {block.name} failed after {effective_max_retries + 1} attempts.")

                # Log block end (outside retry loop, logs final status)
                self.logger.log_block_end(
                    block_execution_id,
                    final_status,
                    block.outputs if hasattr(block, 'outputs') else {},
                    str(last_exception) if last_exception else None,
                    retries_attempted=retries_attempted
                )

                # If the block ultimately failed, raise the last exception
                if final_status == "FAILED" and last_exception:
                    raise last_exception

            # If we get here, all blocks completed successfully
            self.logger.log_run_end(self.run_id, "COMPLETED")
        except Exception as e:
            # Log workflow failure if any block failed
            self.logger.log_run_end(self.run_id, "FAILED")
            raise

    def topological_sort(self) -> List[Block]:
        """Perform a topological sort of the blocks based on their dependencies."""
        visited: Set[Block] = set()
        temp_marked: Set[Block] = set()
        result: List[Block] = []

        def visit(block: Block):
            if block in visited:
                return
            if block in temp_marked:
                raise ValueError(f"Circular dependency detected at block: {block.name}")
            temp_marked.add(block)
            for dep in block.dependencies:
                visit(dep)
            temp_marked.remove(block)
            visited.add(block)
            result.append(block)

        for block in self.blocks:
            visit(block)

        return result

    def to_mermaid(self) -> str:
        """Generate a Mermaid diagram string representing the workflow."""
        mermaid_str = "graph TD;\n"
        # Use a consistent way to generate IDs, e.g., based on object id
        node_ids = {block: f"id{id(block)}" for block in self.blocks}

        # Define nodes
        for block, node_id in node_ids.items():
            # Escape quotes in block names for Mermaid compatibility
            safe_name = block.name.replace('"', '#quot;')
            mermaid_str += f'  {node_id}["{safe_name}"];\n'

        # Define edges (Dependencies and Input Map)
        labeled_edges = set() # Keep track of edges defined by input_map

        # First pass: Process input_map to create labeled edges
        for block in self.blocks:
            block_id = node_ids[block]
            if hasattr(block, "input_map") and isinstance(block.input_map, dict):
                for input_key, source_info in block.input_map.items():
                    if isinstance(source_info, tuple) and len(source_info) == 2:
                        source_block, output_key = source_info
                        if source_block in node_ids:
                            source_id = node_ids[source_block]
                            safe_output_key = str(output_key).replace('"', '#quot;')
                            safe_input_key = str(input_key).replace('"', '#quot;')
                            label = f'"{safe_output_key} -> {safe_input_key}"'
                            mermaid_str += f"  {source_id} -- {label} --> {block_id};\n"
                            labeled_edges.add((source_id, block_id)) # Mark this edge as labeled
                        else:
                            print(f"Warning: Source block {getattr(source_block, 'name', 'UNKNOWN')} for input '{input_key}' of block '{block.name}' not found in workflow blocks.")
                    else:
                         print(f"Warning: Invalid format for input_map item for input '{input_key}' of block '{block.name}'. Expected (source_block, output_key), got {source_info}")

        # Second pass: Process dependencies, adding simple edges only if not already labeled
        for block in self.blocks:
            block_id = node_ids[block]
            for dep in block.dependencies:
                 # Check if the dependency block is actually part of the workflow blocks added
                 if dep in node_ids:
                    dep_id = node_ids[dep]
                    edge = (dep_id, block_id)
                    if edge not in labeled_edges: # Only add if no labeled edge exists
                        mermaid_str += f"  {dep_id} --> {block_id};\n"
                 else:
                    # This case might happen if a dependency was added but the dependency block itself wasn't added to the workflow
                    print(f"Warning: Dependency block {getattr(dep, 'name', 'UNKNOWN')} for block '{block.name}' not found in workflow blocks. Skipping edge.")


        return mermaid_str
