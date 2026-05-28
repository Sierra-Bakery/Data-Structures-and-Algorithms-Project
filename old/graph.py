# Graph implementation for ZipRide
# This file contains the implementation of a graph data structure to represent the road network for ZipRide.
# The graph will be used to find the shortest path between locations.
# Made by Dylan Baker, 22368201
#Algorithm reference (Dijkstra):
#    Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022).
#    Introduction to algorithms. MIT Press.


import csv
import numpy as np

# Maximum nodes the graph can ever hold (static allocation)
MAX_NODES: int = 64

# Maximum edges per node (each adjacency-list row is this wide)
MAX_EDGES_PER_NODE: int = 64

# Sentinel values stored in the numpy arrays to mark "empty" slots
EMPTY_NODE: str = ""          # used in the node-name array
EMPTY_NEIGHBOUR: int = -1     # used in the neighbour-index array
EMPTY_WEIGHT: float = 0.0     # used in the weight array


# ──────────────────────────────────────────────────────────────────────────────
# Internal numpy data structures
# ──────────────────────────────────────────────────────────────────────────────

# node_names[i]  -> string name of the i-th node  (dtype=object so it holds str)
# adj_nodes[i,j] -> index of the j-th neighbour of node i  (-1 = empty slot)
# adj_weights[i,j] -> driving time (minutes) to the j-th neighbour of node i
# adj_count[i]   -> how many neighbours node i currently has
# node_count     -> how many nodes are currently registered


# ──────────────────────────────────────────────────────────────────────────────
# Graph class
# ──────────────────────────────────────────────────────────────────────────────

class Graph:
    """
    Weighted, undirected graph stored as an adjacency list.

    All internal data lives in four numpy arrays; Python lists are never used.

    Attributes
    ----------
    _node_names   : np.ndarray, shape (MAX_NODES,),        dtype=object
    _adj_nodes    : np.ndarray, shape (MAX_NODES, MAX_EDGES_PER_NODE), dtype=int32
    _adj_weights  : np.ndarray, shape (MAX_NODES, MAX_EDGES_PER_NODE), dtype=float32
    _adj_count    : np.ndarray, shape (MAX_NODES,),        dtype=int32
    _node_count   : int
    """

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self) -> None:
        """Allocate all numpy arrays and initialise to sentinel values."""

        # Node name table: one string slot per possible node
        self._node_names: np.ndarray = np.full(
            MAX_NODES, EMPTY_NODE, dtype=object
        )

        # Adjacency list (neighbour indices)
        self._adj_nodes: np.ndarray = np.full(
            (MAX_NODES, MAX_EDGES_PER_NODE), EMPTY_NEIGHBOUR, dtype=np.int32
        )

        # Adjacency list (edge weights)
        self._adj_weights: np.ndarray = np.zeros(
            (MAX_NODES, MAX_EDGES_PER_NODE), dtype=np.float32
        )

        # How many filled slots each row has
        self._adj_count: np.ndarray = np.zeros(MAX_NODES, dtype=np.int32)

        # Number of registered nodes
        self._node_count: int = 0

    # ── private helpers ───────────────────────────────────────────────────────

    def _index_of(self, name: str) -> int:
        """
        Return the integer index of *name* in _node_names, or -1 if absent.
        Uses numpy comparison to avoid a Python loop.
        """
        matches: np.ndarray = np.where(self._node_names == name)[0]
        return int(matches[0]) if matches.size > 0 else -1

    def _require_index(self, name: str) -> int:
        """Return the index of *name*, raising ValueError if not found."""
        idx = self._index_of(name)
        if idx == -1:
            raise ValueError(f"Location '{name}' does not exist in the graph.")
        return idx

    def _append_neighbour(self, from_idx: int, to_idx: int, weight: float) -> None:
        """
        Write (to_idx, weight) into the next free slot of row from_idx.
        Raises OverflowError if the row is already full.
        """
        slot: int = int(self._adj_count[from_idx])
        if slot >= MAX_EDGES_PER_NODE:
            raise OverflowError(
                f"Node '{self._node_names[from_idx]}' already has "
                f"{MAX_EDGES_PER_NODE} edges (MAX_EDGES_PER_NODE limit reached)."
            )
        self._adj_nodes[from_idx, slot] = to_idx
        self._adj_weights[from_idx, slot] = weight
        self._adj_count[from_idx] += 1

    def _neighbours_of(self, node_idx: int) -> np.ndarray:
        """
        Return a view of the filled neighbour-index slots for node_idx.
        Shape: (k,)  where k = _adj_count[node_idx].
        """
        k: int = int(self._adj_count[node_idx])
        return self._adj_nodes[node_idx, :k]

    def _weights_of(self, node_idx: int) -> np.ndarray:
        """
        Return a view of the filled weight slots for node_idx.
        Shape: (k,)  where k = _adj_count[node_idx].
        """
        k: int = int(self._adj_count[node_idx])
        return self._adj_weights[node_idx, :k]

    # ── public: node / edge insertion ─────────────────────────────────────────

    def add_location(self, name: str) -> None:
        """
        Dynamically add a new node (location) to the graph.

        Parameters
        ----------
        name : str
            Unique name for the location (e.g. 'CBD', 'Airport').

        Raises
        ------
        ValueError   if *name* is empty or already exists.
        OverflowError if MAX_NODES capacity is exhausted.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Location name must be a non-empty string.")
        if self._index_of(name) != -1:
            raise ValueError(f"Location '{name}' already exists.")
        if self._node_count >= MAX_NODES:
            raise OverflowError(
                f"Cannot add '{name}': graph capacity of {MAX_NODES} nodes reached."
            )

        self._node_names[self._node_count] = name
        self._node_count += 1
        print(f"  [add_location] '{name}' added  (total nodes: {self._node_count})")

    def add_road(self, u: str, v: str, weight: float) -> None:
        """
        Dynamically add an undirected, weighted edge between *u* and *v*.

        Undirected symmetry is enforced by writing the edge in both directions
        (u→v and v→u) with the same weight.

        Parameters
        ----------
        u, v   : str   Names of the two endpoint locations.
        weight : float Driving time in minutes (must be > 0).

        Raises
        ------
        ValueError if either node is missing, weight ≤ 0, or edge already exists.
        """
        if weight <= 0:
            raise ValueError(f"Weight must be positive (got {weight}).")
        u_idx = self._require_index(u)
        v_idx = self._require_index(v)
        if u_idx == v_idx:
            raise ValueError("Self-loops are not permitted.")

        # Guard against duplicate edges
        neighbours_u: np.ndarray = self._neighbours_of(u_idx)
        if np.any(neighbours_u == v_idx):
            raise ValueError(f"Edge '{u}' ↔ '{v}' already exists.")

        self._append_neighbour(u_idx, v_idx, weight)
        self._append_neighbour(v_idx, u_idx, weight)   # ← symmetry

        print(
            f"  [add_road]      '{u}' ↔ '{v}'  ({weight:.1f} min)  "
            f"[{u}→slots used: {int(self._adj_count[u_idx])}  "
            f"{v}→slots used: {int(self._adj_count[v_idx])}]"
        )

    # ── public: display ───────────────────────────────────────────────────────

    def display(self) -> None:
        """
        Print the full adjacency list in a readable format.
        Isolated nodes (no edges) are flagged explicitly.
        """
        print("\n" + "═" * 60)
        print("  ZipRide Road Network — Adjacency List")
        print(f"  Nodes: {self._node_count}   (capacity: {MAX_NODES})")
        print("═" * 60)

        for i in range(self._node_count):
            name: str = str(self._node_names[i])
            k: int = int(self._adj_count[i])

            if k == 0:
                print(f"  {name:<25}  [ISOLATED — no edges]")
                continue

            neighbours: np.ndarray = self._adj_nodes[i, :k]
            weights: np.ndarray    = self._adj_weights[i, :k]

            parts = np.array(
                [
                    f"{self._node_names[int(neighbours[j])]} ({weights[j]:.0f} min)"
                    for j in range(k)
                ],
                dtype=object,
            )
            row: str = "  →  ".join(parts)
            print(f"  {name:<25}  →  {row}")

        print("═" * 60 + "\n")

    # ── public: algorithms ────────────────────────────────────────────────────

    def bfs(self, source: str) -> None:
        """
        Breadth-First Search from *source*.

        Prints all reachable nodes grouped by level (distance in hops).
        Uses numpy arrays as the queue and visited tracker — no deque/list.

        Parameters
        ----------
        source : str  Starting location name.
        """
        src_idx = self._require_index(source)

        print("\n" + "─" * 60)
        print(f"  BFS from '{source}'")
        print("─" * 60)

        # visited[i] = True once node i has been enqueued
        visited: np.ndarray = np.zeros(MAX_NODES, dtype=np.bool_)

        # Queue implemented as a static numpy array with head/tail pointers
        queue: np.ndarray      = np.full(MAX_NODES, EMPTY_NEIGHBOUR, dtype=np.int32)
        queue_level: np.ndarray = np.full(MAX_NODES, -1, dtype=np.int32)
        head: int = 0
        tail: int = 0

        # Enqueue source at level 0
        queue[tail] = src_idx
        queue_level[tail] = 0
        tail += 1
        visited[src_idx] = True

        current_level: int = -1

        while head < tail:
            node_idx: int  = int(queue[head])
            level: int     = int(queue_level[head])
            head += 1

            if level != current_level:
                current_level = level
                print(f"\n  Level {current_level}:", end="")

            print(f"  {self._node_names[node_idx]}", end="")

            # Enqueue unvisited neighbours
            neighbours: np.ndarray = self._neighbours_of(node_idx)
            for nb_idx in neighbours:
                nb_idx = int(nb_idx)
                if not visited[nb_idx]:
                    visited[nb_idx] = True
                    queue[tail] = nb_idx
                    queue_level[tail] = level + 1
                    tail += 1

        # Report unreachable nodes
        unreachable = np.where(
            (self._node_names[:self._node_count] != EMPTY_NODE) & ~visited[:self._node_count]
        )[0]
        if unreachable.size > 0:
            names = np.array([self._node_names[int(i)] for i in unreachable], dtype=object)
            print(f"\n\n  Unreachable from '{source}': {',  '.join(names)}")

        print("\n" + "─" * 60 + "\n")

    def dfs_cycle(self, source: str) -> bool:
        """
        Depth-First Search from *source* with cycle detection.

        Uses numpy arrays as the stack, visited set, and recursion-stack tracker.
        Prints the cycle members if one is found.

        Returns
        -------
        bool  True if a cycle is reachable from *source*, False otherwise.
        """
        src_idx = self._require_index(source)

        print("\n" + "─" * 60)
        print(f"  DFS Cycle Detection from '{source}'")
        print("─" * 60)

        visited: np.ndarray    = np.zeros(MAX_NODES, dtype=np.bool_)
        rec_stack: np.ndarray  = np.zeros(MAX_NODES, dtype=np.bool_)
        # parent[i] = index of the node we reached i from (-1 = none)
        parent: np.ndarray     = np.full(MAX_NODES, EMPTY_NEIGHBOUR, dtype=np.int32)

        # Iterative DFS using a numpy stack
        # Each entry stores (node_index, neighbour_cursor, came_from)
        # We pack two int32 values per stack frame:  [node_idx, cursor, came_from]
        stack_nodes:  np.ndarray = np.full(MAX_NODES, EMPTY_NEIGHBOUR, dtype=np.int32)
        stack_cursor: np.ndarray = np.zeros(MAX_NODES, dtype=np.int32)
        stack_from:   np.ndarray = np.full(MAX_NODES, EMPTY_NEIGHBOUR, dtype=np.int32)
        sp: int = 0  # stack pointer (top)

        # Push source
        stack_nodes[sp]  = src_idx
        stack_cursor[sp] = 0
        stack_from[sp]   = EMPTY_NEIGHBOUR
        visited[src_idx]   = True
        rec_stack[src_idx] = True
        sp += 1

        cycle_found: bool = False

        while sp > 0 and not cycle_found:
            top:    int = sp - 1
            node:   int = int(stack_nodes[top])
            cursor: int = int(stack_cursor[top])
            came_from: int = int(stack_from[top])

            neighbours: np.ndarray = self._neighbours_of(node)

            if cursor >= int(self._adj_count[node]):
                # All neighbours processed — pop
                rec_stack[node] = False
                sp -= 1
                continue

            # Advance cursor for next visit to this frame
            stack_cursor[top] += 1
            nb: int = int(neighbours[cursor])

            # Skip the edge back to parent (undirected graph)
            if nb == came_from:
                continue

            if not visited[nb]:
                visited[nb]   = True
                rec_stack[nb] = True
                parent[nb]    = node
                stack_nodes[sp]  = nb
                stack_cursor[sp] = 0
                stack_from[sp]   = node
                sp += 1

            elif rec_stack[nb]:
                # Back-edge → cycle found; reconstruct path
                cycle_found = True

                # Walk parent chain from *node* back to *nb*
                path_buf: np.ndarray = np.full(MAX_NODES, EMPTY_NEIGHBOUR, dtype=np.int32)
                path_len: int = 0
                cur = node
                while cur != nb and cur != EMPTY_NEIGHBOUR:
                    path_buf[path_len] = cur
                    path_len += 1
                    cur = int(parent[cur])
                path_buf[path_len] = nb
                path_len += 1

                # Reverse so it reads source→…→cycle_start
                cycle_indices = path_buf[:path_len][::-1]
                cycle_names = np.array(
                    [str(self._node_names[int(i)]) for i in cycle_indices], dtype=object
                )
                cycle_str = " → ".join(cycle_names) + f" → {self._node_names[nb]}"
                print(f"  ✔ Cycle detected!")
                print(f"  Members: {cycle_str}")

        if not cycle_found:
            print("  ✘ No cycle found reachable from this source.")

        print("─" * 60 + "\n")
        return cycle_found

    def dijkstra(self, source: str, destination: str) -> tuple:
        """
        Dijkstra's single-source shortest-path algorithm (Cormen et al., 2022).

        Implementation uses numpy arrays for the distance table, visited set,
        and predecessor table.  The priority queue is maintained as an unvisited
        mask with numpy argmin — O(V²), appropriate for the graph sizes in this
        assignment.

        Parameters
        ----------
        source      : str  Starting location name.
        destination : str  Target location name.

        Returns
        -------
        (distance, path_names) : (float, np.ndarray of str)
            distance   — shortest driving time in minutes (np.inf if unreachable)
            path_names — ordered node names along the shortest path
        """
        src_idx = self._require_index(source)
        dst_idx = self._require_index(destination)

        print("\n" + "─" * 60)
        print(f"  Dijkstra  '{source}'  →  '{destination}'")
        print("─" * 60)

        INF = np.inf

        # dist[i]  = current best known distance from source to node i
        dist: np.ndarray = np.full(MAX_NODES, INF, dtype=np.float64)
        dist[src_idx] = 0.0

        # visited[i] = True once node i has been finalised
        visited: np.ndarray = np.zeros(MAX_NODES, dtype=np.bool_)

        # pred[i] = index of the predecessor of i on the shortest path (-1 = none)
        pred: np.ndarray = np.full(MAX_NODES, EMPTY_NEIGHBOUR, dtype=np.int32)

        # We only consider the first _node_count nodes
        n: int = self._node_count

        for _ in range(n):
            # Extract the unvisited node with minimum distance (manual argmin)
            # Mask already-visited nodes with INF so argmin skips them
            masked_dist = np.where(visited[:n], INF, dist[:n])
            u: int = int(np.argmin(masked_dist))

            if dist[u] == INF:
                break  # All remaining nodes are unreachable

            visited[u] = True

            if u == dst_idx:
                break  # Destination finalised — early exit

            # Relax edges out of u
            neighbours: np.ndarray = self._neighbours_of(u)
            weights:    np.ndarray = self._weights_of(u)

            for j in range(int(self._adj_count[u])):
                v: int       = int(neighbours[j])
                w: float     = float(weights[j])
                new_dist: float = float(dist[u]) + w

                if new_dist < float(dist[v]):
                    dist[v] = new_dist
                    pred[v] = u

        # ── reconstruct path ──────────────────────────────────────────────────
        path_buf: np.ndarray = np.full(MAX_NODES, EMPTY_NEIGHBOUR, dtype=np.int32)
        path_len: int = 0

        if dist[dst_idx] == INF:
            print(f"  No path found from '{source}' to '{destination}'.")
            print("─" * 60 + "\n")
            return INF, np.array([], dtype=object)

        cur: int = dst_idx
        while cur != EMPTY_NEIGHBOUR:
            path_buf[path_len] = cur
            path_len += 1
            cur = int(pred[cur])

        # Reverse the buffer (destination→source becomes source→destination)
        path_indices: np.ndarray = path_buf[:path_len][::-1]
        path_names: np.ndarray   = np.array(
            [str(self._node_names[int(i)]) for i in path_indices], dtype=object
        )

        total_dist: float = float(dist[dst_idx])
        print(f"  Shortest path : {' → '.join(path_names)}")
        print(f"  Driving time  : {total_dist:.1f} min")
        print("─" * 60 + "\n")

        return total_dist, path_names


# ──────────────────────────────────────────────────────────────────────────────
# CSV loader
# ──────────────────────────────────────────────────────────────────────────────

def load_from_csv(filepath: str) -> Graph:
    """
    Build a Graph by reading a CSV file with columns:
        NodeName, NodeDestination, WeightMinutes

    Nodes are added automatically the first time they are encountered.
    Duplicate edges are silently skipped (already-exists warning printed).

    Parameters
    ----------
    filepath : str  Path to the CSV file (e.g. 'perth_road_network.csv').

    Returns
    -------
    Graph  A fully constructed graph instance.
    """
    g = Graph()
    print(f"\n{'═' * 60}")
    print(f"  Loading graph from: {filepath}")
    print(f"{'═' * 60}")

    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            u      = row["NodeName"].strip()
            v      = row["NodeDestination"].strip()
            weight = float(row["WeightMinutes"].strip())

            # Dynamically register nodes on first encounter
            if g._index_of(u) == -1:
                g.add_location(u)
            if g._index_of(v) == -1:
                g.add_location(v)

            # Add road (skip if already present — CSV may list both directions)
            try:
                g.add_road(u, v, weight)
            except ValueError as exc:
                print(f"  [skip] {exc}")

    print(f"\n  CSV load complete — {g._node_count} nodes registered.\n")
    return g


# ──────────────────────────────────────────────────────────────────────────────
# Demo / test driver
# ──────────────────────────────────────────────────────────────────────────────

def _run_demo() -> None:
    """
    Exercise every public method of the Graph class.
    Reads the Perth road network from CSV, then runs BFS, DFS, and Dijkstra.
    """

    # ── 1. Build graph from CSV ───────────────────────────────────────────────
    g = load_from_csv("perth_road_network.csv")
    g.display()

    # ── 2. BFS from CBD ───────────────────────────────────────────────────────
    g.bfs("CBD")

    # ── 3. DFS cycle detection ────────────────────────────────────────────────
    g.dfs_cycle("CBD")

    # ── 4. Dijkstra shortest paths ────────────────────────────────────────────
    g.dijkstra("CBD", "JoondalupHospital")
    g.dijkstra("Airport", "Fremantle")
    g.dijkstra("CBD", "ParkAndRide_Midland")   # longer route through kewdale

    # ── 5. Edge-case: isolated node reachability ─────────────────────────────
    print("── Isolated node test ──────────────────────────────────────")
    g.bfs("ParkAndRide_Midland")

    # ── 6. Dynamic insertion at runtime ──────────────────────────────────────
    print("── Dynamic insertion test ──────────────────────────────────")
    g.add_location("NewSuburb_Ellenbrook")
    g.add_road("NewSuburb_Ellenbrook", "Airport", 35)
    g.add_road("NewSuburb_Ellenbrook", "SuburbNorth_Joondalup", 28)
    g.dijkstra("CBD", "NewSuburb_Ellenbrook")

    # ── 7. Error handling demo ────────────────────────────────────────────────
    print("── Error handling demo ─────────────────────────────────────")
    for label, fn in (
        ("Duplicate node",  lambda: g.add_location("CBD")),
        ("Unknown node",    lambda: g.add_road("CBD", "Atlantis", 99)),
        ("Negative weight", lambda: g.add_road("CBD", "Airport", -5)),
        ("Duplicate edge",  lambda: g.add_road("CBD", "Airport", 25)),
        ("Dijkstra miss",   lambda: g.dijkstra("CBD", "Atlantis")),
    ):
        try:
            fn()
        except (ValueError, OverflowError) as exc:
            print(f"  [{label}]  Caught expected error: {exc}")

    print("\nDemo complete.\n")


if __name__ == "__main__":
    _run_demo()