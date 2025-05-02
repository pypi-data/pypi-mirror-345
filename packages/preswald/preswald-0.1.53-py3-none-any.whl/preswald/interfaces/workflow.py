import hashlib
import inspect
import logging
import pickle
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Optional

import networkx as nx
import plotly.graph_objects as go


# Set up logging
logger = logging.getLogger(__name__)


class AtomStatus(Enum):
    """Represents the current status of an atom's execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"


@dataclass
class AtomResult:
    """Represents the result of an atom's execution."""

    status: AtomStatus
    value: Any = None
    error: Exception | None = None
    attempts: int = 0
    start_time: float | None = None
    end_time: float | None = None
    input_hash: str | None = None  # Hash of input parameters

    @property
    def execution_time(self) -> float | None:
        """Calculate the execution time if both start and end times are available."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class RetryPolicy:
    """Defines how retries should be handled for failed atoms."""

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        retry_exceptions: tuple = (Exception,),
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.retry_exceptions = retry_exceptions

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if another retry attempt should be made."""
        return attempt < self.max_attempts and isinstance(error, self.retry_exceptions)

    def get_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry attempt."""
        return self.delay * (self.backoff_factor ** (attempt - 1))


class AtomCache:
    """Manages caching of atom results and determines when recomputation is needed."""

    def __init__(self):
        self.cache: dict[str, AtomResult] = {}
        self.hash_cache: dict[str, str] = {}  # Stores input parameter hashes

    def compute_input_hash(self, atom_name: str, kwargs: dict[str, Any]) -> str:
        """
        Compute a hash of the input parameters to determine if recomputation is needed.
        The hash includes:
        1. The atom name (since different atoms with same inputs should have different hashes)
        2. The input parameter values
        3. The hashes of any dependent atoms (to capture changes in the dependency chain)
        """
        # Create a list of items to hash
        hash_items = [
            atom_name,
            # Sort kwargs to ensure consistent ordering
            sorted([(k, self._hash_value(v)) for k, v in kwargs.items()]),
        ]

        # Convert to bytes and hash
        hash_str = str(hash_items).encode("utf-8")
        return hashlib.sha256(hash_str).hexdigest()

    def _hash_value(self, value: Any) -> str:
        """
        Create a hash for a value, handling different types appropriately.
        For complex objects, we use their memory address as a proxy for identity.
        """
        try:
            # Try to pickle the value first
            return hashlib.sha256(pickle.dumps(value)).hexdigest()
        except:
            # If pickling fails, use the object's memory address
            return str(id(value))

    def should_recompute(self, atom_name: str, input_hash: str) -> bool:
        """Determine if an atom needs to be recomputed based on its inputs."""
        if atom_name not in self.cache:
            return True

        cached_result = self.cache[atom_name]
        return cached_result.input_hash != input_hash


@dataclass
class Atom:
    """
    Represents a cell/atom in the workflow, containing code and its dependencies.
    """

    name: str
    func: Callable
    original_func: Callable
    dependencies: set[str] = field(default_factory=set)
    retry_policy: RetryPolicy | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    force_recompute: bool = False  # Flag to force recomputation regardless of cache

    def __post_init__(self):
        # Extract function signature to understand inputs
        self.signature = inspect.signature(self.func)
        # Set default retry policy if none provided
        if self.retry_policy is None:
            self.retry_policy = RetryPolicy()

        # Store the original function
        self.original_func = self.func

        # Create the wrapped function
        @wraps(self.original_func)
        def wrapped_func(*args, **kwargs):
            logger.info(f"Executing atom: {self.name}")
            start_time = time.time()
            try:
                result = self.original_func(*args, **kwargs)
                logger.info(f"Atom {self.name} completed successfully")
                return result
            except Exception as e:
                logger.error(
                    f"Atom {self.name} failed with error: {e!s}", exc_info=True
                )
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.info(f"Atom {self.name} execution time: {execution_time:.2f}s")

        # Replace the function with the wrapped version
        self.func = wrapped_func


class WorkflowContext:
    """
    Maintains the state and variables across atoms in the workflow.
    """

    def __init__(self):
        self.variables: dict[str, Any] = {}
        self.results: dict[str, AtomResult] = {}

    def get_variable(self, name: str) -> Any:
        return self.variables.get(name)

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def set_result(self, atom_name: str, result: AtomResult):
        self.results[atom_name] = result
        if result.status == AtomStatus.COMPLETED:
            self.variables[atom_name] = result.value
            logger.info(f"[CONTEXT] Set result for {atom_name} = {result.value}")

class Workflow:
    """
    Main workflow class that manages atoms and their execution.
    """

    def __init__(self, service: Optional["BasePreswaldService"] = None, default_retry_policy: RetryPolicy | None = None):
        self.atoms: dict[str, Atom] = {}
        self.context = WorkflowContext()
        self.default_retry_policy = default_retry_policy or RetryPolicy()
        self.cache = AtomCache()
        self._component_producers: dict[str, str] = {}  # component_id -> atom_name
        self._current_atom: str | None = None  # currently executing atom
        self._service = service
        self._is_rerun = False

    def atom(
        self,
        dependencies: list[str] | None = None,
        retry_policy: RetryPolicy | None = None,
        force_recompute: bool = False,
    ):
        """
        Decorator to create and register an atom in the workflow.

        If no dependencies are provided explicitly, the decorator will infer them
        from the function’s parameter names.

        Example:
            @workflow.atom()
            def show_name(name):
                text(f"Hello, {name}")

            @workflow.atom()
            def name_input():
                return text_input("Enter your name")

        Args:
            dependencies: Optional list of atom names this atom depends on.
            retry_policy: Optional custom retry policy.
            force_recompute: If True, this atom will always recompute on execution.
        """
        def decorator(func):
            atom_name = func.__name__

            if self._is_rerun and atom_name in self.atoms:
                return func

            # Use the unwrapped function to infer dependencies
            raw_func = getattr(func, 'original_func', func)
            inferred_deps = list(inspect.signature(raw_func).parameters.keys())
            atom_deps = dependencies if dependencies is not None else inferred_deps

            atom = Atom(
                name=atom_name,
                original_func=func,
                func=func,
                dependencies=set(atom_deps),
                retry_policy=retry_policy or self.default_retry_policy,
                force_recompute=force_recompute,
            )
            self.atoms[atom_name] = atom
            return func

        return decorator

    def execute(
        self, recompute_atoms: set[str] | None = None
    ) -> dict[str, AtomResult]:
        """
        Executes atoms in the workflow, with selective recomputation.

        Args:
            recompute_atoms: Optional set of atom names to force recomputation,
                           regardless of cache status
        """
        self._is_rerun = True  # prevent duplicate re-registration
        try:
            # Clear caches and component producers, but not atoms
            self.cache.cache.clear()
            self._component_producers.clear()

            # Re-register atoms to ensure they're fresh and bound correctly
            # Preserve original atoms before clearing
            original_atoms = list(self.atoms.items())

            # Clear atoms and repopulate cleanly
            self.atoms.clear()
            for atom_name, atom in original_atoms:
                self.atoms[atom_name] = Atom(
                    name=atom_name,
                    original_func=atom.original_func,
                    func=atom.original_func,
                    dependencies=set(atom.dependencies),
                    retry_policy=atom.retry_policy,
                    force_recompute=atom.force_recompute,
                )

            execution_order = self._get_execution_order()

            # Determine which atoms need recomputation
            atoms_to_recompute = set()
            if recompute_atoms:
                atoms_to_recompute = self._get_affected_atoms(recompute_atoms)
                logger.debug(f"Atoms requiring recomputation: {atoms_to_recompute}")

            for atom_name in execution_order:
                if self._is_rerun and atoms_to_recompute and atom_name not in atoms_to_recompute:
                    logger.debug(f"Skipping atom {atom_name} (not affected)")
                    continue
                atom = self.atoms[atom_name]

                # Force recomputation if needed
                if atom_name in atoms_to_recompute:
                    atom.force_recompute = True

                # Execute the atom using values from dependencies
                result = self._execute_atom(atom)

                # Store the result in the context
                self.context.set_result(atom_name, result)

                # Reset force_recompute flag
                atom.force_recompute = False

                # If this atom failed and has dependencies, we should stop execution
                if result.status == AtomStatus.FAILED:
                    logger.error(f"Workflow stopped due to failure in atom: {atom_name}")
                    break

            return self.context.results
        finally:
            self._is_rerun = False  # reset after execution

    def get_component_producer(self, component_id: str) -> str | None:
        """Retrieve the name of the atom that last produced the component."""
        return self._component_producers.get(component_id)

    #TODO: I need to update this function with a log
    # but it is different.
    def register_component_producer(self, component_id: str):
        """Associate a component ID with the currently active atom."""
        logger.info(f"[DEBUG] Called register_component_producer({component_id})")
        if hasattr(self, '_current_atom') and self._current_atom:
            logger.info(f"[DAG] Registering {component_id} as output of {self._current_atom}")
            self._component_producers[component_id] = self._current_atom

    def _get_affected_atoms(self, changed_atoms: set[str]) -> set[str]:
        """
        Determine which atoms need to be recomputed based on changes.
        Returns a set of atom names that need recomputation.
        """
        affected = set(changed_atoms)

        logger.debug(f"[DAG] Starting traversal from: {changed_atoms}")

        # Repeatedly find atoms that depend on affected atoms until no new ones are found
        while True:
            new_affected = set()
            for atom_name, atom in self.atoms.items():
                if atom_name not in affected:  # Skip already affected atoms
                    if any(dep in affected for dep in atom.dependencies):
                        logger.debug(f"[DAG] Visiting: {atom_name}")
                        new_affected.add(atom_name)

            if not new_affected:  # No new affected atoms found
                break

            affected.update(new_affected)

        return affected

    def _validate_dependencies(self):
        """Validates that all dependencies exist and there are no cycles."""
        for atom in self.atoms.values():
            for dep in atom.dependencies:
                if dep not in self.atoms:
                    raise ValueError(
                        f"Atom '{atom.name}' depends on non-existent atom '{dep}'"
                    )

        visited = set()
        temp_visited = set()
        stack = []

        def has_cycle(atom_name: str) -> bool:
            if atom_name in temp_visited:
                logger.error(f"[CYCLE DETECTED] -> {' -> '.join(stack + [atom_name])}")
                return True
            if atom_name in visited:
                return False

            temp_visited.add(atom_name)
            stack.append(atom_name)

            for dep in self.atoms[atom_name].dependencies:
                if has_cycle(dep):
                    return True

            temp_visited.remove(atom_name)
            visited.add(atom_name)
            stack.pop()
            return False

        for atom_name in self.atoms:
            if has_cycle(atom_name):
                raise ValueError("Circular dependency detected in workflow")

    def _get_execution_order(self) -> list[str]:
        """Returns a valid execution order for atoms based on dependencies."""
        self._validate_dependencies()

        visited = set()
        order = []

        def visit(atom_name: str):
            if atom_name in visited:
                return

            for dep in self.atoms[atom_name].dependencies:
                visit(dep)

            visited.add(atom_name)
            order.append(atom_name)

        for atom_name in self.atoms:
            visit(atom_name)

        return order

    def _execute_atom(self, atom: Atom, **kwargs) -> AtomResult:
        """Execute a single atom with retry logic and caching."""
        # Compute input arguments from declared dependencies
        dependency_values = {
            dep: self.context.variables[dep]
            for dep in atom.dependencies
            if dep in self.context.variables
        }

        input_hash = self.cache.compute_input_hash(atom.name, dependency_values)
        if not atom.force_recompute and not self.cache.should_recompute(
            atom.name, input_hash
        ):
            logger.info(f"Using cached result for atom: {atom.name}")
            cached_result = self.cache.cache[atom.name]
            cached_result.status = AtomStatus.SKIPPED
            return cached_result

        self._current_atom = atom.name

        try:
            if self._service:
                with self._service.active_atom(atom.name):
                    return self._execute_atom_inner(atom, dependency_values, input_hash)
            else:
                return self._execute_atom_inner(atom, dependency_values, input_hash)
        finally:
            self._current_atom = None

    def _execute_atom_inner(self, atom, dependency_values, input_hash):
        attempts = 0
        start_time = time.time()

        while True:
            attempts += 1
            try:
                result = atom.func(**dependency_values)
                end_time = time.time()
                atom_result = AtomResult(
                    status=AtomStatus.COMPLETED,
                    value=result,
                    attempts=attempts,
                    start_time=start_time,
                    end_time=end_time,
                    input_hash=input_hash,
                )
                # Cache the successful result
                self.cache.cache[atom.name] = atom_result
                return atom_result
            except Exception as e:
                current_time = time.time()
                if atom.retry_policy.should_retry(attempts, e):
                    logger.warning(
                        f"Atom {atom.name} failed (attempt {attempts}). "
                        f"Retrying after {atom.retry_policy.get_delay(attempts)}s"
                    )
                    time.sleep(atom.retry_policy.get_delay(attempts))
                    continue
                else:
                    return AtomResult(
                        status=AtomStatus.FAILED,
                        error=e,
                        attempts=attempts,
                        start_time=start_time,
                        end_time=current_time,
                        input_hash=input_hash,
                    )


class WorkflowAnalyzer:
    """
    Provides visualization and analysis capabilities for workflow structures.
    Uses Plotly for interactive visualization and NetworkX for graph algorithms.
    """

    def __init__(self, workflow):
        self.workflow = workflow
        self.graph = nx.DiGraph()
        self._last_analysis_time = None

        # Define color scheme for different atom statuses
        self.status_colors = {
            "pending": "#E8E8E8",  # Light Gray
            "running": "#72B0DD",  # Blue
            "completed": "#72B7B7",  # Teal
            "failed": "#B76E79",  # Rose
            "retry": "#FFB347",  # Orange
            "skipped": "#D7BDE2",  # Light Purple
            "not_executed": "#C8C8C8",  # Gray
        }

    def build_graph(self) -> nx.DiGraph:
        """
        Constructs a NetworkX graph representation of the workflow.
        Includes rich metadata for visualization and analysis.
        """
        self.graph.clear()

        # Add nodes (atoms) with their metadata
        for atom_name, atom in self.workflow.atoms.items():
            result = self.workflow.context.results.get(atom_name)

            # Prepare node metadata with rich information for tooltips
            node_data = {
                "name": atom_name,
                "status": result.status.value if result else "not_executed",
                "execution_time": (
                    f"{result.execution_time:.2f}s"
                    if result and result.execution_time
                    else "N/A"
                ),
                "attempts": result.attempts if result else 0,
                "error": str(result.error) if result and result.error else None,
                "dependencies": list(atom.dependencies),
                "force_recompute": atom.force_recompute,
            }

            self.graph.add_node(atom_name, **node_data)

            # Add edges for dependencies
            for dep in atom.dependencies:
                self.graph.add_edge(dep, atom_name)

        self._last_analysis_time = datetime.now()
        return self.graph

    def get_critical_path(self) -> list[str]:
        """
        Identifies the critical path through the workflow - the longest dependency chain
        that must be executed sequentially.
        """
        if not self._is_graph_current():
            self.build_graph()

        try:
            # Find all paths and their total execution times
            paths = []
            for source in (n for n, d in self.graph.in_degree() if d == 0):
                for target in (n for n, d in self.graph.out_degree() if d == 0):
                    paths.extend(nx.all_simple_paths(self.graph, source, target))

            if not paths:
                return []

            # Calculate path weights based on execution times
            path_weights = []
            for path in paths:
                weight = sum(
                    (
                        float(self.graph.nodes[node]["execution_time"].rstrip("s"))
                        if self.graph.nodes[node]["execution_time"] != "N/A"
                        else 1.0
                    )
                    for node in path
                )
                path_weights.append((weight, path))

            return max(path_weights, key=lambda x: x[0])[1]

        except nx.NetworkXException as e:
            print(f"Error finding critical path: {e}")
            return []

    def get_parallel_groups(self) -> list[set[str]]:
        """
        Identifies groups of atoms that could potentially be executed in parallel.
        """
        if not self._is_graph_current():
            self.build_graph()

        try:
            return list(nx.topological_generations(self.graph))
        except nx.NetworkXException as e:
            print(f"Error finding parallel groups: {e}")
            return []

    def visualize(
        self,
        highlight_path: list[str] | None = None,
        title: str = "Workflow Dependency Graph",
    ):
        """
        Creates an interactive visualization of the workflow using Plotly.

        Args:
            highlight_path: Optional list of atom names to highlight (e.g., critical path)
            title: Title for the visualization
        """
        if not self._is_graph_current():
            self.build_graph()

        # Calculate layout using NetworkX
        pos = nx.spring_layout(self.graph, k=1, iterations=50)

        # Prepare node trace
        node_x, node_y = [], []
        node_colors, node_sizes = [], []
        node_texts = []

        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Get node status and set color
            status = self.graph.nodes[node]["status"]
            node_colors.append(
                self.status_colors.get(status, self.status_colors["not_executed"])
            )

            # Set node size (larger for highlighted path)
            size = 40 if highlight_path and node in highlight_path else 30
            node_sizes.append(size)

            # Create rich hover text
            hover_text = [
                f"Atom: {node}",
                f"Status: {status}",
                f"Execution Time: {self.graph.nodes[node]['execution_time']}",
                f"Attempts: {self.graph.nodes[node]['attempts']}",
            ]

            if self.graph.nodes[node]["error"]:
                hover_text.append(f"Error: {self.graph.nodes[node]['error']}")

            if self.graph.nodes[node]["dependencies"]:
                hover_text.append(
                    f"Dependencies: {', '.join(self.graph.nodes[node]['dependencies'])}"
                )

            node_texts.append("<br>".join(hover_text))

        nodes_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=list(self.graph.nodes()),
            textposition="bottom center",
            hovertext=node_texts,
            marker=dict(
                color=node_colors, size=node_sizes, line_width=2, line_color="white"
            ),
            name="Atoms",
        )

        # Prepare edge traces
        edge_traces = []

        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # Determine if this edge is part of the highlighted path
            is_highlighted = (
                highlight_path
                and edge[0] in highlight_path
                and edge[1] in highlight_path
            )

            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(
                    width=3 if is_highlighted else 1,
                    color="#d62728" if is_highlighted else "#888",
                ),
                hoverinfo="none",
                showlegend=False,
            )
            edge_traces.append(edge_trace)

        # Create the figure
        fig = go.Figure(
            data=edge_traces + [nodes_trace],
            layout=go.Layout(
                title=dict(text=title, x=0.5, y=0.95),
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="white",
            ),
        )

        # Add a legend for node status colors
        for status, color in self.status_colors.items():
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    name=status.replace("_", " ").title(),
                    showlegend=True,
                )
            )

        return fig

    def _is_graph_current(self) -> bool:
        """
        Checks if the current graph representation is up to date with the workflow state.
        """
        if self._last_analysis_time is None:
            return False

        for result in self.workflow.context.results.values():
            if (
                result.end_time
                and datetime.fromtimestamp(result.end_time) > self._last_analysis_time
            ):
                return False

        return True
