from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Block(ABC):
    """
    Base class for all blocks in the workflow.

    Each block should:
    - Declare any upstream dependencies using `add_dependency()`
    - Accept inputs via `set_input()`
    - Merge upstream outputs via `collect_inputs_from_dependencies()`
    - Implement the `run()` method to produce outputs
    """

    def __init__(self, name: str = "", config: Dict[str, Any] = None, max_retries: Optional[int] = None):
        self.name = name or self.__class__.__name__
        self.config: Dict[str, Any] = config or {}
        self.max_retries: Optional[int] = max_retries

        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}

        self.dependencies: List["Block"] = []
        self.has_run: bool = False

    def add_dependency(self, block: "Block") -> None:
        """Declare a dependency on another block."""
        self.dependencies.append(block)

    def set_input(self, key: str, value: Any) -> None:
        """Set an input manually (or override)."""
        self.inputs[key] = value

    def get_output(self, key: str) -> Any:
        """Access a specific output."""
        return self.outputs.get(key)

    def collect_inputs_from_dependencies(self) -> None:
        """Pull outputs from dependencies and merge into inputs."""
        for dep in self.dependencies:
            if not dep.has_run:
                dep.run()
                dep.has_run = True
            self.inputs.update(dep.outputs)

    @abstractmethod
    def run(self) -> None:
        """Run the block's logic. Must be implemented by subclasses."""
        raise NotImplementedError("Each block must implement its own `run()` method.")
