"""
================================================================================
COMP1002 - ZipRide Dispatch System
DSA Graph — Numpy-Backed Implementation
--------------------------------------------------------------------------------
Author      : <Your Name>
Student ID  : <Your Student ID>
Date        : 2026-05-28
Description : Re-implementation of DSALinkedList and DSAGraph where every
              internal collection is a statically-allocated numpy array.
              No Python lists are used anywhere in this file.

              The original linked-list and graph logic/interface is preserved
              exactly so the rest of the project can import and call the same
              method names without changes.

              numpy is used solely for fixed-size array allocation and
              element access — no built-in graph, sort, or search helpers.
================================================================================
"""

import numpy as np


# ──────────────────────────────────────────────────────────────────────────────
# Capacity constants  (increase if your dataset grows)
# ──────────────────────────────────────────────────────────────────────────────

MAX_LIST_NODES: int   = 256   # max nodes a single DSALinkedList can hold
MAX_GRAPH_VERTICES: int = 64  # max vertices in the graph
MAX_EDGES_PER_VERTEX: int = 64  # max edges (neighbours) per vertex


# ─────────────────────────────────────────────────────────────────────────────
# DSAListNode  — unchanged interface; internal storage is just Python attrs
# (the *list itself* is what uses numpy; nodes are plain lightweight objects)
# ─────────────────────────────────────────────────────────────────────────────

class DSAListNode:
    """Lightweight container; value can be any Python object."""

    def __init__(self, value):
        self.value = value
        self.next = None   # pointer to next DSAListNode
        self.prev = None   # pointer to previous DSAListNode


# ─────────────────────────────────────────────────────────────────────────────
# DSALinkedList — backed by a numpy object array instead of chained pointers
#
#   _store[i]  : the DSAListNode at logical position i  (dtype=object)
#   _size      : how many slots are currently occupied
#   head / tail: kept as property aliases to _store[0] / _store[_size-1]
#                so all existing code that reads .head / .tail still works
# ─────────────────────────────────────────────────────────────────────────────

class DSALinkedList:
    """
    Doubly-linked list whose node storage is a statically-allocated
    numpy array of objects.  No Python list is used.

    Public interface matches the original DSALinkedList exactly.
    """

    def __init__(self):
        # Pre-allocate a fixed-size array; slots beyond _size are None
        self._store: np.ndarray = np.empty(MAX_LIST_NODES, dtype=object)
        self._store[:] = None          # initialise every slot to None
        self._size: int = 0

        # Re-wire prev/next pointers after every mutation so that any
        # external code which walks .head, .next, etc. still works.

    # ── private helpers ───────────────────────────────────────────────────────

    def _rewire(self) -> None:
        """
        Rebuild every .next / .prev pointer from the numpy array state.
        Called after every insert or remove.  O(n) but n is small here.
        """
        for i in range(self._size):
            node: DSAListNode = self._store[i]
            node.prev = self._store[i - 1] if i > 0 else None
            node.next = self._store[i + 1] if i < self._size - 1 else None

    def _check_capacity(self) -> None:
        if self._size >= MAX_LIST_NODES:
            raise OverflowError(
                f"DSALinkedList is full ({MAX_LIST_NODES} nodes max)."
            )

    # ── public properties for head / tail ─────────────────────────────────────

    @property
    def head(self) -> DSAListNode | None:
        return self._store[0] if self._size > 0 else None

    @property
    def tail(self) -> DSAListNode | None:
        return self._store[self._size - 1] if self._size > 0 else None

    # ── public interface ──────────────────────────────────────────────────────

    def isempty(self) -> bool:
        return self._size == 0

    def insert_first(self, value) -> None:
        """Insert at position 0 — O(n) shift via numpy roll."""
        self._check_capacity()
        new_node = DSAListNode(value)

        # Shift existing nodes one slot to the right
        if self._size > 0:
            self._store[1 : self._size + 1] = self._store[0 : self._size]

        self._store[0] = new_node
        self._size += 1
        self._rewire()

    def insert_last(self, value) -> None:
        """Append at the end — O(1) slot write."""
        self._check_capacity()
        new_node = DSAListNode(value)
        self._store[self._size] = new_node
        self._size += 1
        self._rewire()

    def peek_first(self):
        if self.isempty():
            raise Exception("List is empty")
        return self._store[0].value

    def peek_last(self):
        if self.isempty():
            raise Exception("List is empty")
        return self._store[self._size - 1].value

    def remove_first(self):
        """Remove and return the first value — O(n) shift."""
        if self.isempty():
            raise Exception("List is empty")
        val = self._store[0].value
        # Shift everything left
        self._store[0 : self._size - 1] = self._store[1 : self._size]
        self._store[self._size - 1] = None
        self._size -= 1
        self._rewire()
        return val

    def remove_last(self):
        """Remove and return the last value — O(1)."""
        if self.isempty():
            raise Exception("List is empty")
        val = self._store[self._size - 1].value
        self._store[self._size - 1] = None
        self._size -= 1
        self._rewire()
        return val

    def display(self) -> None:
        if self.isempty():
            print("Empty List")
        else:
            for i in range(self._size):
                print(self._store[i].value)

    def __len__(self) -> int:
        return self._size


# ─────────────────────────────────────────────────────────────────────────────
# DSAGraphVertex — unchanged interface; adjacency stored as numpy arrays
# ─────────────────────────────────────────────────────────────────────────────

class DSAGraphVertex:
    """
    Represents one vertex.

    Adjacency is stored in two parallel numpy arrays:
      _nb_labels[j]  — string label of the j-th neighbour
      _nb_weights[j] — float weight of that edge
      _nb_count      — how many neighbour slots are filled

    The .links property returns a DSALinkedList *view* built on demand,
    so that existing code using  vertex.links.head / inner.value  continues
    to work without changes.
    """

    def __init__(self, label: str, value=None):
        self.label: str   = label
        self.value        = value
        self.visited: bool = False

        # Static numpy arrays for neighbours
        self._nb_labels: np.ndarray  = np.full(MAX_EDGES_PER_VERTEX, "", dtype=object)
        self._nb_weights: np.ndarray = np.zeros(MAX_EDGES_PER_VERTEX, dtype=np.float32)
        self._nb_count: int = 0

    # ── adjacency helpers ─────────────────────────────────────────────────────

    def _add_neighbour(self, vertex: "DSAGraphVertex", weight: float = 1.0) -> None:
        """Write neighbour into next free numpy slot."""
        if self._nb_count >= MAX_EDGES_PER_VERTEX:
            raise OverflowError(
                f"Vertex '{self.label}' has reached MAX_EDGES_PER_VERTEX "
                f"({MAX_EDGES_PER_VERTEX})."
            )
        self._nb_labels[self._nb_count]  = vertex.label
        self._nb_weights[self._nb_count] = weight
        self._nb_count += 1

    def _remove_neighbour(self, label: str) -> None:
        """
        Remove a neighbour by label — shift the numpy arrays left to close gap.
        """
        idx = -1
        for i in range(self._nb_count):
            if self._nb_labels[i] == label:
                idx = i
                break
        if idx == -1:
            return  # not present — nothing to do

        # Shift left
        self._nb_labels[idx : self._nb_count - 1]  = (
            self._nb_labels[idx + 1 : self._nb_count]
        )
        self._nb_weights[idx : self._nb_count - 1] = (
            self._nb_weights[idx + 1 : self._nb_count]
        )
        self._nb_labels[self._nb_count - 1]  = ""
        self._nb_weights[self._nb_count - 1] = 0.0
        self._nb_count -= 1

    def _has_neighbour(self, label: str) -> bool:
        for i in range(self._nb_count):
            if self._nb_labels[i] == label:
                return True
        return False

    # ── links property: on-demand DSALinkedList view ──────────────────────────

    @property
    def links(self) -> DSALinkedList:
        """
        Build and return a DSALinkedList whose nodes hold *DSAGraphVertex*
        references for each current neighbour.  Used by BFS/DFS and
        displayAsList so their walk logic ( inner.value.label ) keeps working.

        Note: this is a snapshot — mutations after this call are not reflected.
              The graph always modifies _nb_labels/_nb_weights directly.
        """
        ll = DSALinkedList()
        for i in range(self._nb_count):
            nb_label = str(self._nb_labels[i])
            # We create a lightweight proxy vertex so .label works downstream.
            # Weight is attached as an extra attribute for Dijkstra access.
            proxy = _NeighbourProxy(nb_label, float(self._nb_weights[i]))
            ll.insert_last(proxy)
        return ll

    # ── original interface ────────────────────────────────────────────────────

    def getLabel(self) -> str:
        return self.label

    def getValue(self):
        return self.value

    def getAdjacent(self) -> DSALinkedList:
        return self.links   # returns the on-demand view

    def addEdge(self, vertex: "DSAGraphVertex", weight: float = 1.0) -> None:
        self._add_neighbour(vertex, weight)

    def setVisited(self) -> None:
        self.visited = True

    def clearVisited(self) -> None:
        self.visited = False

    def getVisited(self) -> bool:
        return self.visited

    def __str__(self) -> str:
        return str(self.label)


class _NeighbourProxy:
    """
    Lightweight stand-in returned inside .links so that code like
    `inner.value.label` and `inner.value.weight` keeps working without
    needing a real DSAGraphVertex for every iteration.
    """
    __slots__ = ("label", "weight")

    def __init__(self, label: str, weight: float):
        self.label  = label
        self.weight = weight

    def __str__(self) -> str:
        return self.label


# ─────────────────────────────────────────────────────────────────────────────
# DSAGraph — vertex store is a numpy object array
# ─────────────────────────────────────────────────────────────────────────────

class DSAGraph:
    """
    Weighted, undirected graph.

    Vertex storage: numpy object array of DSAGraphVertex (_vstore).
    The .vertices property returns a DSALinkedList view, keeping all
    existing code that walks  self.vertices.head / temp.value.label  intact.

    No Python lists are used anywhere in this class.
    """

    def __init__(self):
        # Static array of DSAGraphVertex objects
        self._vstore: np.ndarray = np.empty(MAX_GRAPH_VERTICES, dtype=object)
        self._vstore[:] = None
        self._vcount: int = 0

    # ── vertices property: on-demand linked-list view ─────────────────────────

    @property
    def vertices(self) -> DSALinkedList:
        """
        Return a DSALinkedList snapshot of all current vertices.
        Each node's .value is the actual DSAGraphVertex object.
        """
        ll = DSALinkedList()
        for i in range(self._vcount):
            ll.insert_last(self._vstore[i])
        return ll

    # ── private helpers ───────────────────────────────────────────────────────

    def _vertex_index(self, label: str) -> int:
        """Return the numpy-array index of *label*, or -1 if absent."""
        for i in range(self._vcount):
            if self._vstore[i].label == label:
                return i
        return -1

    # ── original public interface ─────────────────────────────────────────────

    def getVertex(self, label: str) -> DSAGraphVertex:
        idx = self._vertex_index(label)
        if idx == -1:
            raise Exception("Vertex not found")
        return self._vstore[idx]

    def hasVertex(self, label: str) -> bool:
        return self._vertex_index(label) != -1

    def addVertex(self, label: str, value=None) -> None:
        """Dynamically add a new vertex; raises if label already exists."""
        if self.hasVertex(label):
            raise Exception("Vertex already exists")
        if self._vcount >= MAX_GRAPH_VERTICES:
            raise OverflowError(
                f"Graph capacity of {MAX_GRAPH_VERTICES} vertices reached."
            )
        self._vstore[self._vcount] = DSAGraphVertex(label, value)
        self._vcount += 1

    def addEdge(self, label1: str, label2: str, weight: float = 1.0) -> None:
        """
        Add undirected weighted edge — symmetry enforced by writing both
        directions into the respective numpy neighbour arrays.
        """
        v1 = self.getVertex(label1)
        v2 = self.getVertex(label2)
        if v1._has_neighbour(label2):
            raise Exception(f"Edge '{label1}' ↔ '{label2}' already exists.")
        v1._add_neighbour(v2, weight)
        v2._add_neighbour(v1, weight)   # ← undirected symmetry

    def getVertexCount(self) -> int:
        return self._vcount

    def getEdgeCount(self) -> int:
        total = 0
        for i in range(self._vcount):
            total += self._vstore[i]._nb_count
        return total // 2   # each undirected edge is stored twice

    def isAdjacent(self, label1: str, label2: str) -> bool:
        return self.getVertex(label1)._has_neighbour(label2)

    def deleteEdge(self, label1: str, label2: str) -> None:
        if not self.hasVertex(label1) or not self.hasVertex(label2):
            raise Exception("Vertex not found")
        self.getVertex(label1)._remove_neighbour(label2)
        self.getVertex(label2)._remove_neighbour(label1)

    def deleteVertex(self, label: str) -> None:
        if not self.hasVertex(label):
            raise Exception("Vertex not found")
        # Remove all edges that involve this vertex
        for i in range(self._vcount):
            v = self._vstore[i]
            if v.label != label:
                v._remove_neighbour(label)
        # Remove vertex from numpy store by shifting left
        idx = self._vertex_index(label)
        self._vstore[idx : self._vcount - 1] = self._vstore[idx + 1 : self._vcount]
        self._vstore[self._vcount - 1] = None
        self._vcount -= 1

    # ── display ───────────────────────────────────────────────────────────────

    def displayAsList(self) -> None:
        print("\n" + "═" * 55)
        print("  Adjacency List")
        print("═" * 55)
        for i in range(self._vcount):
            v = self._vstore[i]
            print(f"  {v.label:<25}", end=" |")
            for j in range(v._nb_count):
                nb  = str(v._nb_labels[j])
                wt  = float(v._nb_weights[j])
                print(f"  {nb} ({wt:.0f}m)", end="")
            if v._nb_count == 0:
                print("  [isolated]", end="")
            print()
        print("═" * 55 + "\n")

    def displayAsMatrix(self) -> None:
        """Print adjacency matrix — 1/0 for connected/unconnected."""
        # Header
        print("\n  ", end="")
        for i in range(self._vcount):
            print(f"{self._vstore[i].label[:8]:>10}", end="")
        print()
        # Rows
        for i in range(self._vcount):
            print(f"  {self._vstore[i].label[:8]:<10}", end="")
            for j in range(self._vcount):
                connected = self._vstore[i]._has_neighbour(self._vstore[j].label)
                print(f"{'1':>10}" if connected else f"{'0':>10}", end="")
            print()
        print()

    # ── traversals ────────────────────────────────────────────────────────────

    def breadthFirstSearch(self) -> DSALinkedList:
        """
        BFS from the first vertex.
        Queue is a DSALinkedList (backed by numpy).
        Returns a DSALinkedList of interleaved (from, to) DSAGraphVertex pairs.
        """
        queue  = DSALinkedList()
        result = DSALinkedList()

        # Clear all visited flags
        for i in range(self._vcount):
            self._vstore[i].clearVisited()

        # Seed the queue with the first vertex
        v = self._vstore[0]
        v.setVisited()
        queue.insert_last(v)

        while not queue.isempty():
            v = queue.remove_first()
            # Walk this vertex's neighbours via its numpy arrays directly
            for j in range(v._nb_count):
                nb_label = str(v._nb_labels[j])
                w = self.getVertex(nb_label)
                if not w.getVisited():
                    result.insert_last(v)
                    result.insert_last(w)
                    w.setVisited()
                    queue.insert_last(w)

        return result

    def depthFirstSearch(self) -> DSALinkedList:
        """
        DFS from the first vertex.
        Stack is a DSALinkedList (backed by numpy).
        Returns a DSALinkedList of interleaved (from, to) DSAGraphVertex pairs.
        """
        stack  = DSALinkedList()
        result = DSALinkedList()

        # Clear all visited flags
        for i in range(self._vcount):
            self._vstore[i].clearVisited()

        v = self._vstore[0]
        v.setVisited()
        stack.insert_last(v)

        while not stack.isempty():
            # Find first unvisited neighbour of v
            w = None
            for j in range(v._nb_count):
                nb_label = str(v._nb_labels[j])
                candidate = self.getVertex(nb_label)
                if not candidate.getVisited():
                    w = candidate
                    break

            if w is not None:
                result.insert_last(v)
                result.insert_last(w)
                w.setVisited()
                stack.insert_last(w)
                v = w
            else:
                v = stack.remove_last()

        return result


# ──────────────────────────────────────────────────────────────────────────────
# CSV loader  (same signature as the one in graph.py)
# ──────────────────────────────────────────────────────────────────────────────

import csv

def load_from_csv(filepath: str) -> DSAGraph:
    """
    Build a DSAGraph from the Perth road-network CSV.
    Columns: NodeName, NodeDestination, WeightMinutes
    """
    g = DSAGraph()
    print(f"\n{'═' * 55}")
    print(f"  Loading graph from: {filepath}")
    print(f"{'═' * 55}")

    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            u      = row["NodeName"].strip()
            v      = row["NodeDestination"].strip()
            weight = float(row["WeightMinutes"].strip())

            if not g.hasVertex(u):
                g.addVertex(u)
                print(f"  [add_vertex] '{u}'")
            if not g.hasVertex(v):
                g.addVertex(v)
                print(f"  [add_vertex] '{v}'")

            try:
                g.addEdge(u, v, weight)
                print(f"  [add_edge]   '{u}' ↔ '{v}'  ({weight:.0f} min)")
            except Exception as exc:
                print(f"  [skip]  {exc}")

    print(f"\n  Loaded: {g.getVertexCount()} vertices, {g.getEdgeCount()} edges\n")
    return g


# ──────────────────────────────────────────────────────────────────────────────
# Interactive menu  (original interface preserved exactly)
# ──────────────────────────────────────────────────────────────────────────────

def menu() -> None:
    g = DSAGraph()
    option = 0

    while option != 9:
        print("\n=== Graph Menu ===")
        print("1. Add vertex")
        print("2. Delete vertex")
        print("3. Add edge")
        print("4. Delete edge")
        print("5. Display as list")
        print("6. Display as matrix")
        print("7. Breadth First Search")
        print("8. Depth First Search")
        print("9. Quit")

        try:
            option = int(input("Enter option: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if option == 1:
            label = input("Enter vertex label: ")
            try:
                g.addVertex(label)
                print(f"Vertex {label} added!")
            except Exception as exc:
                print(f"Error: {exc}")

        elif option == 2:
            label = input("Enter vertex label to delete: ")
            try:
                g.deleteVertex(label)
                print(f"Vertex {label} deleted!")
            except Exception as exc:
                print(f"Error: {exc}")

        elif option == 3:
            label1 = input("Enter first vertex label: ")
            label2 = input("Enter second vertex label: ")
            try:
                weight = float(input("Enter edge weight (minutes): "))
                g.addEdge(label1, label2, weight)
                print(f"Edge {label1}-{label2} (weight {weight}) added!")
            except Exception as exc:
                print(f"Error: {exc}")

        elif option == 4:
            label1 = input("Enter first vertex label: ")
            label2 = input("Enter second vertex label: ")
            try:
                g.deleteEdge(label1, label2)
                print(f"Edge {label1}-{label2} deleted!")
            except Exception as exc:
                print(f"Error: {exc}")

        elif option == 5:
            g.displayAsList()

        elif option == 6:
            g.displayAsMatrix()

        elif option == 7:
            if g.getVertexCount() == 0:
                print("Graph is empty.")
            else:
                bfs = g.breadthFirstSearch()
                print("BFS traversal edges:")
                temp = bfs.head
                while temp is not None:
                    frm  = temp.value.label
                    temp = temp.next
                    if temp is not None:
                        to   = temp.value.label
                        temp = temp.next
                        print(f"  {frm} → {to}")

        elif option == 8:
            if g.getVertexCount() == 0:
                print("Graph is empty.")
            else:
                dfs = g.depthFirstSearch()
                print("DFS traversal edges:")
                temp = dfs.head
                while temp is not None:
                    frm  = temp.value.label
                    temp = temp.next
                    if temp is not None:
                        to   = temp.value.label
                        temp = temp.next
                        print(f"  {frm} → {to}")

        elif option == 9:
            print("Goodbye!")

        else:
            print("Invalid option, try again!")


# ──────────────────────────────────────────────────────────────────────────────
# Quick smoke-test (runs when executed directly, skips when imported)
# ──────────────────────────────────────────────────────────────────────────────

def _smoke_test() -> None:
    print("\n" + "═" * 55)
    print("  Smoke test — loading Perth road network")
    print("═" * 55)

    g = load_from_csv("perth_road_network.csv")
    g.displayAsList()

    # ── BFS ───────────────────────────────────────────────────────────────────
    print("── BFS from first vertex ─────────────────────────────")
    bfs = g.breadthFirstSearch()
    temp = bfs.head
    while temp is not None:
        frm  = temp.value.label
        temp = temp.next
        if temp is not None:
            to   = temp.value.label
            temp = temp.next
            print(f"  {frm} → {to}")

    # ── DFS ───────────────────────────────────────────────────────────────────
    print("\n── DFS from first vertex ─────────────────────────────")
    dfs = g.depthFirstSearch()
    temp = dfs.head
    while temp is not None:
        frm  = temp.value.label
        temp = temp.next
        if temp is not None:
            to   = temp.value.label
            temp = temp.next
            print(f"  {frm} → {to}")

    # ── add / delete ──────────────────────────────────────────────────────────
    print("\n── Dynamic add / delete test ─────────────────────────")
    g.addVertex("TestNode")
    g.addEdge("TestNode", "CBD", 99.0)
    print(f"  After adding TestNode — vertices: {g.getVertexCount()}, edges: {g.getEdgeCount()}")
    g.deleteEdge("TestNode", "CBD")
    g.deleteVertex("TestNode")
    print(f"  After deleting TestNode — vertices: {g.getVertexCount()}, edges: {g.getEdgeCount()}")

    # ── error handling ────────────────────────────────────────────────────────
    print("\n── Error handling ────────────────────────────────────")
    for label, fn in (
        ("Duplicate vertex", lambda: g.addVertex("CBD")),
        ("Missing vertex",   lambda: g.getVertex("Atlantis")),
        ("Duplicate edge",   lambda: g.addEdge("CBD", "Airport", 25)),
    ):
        try:
            fn()
        except Exception as exc:
            print(f"  [{label}] Caught: {exc}")

    print("\nSmoke test complete.\n")


if __name__ == "__main__":
    _smoke_test()
    # Uncomment the line below to run the interactive menu instead:
    # menu()