import linklists
import numpy as np
import os

# EdgeNode stores a neighbour vertex AND the integer weight of the edge
class EdgeNode():
    def __init__(self, vertex, weight):
        self.vertex = vertex
        self.weight = weight  # integer driving time

class GraphVertex():
    def __init__(self, label, value):
        self.label = label
        self.value = value
        self.links = linklists.LinkedList()  # stores EdgeNode objects
        self.visited = False

    def getLabel(self):
        return self.label

    def getValue(self):
        return self.value

    def getAdjacent(self):
        return self.links

    def addEdge(self, vertex, weight):
        self.links.insert_last(EdgeNode(vertex, weight))  # stores EdgeNode, not raw vertex

    def setVisited(self):
        self.visited = True

    def clearVisited(self):
        self.visited = False

    def getVisited(self):
        return self.visited

    def __str__(self):
        return str(self.label)


class Graph():
    def __init__(self):
        self.vertices = linklists.LinkedList()

    # ------------------------------------------------------------------ helpers

    def getVertex(self, label):
        try:
            cur = self.vertices.head
            while cur is not None:
                if cur.value.label == label:
                    return cur.value
                cur = cur.next
            raise Exception("Vertex not found")
        except Exception as e:
            raise Exception(f"Error getting vertex: {e}")

    def hasVertex(self, label):
        try:
            cur = self.vertices.head
            while cur is not None:
                if cur.value.label == label:
                    return True
                cur = cur.next
            return False
        except Exception as e:
            raise Exception(f"Error checking vertex: {e}")

    def getVertexCount(self):
        try:
            count = 0
            cur = self.vertices.head
            while cur is not None:
                count += 1
                cur = cur.next
            return count
        except Exception as e:
            raise Exception(f"Error getting vertex count: {e}")

    def getLabelArray(self):
        """Returns a numpy array of all vertex labels (dtype object for strings)."""
        n = self.getVertexCount()
        labels = np.empty(n, dtype=object)
        cur = self.vertices.head
        i = 0
        while cur is not None:
            labels[i] = cur.value.label
            i += 1
            cur = cur.next
        return labels

    def _labelIndex(self, labels, label):
        """Returns the index of label in a numpy labels array, or -1 if not found."""
        for i in range(len(labels)):
            if labels[i] == label:
                return i
        return -1

    # ------------------------------------------------------------------ mutators

    def addVertex(self, label, value=None):
        try:
            if self.hasVertex(label):
                raise Exception("Vertex already exists")
            new_vertex = GraphVertex(label, value)
            self.vertices.insert_last(new_vertex)
        except Exception as e:
            raise Exception(f"Error adding vertex: {e}")

    def addEdge(self, label1, label2, weight=1):
        """Adds a weighted undirected edge between label1 and label2."""
        try:
            vertex1 = self.getVertex(label1)
            vertex2 = self.getVertex(label2)
            vertex1.addEdge(vertex2, weight)
            vertex2.addEdge(vertex1, weight)
        except Exception as e:
            raise Exception(f"Error adding edge: {e}")

    def deleteVertex(self, label):
        try:
            if not self.hasVertex(label):
                raise Exception("Vertex not found")
            # remove all edges referencing this vertex first
            temp = self.vertices.head
            while temp is not None:
                if temp.value.label != label:
                    self._removeEdgeFromLinks(temp.value, label)
                temp = temp.next
            # remove the vertex node itself
            if self.vertices.head.value.label == label:
                self.vertices.remove_first()
            else:
                prev = self.vertices.head
                cur = self.vertices.head.next
                found = False
                while cur is not None and not found:
                    if cur.value.label == label:
                        prev.next = cur.next
                        found = True
                    else:
                        prev = cur
                        cur = cur.next
        except Exception as e:
            raise Exception(f"Error deleting vertex: {e}")

    def _removeEdgeFromLinks(self, vertex, targetLabel):
        """Removes the EdgeNode pointing to targetLabel from vertex.links."""
        prev = None
        temp = vertex.links.head
        found = False
        while temp is not None and not found:
            if temp.value.vertex.label == targetLabel:
                if prev is None:
                    vertex.links.head = temp.next
                else:
                    prev.next = temp.next
                found = True
            else:
                prev = temp
                temp = temp.next

    def deleteEdge(self, label1, label2):
        try:
            if not self.hasVertex(label1) or not self.hasVertex(label2):
                raise Exception("Vertex not found")
            self._removeEdgeFromLinks(self.getVertex(label1), label2)
            self._removeEdgeFromLinks(self.getVertex(label2), label1)
        except Exception as e:
            raise Exception(f"Error deleting edge: {e}")

    # ------------------------------------------------------------------ display

    def getEdgeCount(self):
        try:
            count = 0
            cur = self.vertices.head
            while cur is not None:
                inner = cur.value.links.head
                while inner is not None:
                    count += 1
                    inner = inner.next
                cur = cur.next
            return count // 2
        except Exception as e:
            raise Exception(f"Error getting edge count: {e}")

    def isAdjacent(self, label1, label2):
        try:
            vertex = self.getVertex(label1)
            temp = vertex.links.head
            while temp is not None:
                if temp.value.vertex.label == label2:
                    return True
                temp = temp.next
            return False
        except Exception as e:
            raise Exception(f"Error checking adjacency: {e}")

    def getEdgeWeight(self, label1, label2):
        """Returns the weight of the edge between label1 and label2, or 0."""
        try:
            vertex = self.getVertex(label1)
            temp = vertex.links.head
            while temp is not None:
                if temp.value.vertex.label == label2:
                    return temp.value.weight
                temp = temp.next
            return 0
        except Exception as e:
            raise Exception(f"Error getting edge weight: {e}")

    def displayAsList(self):
        """Displays graph as adjacency list showing edge weights."""
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            print("\n=== Graph Adjacency List ===")
            temp = self.vertices.head
            while temp is not None:
                vertex = temp.value
                print(f"  {vertex.label} |", end="")
                inner = vertex.links.head
                while inner is not None:
                    print(f" {inner.value.vertex.label}(w={inner.value.weight})", end="")
                    inner = inner.next
                print()
                temp = temp.next
        except Exception as e:
            raise Exception(f"Error displaying list: {e}")

    def displayAsMatrix(self):
        """Displays graph as adjacency matrix showing weights (0 = no edge)."""
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            labels = self.getLabelArray()
            n = len(labels)

            # find longest label for consistent padding
            colWidth = max(len(str(lbl)) for lbl in labels) + 2
            
            # build weight matrix using numpy
            matrix = np.zeros((n, n), dtype=int)
            for i in range(n):
                for j in range(n):
                    if self.isAdjacent(labels[i], labels[j]):
                        matrix[i][j] = self.getEdgeWeight(labels[i], labels[j])


            print("\n=== Graph Adjacency Matrix (weights) ===")

            # header row: blank pad + each label padded to colWidth
            header = " " * (colWidth + 2) + "".join(f"{str(lbl):>{colWidth}}" for lbl in labels)
            print(header)

            # each data row: label padded to colWidth, then values padded to colWidth
            for i in range(n):
                row_str = f"{str(labels[i]):>{colWidth}} ["
                for j in range(n):
                    row_str += f"{matrix[i][j]:>{colWidth}}"
                row_str += " ]"
                print(row_str)

        except Exception as e:
            raise Exception(f"Error displaying matrix: {e}")

    # ------------------------------------------------------------------ BFS

    def breadthFirstSearch(self, sourceLabel):
        """
        Input : source location label
        Output: all reachable locations grouped by level (Level 0, Level 1, ...)
        Uses numpy arrays; no break; no Python lists.
        """
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            if not self.hasVertex(sourceLabel):
                raise Exception("Source vertex not found")

            n = self.getVertexCount()
            labels = self.getLabelArray()

            # numpy arrays for level tracking (-1 = unvisited)
            levelArr = np.full(n, -1, dtype=int)
            srcIdx = self._labelIndex(labels, sourceLabel)
            levelArr[srcIdx] = 0

            queue = linklists.LinkedList()

            # clear visited flags
            temp = self.vertices.head
            while temp is not None:
                temp.value.clearVisited()
                temp = temp.next

            v = self.getVertex(sourceLabel)
            v.setVisited()
            queue.insert_last(v)

            while not queue.isempty():
                v = queue.remove_first()
                vIdx = self._labelIndex(labels, v.label)
                inner = v.links.head
                while inner is not None:
                    w = inner.value.vertex
                    wIdx = self._labelIndex(labels, w.label)
                    if not w.getVisited():
                        w.setVisited()
                        levelArr[wIdx] = levelArr[vIdx] + 1
                        queue.insert_last(w)
                    inner = inner.next

            # print grouped by level
            maxLevel = int(np.max(levelArr[levelArr >= 0]))
            print(f"\nBFS from source: {sourceLabel}")
            print("  Reachable locations by level:")
            for lvl in range(maxLevel + 1):
                idxs = np.where(levelArr == lvl)[0]
                locationNames = np.empty(len(idxs), dtype=object)
                for i in range(len(idxs)):
                    locationNames[i] = labels[idxs[i]]
                print(f"    Level {lvl}: {', '.join(locationNames)}")

            # report unreachable nodes if any
            unreachable = labels[levelArr == -1]
            if len(unreachable) > 0:
                print(f"  Unreachable locations: {', '.join(unreachable)}")

            return levelArr, labels

        except Exception as e:
            raise Exception(f"Error in breadth first search: {e}")

    # ------------------------------------------------------------------ DFS

    def depthFirstSearch(self, sourceLabel):
        """
        Input : source location label
        Output: whether graph contains a cycle; if found, shows locations involved.
        Uses numpy arrays; no break; no Python lists.
        """
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            if not self.hasVertex(sourceLabel):
                raise Exception("Source vertex not found")

            n = self.getVertexCount()
            labels = self.getLabelArray()

            # numpy arrays: parent index (-1 = no parent), visited flags
            parentArr = np.full(n, -1, dtype=int)
            visitedArr = np.zeros(n, dtype=bool)

            # numpy array to store cycle path (max possible length = n)
            cycleArr = np.empty(n, dtype=object)
            cycleLen = 0
            cycleFound = False

            stack = linklists.LinkedList()

            # clear visited flags on vertex objects
            temp = self.vertices.head
            while temp is not None:
                temp.value.clearVisited()
                temp = temp.next

            v = self.getVertex(sourceLabel)
            srcIdx = self._labelIndex(labels, sourceLabel)
            v.setVisited()
            visitedArr[srcIdx] = True
            stack.insert_last(v)

            while not stack.isempty() and not cycleFound:
                inner = v.links.head
                w = None
                found = False
                while inner is not None and not found:
                    neighbour = inner.value.vertex
                    nIdx = self._labelIndex(labels, neighbour.label)
                    vIdx = self._labelIndex(labels, v.label)
                    if not visitedArr[nIdx]:
                        w = neighbour
                        found = True
                    else:
                        # visited neighbour that is not the direct parent = cycle
                        if parentArr[vIdx] != nIdx:
                            cycleFound = True
                            found = True
                            # trace cycle by walking parent chain
                            cur = v
                            cycleLen = 0
                            cycleArr[cycleLen] = neighbour.label
                            cycleLen += 1
                            stillTracing = True
                            while stillTracing:
                                cycleArr[cycleLen] = cur.label
                                cycleLen += 1
                                if cur.label == neighbour.label:
                                    stillTracing = False
                                else:
                                    curIdx = self._labelIndex(labels, cur.label)
                                    pIdx = parentArr[curIdx]
                                    if pIdx == -1:
                                        stillTracing = False
                                    else:
                                        cur = self.getVertex(labels[pIdx])
                            # reverse the filled portion
                            cycleSlice = cycleArr[:cycleLen].copy()
                            cycleArr[:cycleLen] = cycleSlice[::-1]
                        else:
                            inner = inner.next

                if not cycleFound:
                    if w is not None:
                        wIdx = self._labelIndex(labels, w.label)
                        vIdx = self._labelIndex(labels, v.label)
                        parentArr[wIdx] = vIdx
                        w.setVisited()
                        visitedArr[wIdx] = True
                        stack.insert_last(w)
                        v = w
                    else:
                        v = stack.remove_last()

            print(f"\nDFS from source: {sourceLabel}")
            if cycleFound:
                cyclePath = " -> ".join(str(cycleArr[i]) for i in range(cycleLen))
                print(f"  Cycle detected!")
                print(f"  Locations involved: {cyclePath}")
            else:
                print("  No cycle found in graph")

            return cycleFound, cycleArr[:cycleLen]

        except Exception as e:
            raise Exception(f"Error in depth first search: {e}")

    # ------------------------------------------------------------------ Dijkstra

    def dijkstra(self, sourceLabel, destinationLabel):
        """
        Input : source location label, destination location label
        Output: shortest driving time and path from source to destination.
        Uses numpy arrays; no break; no Python lists.
        Reference: Cormen et al. (2022)
        """
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            if not self.hasVertex(sourceLabel):
                raise Exception("Source vertex not found")
            if not self.hasVertex(destinationLabel):
                raise Exception("Destination vertex not found")

            n = self.getVertexCount()
            labels = self.getLabelArray()
            srcIdx = self._labelIndex(labels, sourceLabel)
            dstIdx = self._labelIndex(labels, destinationLabel)

            # numpy arrays for distances and previous node indices
            dist = np.full(n, np.inf)
            prevArr = np.full(n, -1, dtype=int)
            visitedArr = np.zeros(n, dtype=bool)

            dist[srcIdx] = 0

            # process all vertices
            processedCount = 0
            while processedCount < n:
                # find unvisited vertex with smallest distance
                u = -1
                minDist = np.inf
                for i in range(n):
                    if not visitedArr[i] and dist[i] < minDist:
                        minDist = dist[i]
                        u = i

                # no reachable unvisited vertex remains OR destination reached
                done = (u == -1) or (dist[u] == np.inf) or (u == dstIdx)
                if not done:
                    visitedArr[u] = True
                    processedCount += 1

                    vertex = self.getVertex(labels[u])
                    inner = vertex.links.head
                    while inner is not None:
                        w = inner.value.vertex
                        weight = inner.value.weight
                        wIdx = self._labelIndex(labels, w.label)
                        if not visitedArr[wIdx]:
                            alt = dist[u] + weight
                            if alt < dist[wIdx]:
                                dist[wIdx] = alt
                                prevArr[wIdx] = u
                        inner = inner.next
                else:
                    processedCount = n  # exit condition: set to n to stop loop

            # reconstruct path using numpy array
            pathArr = np.empty(n, dtype=object)
            pathLen = 0
            reachable = dist[dstIdx] != np.inf

            if reachable:
                cur = dstIdx
                still = True
                while still:
                    pathArr[pathLen] = labels[cur]
                    pathLen += 1
                    if cur == srcIdx:
                        still = False
                    else:
                        if prevArr[cur] == -1:
                            still = False
                        else:
                            cur = prevArr[cur]
                # reverse filled portion
                pathSlice = pathArr[:pathLen].copy()
                pathArr[:pathLen] = pathSlice[::-1]

            print(f"\nDijkstra Shortest Path: {sourceLabel} -> {destinationLabel}")
            if not reachable:
                print("  No path found between source and destination")
            else:
                pathStr = " -> ".join(str(pathArr[i]) for i in range(pathLen))
                print(f"  Shortest driving time: {int(dist[dstIdx])} mins")
                print(f"  Path: {pathStr}")

            return dist[dstIdx], pathArr[:pathLen]

        except Exception as e:
            raise Exception(f"Error in Dijkstra's algorithm: {e}")


# ------------------------------------------------------------------ menu

def menu(g):
    option = 0
    while option != 10:
        print("\n=== ZipRide Graph Menu ===")
        print("1.  Add vertex")
        print("2.  Delete vertex")
        print("3.  Add edge (with weight)")
        print("4.  Delete edge")
        print("5.  Display as adjacency list")
        print("6.  Display as adjacency matrix")
        print("7.  Breadth First Search (BFS by level)")
        print("8.  Depth First Search (DFS cycle detection)")
        print("9.  Shortest Path (Dijkstra)")
        print("10. Quit")

        try:
            option = int(input("Enter option: "))
        except ValueError:
            print("Invalid input, please enter a number!")
            option = 0
            continue

        if option == 1:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            label = input("Enter vertex label: ")
            try:
                g.addVertex(label)
                print(f"Vertex '{label}' added!")
            except Exception as e:
                print(f"Error: {e}")

        elif option == 2:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            label = input("Enter vertex label to delete: ")
            try:
                g.deleteVertex(label)
                print(f"Vertex '{label}' deleted!")
            except Exception as e:
                print(f"Error: {e}")

        elif option == 3:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            label1 = input("Enter first vertex label: ")
            label2 = input("Enter second vertex label: ")
            try:
                weight = int(input("Enter edge weight (driving time in mins): "))
                g.addEdge(label1, label2, weight)
                print(f"Edge '{label1}' <-> '{label2}' (weight={weight}) added!")
            except ValueError:
                print("Invalid weight, please enter an integer!")
            except Exception as e:
                print(f"Error: {e}")

        elif option == 4:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            label1 = input("Enter first vertex label: ")
            label2 = input("Enter second vertex label: ")
            try:
                g.deleteEdge(label1, label2)
                print(f"Edge '{label1}' <-> '{label2}' deleted!")
            except Exception as e:
                print(f"Error: {e}")

        elif option == 5:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            try:
                g.displayAsList()
            except Exception as e:
                print(f"Error: {e}")

        elif option == 6:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            try:
                g.displayAsMatrix()
            except Exception as e:
                print(f"Error: {e}")

        elif option == 7:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            source = input("Enter source location: ")
            try:
                g.breadthFirstSearch(source)
            except Exception as e:
                print(f"Error: {e}")

        elif option == 8:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            source = input("Enter source location: ")
            try:
                g.depthFirstSearch(source)
            except Exception as e:
                print(f"Error: {e}")

        elif option == 9:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            source = input("Enter source location: ")
            destination = input("Enter destination location: ")
            try:
                g.dijkstra(source, destination)
            except Exception as e:
                print(f"Error: {e}")

        elif option == 10:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            print("Goodbye!")

        else:
            print("Invalid option, try again!")