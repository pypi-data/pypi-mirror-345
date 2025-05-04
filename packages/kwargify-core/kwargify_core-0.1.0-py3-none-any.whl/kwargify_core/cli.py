"""Command-line interface for Kwargify workflows."""

import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pkg_resources

from kwargify_core.logging.sqlite_logger import SQLiteLogger

from kwargify_core.loader import load_workflow_from_py, WorkflowLoadError
from kwargify_core.registry import WorkflowRegistry, WorkflowRegistryError

# Create console for rich output
console = Console()

# Create the main Typer application
app = typer.Typer(
    name="kwargify",
    help="Kwargify: Define, run, and manage workflows.",
    no_args_is_help=True,
    rich_help_panel="Kwargify CLI"
)


def get_version() -> str:
    """Get the version of kwargify-core package."""
    try:
        return pkg_resources.get_distribution('kwargify-core').version
    except pkg_resources.DistributionNotFound:
        return "unknown"


def version_callback(value: bool):
    """Callback for --version flag."""
    if value:
        typer.echo(f"Kwargify CLI Version: {get_version()}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    Kwargify CLI - Define, run, and manage workflows.

    A command-line tool for working with Kwargify workflows. Use this tool to:
    - Run workflows defined in Python files
    - Validate workflow structure
    - Visualize workflow dependencies
    - Register and version workflows
    """
    pass


@app.command("run")
def run_workflow(
    workflow_path: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the workflow Python file (.py)"
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Name of the registered workflow to run"
    ),
    version: Optional[int] = typer.Option(
        None,
        "--version",
        "-v",
        help="Version of the registered workflow to run (default: latest)"
    ),
    resume_id: Optional[str] = typer.Option(
        None,
        "--resume-id",
        help="ID of the previous run to resume from. If --resume-after is not specified, resumes after the last successful block."
    ),
    resume_after: Optional[str] = typer.Option(
        None,
        "--resume-after",
        help="Name of the last completed block after which to resume. If not specified, resumes after the last successful block."
    )
) -> None:
    """
    Run a workflow from a file or from the registry.

    The workflow can be specified either by:
    - A path to a Python file containing the workflow definition
    - A name (and optional version) of a registered workflow
    """
    # Validate inputs
    if not workflow_path and not name:
        typer.echo("Error: Must provide either a workflow path or --name. Use --help for usage information.", err=True)
        raise typer.Exit(code=1)
    if workflow_path and name:
        typer.echo("Error: Cannot provide both workflow path and --name. Please use only one method to specify the workflow.", err=True)
        raise typer.Exit(code=1)

    # Validate resume parameters
    if resume_after and not resume_id:
        typer.echo("Error: --resume-after requires --resume-id to identify the previous run.", err=True)
        raise typer.Exit(code=1)

    if resume_id and not resume_after:
        # Automatically find the last successful block
        logger = SQLiteLogger("kwargify_runs.db")
        run_details = logger.get_run_details(resume_id)
        if not run_details:
            typer.echo(f"Error: Could not find run with ID: {resume_id}", err=True)
            raise typer.Exit(code=1)

        completed_blocks = [block for block in run_details['blocks'] if block['status'] == 'COMPLETED']
        if not completed_blocks:
            typer.echo("Error: No successfully completed blocks found in the previous run.", err=True)
            raise typer.Exit(code=1)

        # Get the last successful block
        resume_after = completed_blocks[-1]['block_name']
        typer.echo(f"Auto-resuming after last successful block: {resume_after}")

    try:
        workflow_version_id = None

        if name:
            # Run registered workflow
            registry = WorkflowRegistry()
            details = registry.get_version_details(name, version)
            workflow_version_id = details["id"]
            workflow_path = Path(details["source_path"])
            
            if not workflow_path.exists():
                raise WorkflowLoadError(
                    f"Source file for workflow '{name}' version {version or 'latest'} "
                    f"not found at: {workflow_path}"
                )
            
            typer.echo(f"Loading registered workflow: {name} (Version: {details['version']})")
            workflow = load_workflow_from_py(str(workflow_path))
            typer.echo(f"Run ID: {workflow.run_id}")
        else:
            # Run workflow from file
            typer.echo(f"Loading workflow from: {workflow_path}")
            workflow = load_workflow_from_py(str(workflow_path))
            typer.echo(f"Run ID: {workflow.run_id}")
        
        typer.echo(f"Starting workflow: {workflow.name}")
        if resume_id and resume_after:
            typer.echo(f"Attempting to resume from block: {resume_after}")
            typer.echo(f"Resumed Run ID: {resume_id}")
        workflow.run(
            workflow_version_id=workflow_version_id,
            resume_from_run_id=resume_id,
            resume_after_block_name=resume_after
        )
        typer.echo(f"Workflow completed successfully")

    except (WorkflowLoadError, WorkflowRegistryError) as e:
        typer.echo(f"Error loading workflow: {e}\nPlease ensure the workflow file exists and contains a valid get_workflow() function.", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error running workflow: {e}\nCheck the workflow configuration and ensure all required dependencies are satisfied.", err=True)
        raise typer.Exit(code=1)


@app.command("validate")
def validate_workflow(
    workflow_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the workflow Python file (.py)"
    )
) -> None:
    """
    Validate a workflow defined in a Python file without executing it.

    Checks:
    - File can be loaded successfully
    - get_workflow() function exists and returns a Workflow
    - No circular dependencies in the workflow graph
    - All block dependencies are satisfied
    """
    try:
        typer.echo(f"Validating workflow from: {workflow_path}")
        workflow = load_workflow_from_py(str(workflow_path))
        
        # Check for cycles in the dependency graph
        typer.echo("Checking for circular dependencies...")
        workflow.topological_sort()  # This will raise an error if cycles exist
        
        # Check if all blocks have their dependencies added to the workflow
        missing_deps = []
        for block in workflow.blocks:
            for dep in block.dependencies:
                if dep not in workflow.blocks:
                    missing_deps.append(f"Block '{block.name}' depends on '{dep.name}' but it's not in the workflow")
        
        if missing_deps:
            raise ValueError("Missing dependencies:\n" + "\n".join(f"- {dep}" for dep in missing_deps))

        typer.echo(typer.style("\n✓ Workflow validation successful!", fg=typer.colors.GREEN, bold=True))
        typer.echo(f"- Name: {workflow.name}")
        typer.echo(f"- Blocks: {len(workflow.blocks)}")
        block_names = [block.name for block in workflow.topological_sort()]
        typer.echo(f"- Execution order: {' -> '.join(block_names)}")

    except WorkflowLoadError as e:
        typer.echo(f"Error loading workflow: {e}", err=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Validation Error: {e}\nPlease fix the issues and try again. See docs/cli_usage_guide.md for help.", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error during validation: {e}\nThis might be a bug. Please report it if the issue persists.", err=True)
        raise typer.Exit(code=1)


@app.command("show")
def show_workflow(
    workflow_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the workflow Python file (.py)"
    ),
    diagram: bool = typer.Option(
        False,
        "--diagram",
        "-d",
        help="Show the Mermaid diagram definition instead of summary"
    )
) -> None:
    """
    Display a summary or the Mermaid diagram of a workflow.
    
    Shows a human-readable summary by default, including blocks and their dependencies.
    Use --diagram to get the Mermaid diagram definition instead.
    """
    try:
        workflow = load_workflow_from_py(str(workflow_path))
        
        if diagram:
            typer.echo("```mermaid")
            typer.echo(workflow.to_mermaid())
            typer.echo("```")
        else:
            # Display workflow summary
            typer.echo(f"\nWorkflow Summary: {workflow.name}")
            typer.echo("=" * (len(workflow.name) + 16))
            
            # Get blocks in execution order
            sorted_blocks = workflow.topological_sort()
            
            typer.echo(f"\nTotal Blocks: {len(workflow.blocks)}")
            typer.echo("\nExecution Order:")
            for i, block in enumerate(sorted_blocks, 1):
                deps = [dep.name for dep in block.dependencies]
                deps_str = f" (depends on: {', '.join(deps)})" if deps else ""
                typer.echo(f"{i}. {block.name}{deps_str}")
            
            # Display block details
            typer.echo("\nBlock Details:")
            for block in sorted_blocks:
                typer.echo(f"\n{block.name}:")
                if hasattr(block, 'config') and block.config:
                    typer.echo("  Config:")
                    for key, value in block.config.items():
                        typer.echo(f"    {key}: {value}")
                if hasattr(block, 'input_map') and block.input_map:
                    typer.echo("  Input Mappings:")
                    for input_key, (source_block, output_key) in block.input_map.items():
                        typer.echo(f"    {input_key} <- {source_block.name}.{output_key}")

    except WorkflowLoadError as e:
        typer.echo(f"Error loading workflow: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error showing workflow: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("register")
def register_workflow(
    workflow_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the workflow Python file (.py)"
    ),
    description: Optional[str] = typer.Option(
        None,
        "--description",
        "-d",
        help="Optional description of the workflow"
    )
) -> None:
    """
    Register a workflow in the registry or create a new version if it exists.
    """
    try:
        registry = WorkflowRegistry()
        typer.echo(f"Registering workflow from: {workflow_path}")
        
        result = registry.register(str(workflow_path), description)
        
        typer.echo(typer.style("\n✓ Workflow registered successfully!", fg=typer.colors.GREEN))
        typer.echo(f"Name: {result['workflow_name']}")
        typer.echo(f"Version: {result['version']}")
        typer.echo(f"Source Hash: {result['source_hash']}")

    except (WorkflowLoadError, WorkflowRegistryError) as e:
        typer.echo(f"Error registering workflow: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("list")
def list_workflows(
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Show versions for a specific workflow"
    )
) -> None:
    """
    List registered workflows or versions of a specific workflow.
    """
    try:
        registry = WorkflowRegistry()
        
        if name:
            # Show versions of specific workflow
            versions = registry.list_versions(name)
            
            # Create versions table
            table = Table(title=f"Versions of Workflow: {name}")
            table.add_column("Version", justify="right")
            table.add_column("Created", justify="left")
            table.add_column("Source Path", justify="left")
            table.add_column("Source Hash", justify="left")
            
            for version in versions:
                created = datetime.fromisoformat(version["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
                table.add_row(
                    str(version["version"]),
                    created,
                    str(version["source_path"]),
                    version["source_hash"][:8] + "..."  # Show first 8 chars
                )
            
            console.print(table)
            
        else:
            # List all workflows
            workflows = registry.list_workflows()
            
            # Create workflows table
            table = Table(title="Registered Workflows")
            table.add_column("Name", justify="left")
            table.add_column("Latest Version", justify="right")
            table.add_column("Description", justify="left")
            table.add_column("Created", justify="left")
            
            for workflow in workflows:
                created = datetime.fromisoformat(workflow["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
                table.add_row(
                    workflow["name"],
                    str(workflow["latest_version"] or "N/A"),
                    workflow["description"] or "No description",
                    created
                )
            
            console.print(table)

    except WorkflowRegistryError as e:
        typer.echo(f"Error listing workflows: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command("history")
def show_history(
    run_id: Optional[str] = typer.Argument(
        None,
        help="Specific run ID to show details for"
    )
) -> None:
    """
    Show workflow run history or details of a specific run.

    If run_id is provided, shows detailed information about that specific run.
    Otherwise, lists recent workflow runs.
    """
    try:
        logger = SQLiteLogger("kwargify_runs.db")

        if run_id:
            # Show details for specific run
            run_details = logger.get_run_details(run_id)
            if not run_details:
                typer.echo(f"Run not found: {run_id}", err=True)
                raise typer.Exit(code=1)

            # Display run summary
            console.print(Panel.fit(
                f"[bold]Workflow:[/bold] {run_details['workflow_name']}\n"
                f"[bold]Run ID:[/bold] {run_details['run_id']}\n"
                f"[bold]Status:[/bold] {run_details['status']}\n"
                f"[bold]Started:[/bold] {run_details['start_time']}\n"
                f"[bold]Ended:[/bold] {run_details['end_time'] or 'Not completed'}"
            ))

            # Display block executions
            table = Table(title="Block Executions")
            table.add_column("Block", justify="left")
            table.add_column("Status", justify="center")
            table.add_column("Started", justify="left")
            table.add_column("Duration", justify="right")
            table.add_column("Retries", justify="center")

            for block in run_details['blocks']:
                start_time = datetime.fromisoformat(block['start_time'])
                end_time = datetime.fromisoformat(block['end_time']) if block['end_time'] else None
                duration = str(end_time - start_time) if end_time else "N/A"

                table.add_row(
                    block['block_name'],
                    f"[{'green' if block['status'] == 'COMPLETED' else 'red'}]{block['status']}[/]",
                    start_time.strftime("%H:%M:%S"),
                    duration,
                    str(block['retries_attempted'])
                )

            console.print("\n[bold]Execution Details:[/bold]")
            console.print(table)

            # Show inputs and outputs for each block
            for block in run_details['blocks']:
                console.print(f"\n[bold]{block['block_name']}[/bold]")
                if block['inputs']:
                    console.print("  [cyan]Inputs:[/cyan]")
                    for key, value in block['inputs'].items():
                        console.print(f"    {key}: {value}")
                if block['outputs']:
                    console.print("  [green]Outputs:[/green]")
                    for key, value in block['outputs'].items():
                        console.print(f"    {key}: {value}")
                if block['error_message']:
                    console.print(f"  [red]Error:[/red] {block['error_message']}")

        else:
            # List recent runs
            runs = logger.list_runs()
            if not runs:
                typer.echo("No workflow runs found")
                return

            table = Table(title="Recent Workflow Runs")
            table.add_column("Run ID", justify="left")
            table.add_column("Workflow", justify="left")
            table.add_column("Status", justify="center")
            table.add_column("Started", justify="left")
            table.add_column("Duration", justify="right")

            for run in runs:
                start_time = datetime.fromisoformat(run['start_time'])
                end_time = datetime.fromisoformat(run['end_time']) if run['end_time'] else None
                duration = str(end_time - start_time) if end_time else "Running..."

                table.add_row(
                    run['run_id'],
                    run['workflow_name'],
                    f"[{'green' if run['status'] == 'COMPLETED' else 'red'}]{run['status']}[/]",
                    start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    duration
                )

            console.print(table)

    except Exception as e:
        typer.echo(f"Error accessing workflow history: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()