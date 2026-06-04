# Description: Graph structure for storing the locations and driving times between them
# Author: Dylan Baker 22368201
# Date: 30/05/2026

import linklists
import numpy as np
import os

# EdgeNode stores a neighbour vertex AND the integer weight of the edge
class EdgeNode():
    def __init__(self, vertex, weight):
        self.vertex = vertex
        self.weight = weight  # integer driving time

# GraphVertex stores the label, value, and linked list of EdgeNodes for a vertex
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


    def getVertex(self, label):
        # traverses linked list to find vertex with matching label. returns vertex object if found, raises exception if not
        try:
            current = self.vertices.head # traverse linked list to find vertex with matching label
            while current is not None:
                if current.value.label == label: # if found, return the vertex object
                    return current.value
                
                current = current.next 
                
            raise Exception("Vertex not found") 
        
        except Exception as e: # if not found after traversing whole list, raise exception
            raise Exception(f"Error getting vertex: {e}")


    def hasVertex(self, label):
        # traverses linked list to find vertex with matching label. returns True if found, False if not
        try:
            current = self.vertices.head # traverse linked list to find vertex with matching label
            
            while current is not None:
                if current.value.label == label: # if found, return True
                    return True
                
                current = current.next
                
            return False
        
        except Exception as e: # if not found after traversing whole list, raise exception
            raise Exception(f"Error checking vertex: {e}")

    def getVertexCount(self):
        # traverses linked list of vertices and counts them; returns count
        try:
            count = 0
            current = self.vertices.head
            
            while current is not None:
                count += 1
                current = current.next
                
            return count
        
        except Exception as e:
            raise Exception(f"Error getting vertex count: {e}")

    def getLabelArray(self):
        #Returns a numpy array of all vertex labels
        vertexCount = self.getVertexCount()
        labels = np.empty(vertexCount, dtype=object)
        
        current = self.vertices.head
        i = 0
        
        while current is not None: # traverse linked list and fill numpy array with vertex labels
            labels[i] = current.value.label
            i += 1
            current = current.next
            
        return labels

    def _labelIndex(self, labels, label):
        # Returns the index of label in a numpy labels array, or -1 if not found.
        for i in range(len(labels)):
            if labels[i] == label:
                return i
            
        return -1


    def addVertex(self, label, value=None):
        # Adds a new vertex to the graph. Raises exception if vertex with same label already exists.
        try:
            if self.hasVertex(label):
                raise Exception("Vertex already exists")
            
            new_vertex = GraphVertex(label, value)
            self.vertices.insert_last(new_vertex)
            
        except Exception as e:
            raise Exception(f"Error adding vertex: {e}")

    def addEdge(self, label1, label2, weight=1):
        #Adds a weighted undirected edge between label1 and label2.
        try:
            vertex1 = self.getVertex(label1)
            vertex2 = self.getVertex(label2)
            vertex1.addEdge(vertex2, weight)
            vertex2.addEdge(vertex1, weight)
            
        except Exception as e:
            raise Exception(f"Error adding edge: {e}")

    def deleteVertex(self, label):
        # Removes vertex with given label and all edges referencing it. Raises exception if vertex not found.
        try:
            if not self.hasVertex(label):
                raise Exception("Vertex not found")
            
            # remove all edges referencing this vertex first
            temporary = self.vertices.head
            
            while temporary is not None:
                if temporary.value.label != label:
                    self._removeEdgeFromLinks(temporary.value, label)
                temporary = temporary.next
                
            # remove the vertex node itself
            if self.vertices.head.value.label == label:
                self.vertices.remove_first()
                
            else:
                previous = self.vertices.head
                current = self.vertices.head.next
                found = False
                
                while current is not None and not found: # traverse linked list of vertices until you find the one to delete
                    if current.value.label == label:
                        previous.next = current.next
                        found = True
                        
                    else: # if not found, keep traversing
                        previous = current
                        current = current.next
                        
        except Exception as e:
            raise Exception(f"Error deleting vertex: {e}")

    def _removeEdgeFromLinks(self, vertex, targetLabel):
        # Removes the EdgeNode pointing to targetLabel from vertex.links linked list
        previous = None
        temporary = vertex.links.head
        found = False
        
        while temporary is not None and not found: # traverse linked list of edges until find the one pointing to targetLabel
            if temporary.value.vertex.label == targetLabel: # if found, remove it by updating previous.next to skip temporary
                if previous is None:
                    vertex.links.head = temporary.next
                    
                else:
                    previous.next = temporary.next
                    
                found = True
                
            else: # if not found, keep traversing
                previous = temporary
                temporary = temporary.next

    def deleteEdge(self, label1, label2):
        # Removes the undirected edge between label1 and label2. Raises exception if either vertex not found
        try:
            if not self.hasVertex(label1) or not self.hasVertex(label2):
                raise Exception("Vertex not found")
            self._removeEdgeFromLinks(self.getVertex(label1), label2)
            self._removeEdgeFromLinks(self.getVertex(label2), label1)
            
        except Exception as e:
            raise Exception(f"Error deleting edge: {e}")


    def getEdgeCount(self):
        # traverse vertices and counts all edges by adding the lengths of their lists
        # divides count by 2 for undirected edges also for edges stored twice
        try:
            count = 0
            current = self.vertices.head
            
            while current is not None:
                inner = current.value.links.head

                while inner is not None:
                    count += 1
                    inner = inner.next

                current = current.next

            count = count // 2
            return count
                
            return count
        
        except Exception as e:
            raise Exception(f"Error getting edge count: {e}")

    def isAdjacent(self, label1, label2):
        # Returns True if there is an edge between label1 and label2, and False if not
        try:
            vertex = self.getVertex(label1)
            temporary = vertex.links.head
            
            while temporary is not None:
                if temporary.value.vertex.label == label2:
                    return True
                
                temporary = temporary.next
            return False
        
        except Exception as e: # Raises exception if either vertex not found
            raise Exception(f"Error checking adjacency: {e}")

    def getEdgeWeight(self, label1, label2):
        # Returns the weight of the edge between label1 and label2 if it exists, otherwise 0
        try:
            vertex = self.getVertex(label1)
            temporary = vertex.links.head
            
            while temporary is not None:
                if temporary.value.vertex.label == label2:
                    return temporary.value.weight
                
                temporary = temporary.next
                
            return 0
        
        except Exception as e: # Raises exception if either vertex not found
            raise Exception(f"Error getting edge weight: {e}")

    def displayAsList(self):
        # WARNING - THIS METHOD CONTAINS CODE FROM PAST WORKSHOPS - Workshop 7: Graphs
        # Displays graph as adjacency list showing edge weights
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            
            print("=== Graph Adjacency List ===")
            temporary = self.vertices.head
            
            while temporary is not None:
                vertex = temporary.value
                print(f"{vertex.label} |", end="")
                inner = vertex.links.head
                
                while inner is not None:
                    print(f"{inner.value.vertex.label}(weight={inner.value.weight})", end="") # print neighbour label and weight
                    inner = inner.next
                print()
                temporary = temporary.next
                
        except Exception as e: # Raises exception if graph is empty or error occurs during traversal
            raise Exception(f"Error displaying list: {e}")

    def displayAsMatrix(self):
        # WARNING - THIS METHOD CONTAINS CODE FROM PAST WORKSHOPS - Workshop 7: Graphs
        # Displays graph as adjacency matrix showing weights, 0 if no edge exits
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            
            labels = self.getLabelArray()
            vertexCount = len(labels)

            # Find longest label for consistent padding
            colWidth = max(len(str(lbl)) for lbl in labels) + 2
            
            # Build weight matrix using numpy
            matrix = np.zeros((vertexCount, vertexCount), dtype=int)
            
            for i in range(vertexCount):
                for j in range(vertexCount):
                    if self.isAdjacent(labels[i], labels[j]):
                        matrix[i][j] = self.getEdgeWeight(labels[i], labels[j]) # fill weight if edge exists, otherwise 0 remains


            print("=== Graph Adjacency Matrix (weights) ===")

            # header row: blank pad + each label padded to colWidth
            leadingSpace = " " * (colWidth + 2)
            headerParts = np.empty(len(labels), dtype=object)
            
            for i in range(len(labels)):
                headerParts[i] = f"{str(labels[i]):>{colWidth}}" # pad each label to colWidth

            header = leadingSpace + "".join(headerParts)
            print(header)

            # each data row: label padded to colWidth, then values padded to colWidth
            for i in range(vertexCount):
                row_str = f"{str(labels[i]):>{colWidth}} ["
                
                for j in range(vertexCount):
                    row_str += f"{matrix[i][j]:>{colWidth}}"
                    
                row_str += " ]"
                print(row_str)

        except Exception as e:
            raise Exception(f"Error displaying matrix: {e}")


    def breadthFirstSearch(self, sourceLabel):
        # WARNING - THIS METHOD CONTAINS CODE FROM PAST WORKSHOPS - Workshop 7: Graphs
        # Performs a breadth first search starting from the source vertex
        #   using a queue to explore neighbors level by level
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            
            if not self.hasVertex(sourceLabel):
                raise Exception("Source vertex not found")

            vertexCount = self.getVertexCount()
            labels = self.getLabelArray()

            # store level of each vertex in numpy array -1 means not reached yet and at end unreachable
            levelArr = np.full(vertexCount, -1, dtype=int)
            sourceIndex = self._labelIndex(labels, sourceLabel)
            levelArr[sourceIndex] = 0
            queue = linklists.LinkedList()
            temporary = self.vertices.head
            
            while temporary is not None: # clear visited tagging on vertex objects before starting the search
                temporary.value.clearVisited()
                temporary = temporary.next

            vertex = self.getVertex(sourceLabel) # mark source vertex as visited and start the search
            vertex.setVisited()
            queue.insert_last(vertex)

            # loop until queue is empty and at each step remove first vertex and add its unvisited neighbours to the end of the queue
            while not queue.isempty():
                vertex = queue.remove_first()
                vertexIndex = self._labelIndex(labels, vertex.label)
                inner = vertex.links.head
                
                while inner is not None: # for each neighbour weight of vertex, if weight is unvisited, mark it visited, set its level to be one more than vertex's level, and add it to the end of the queue
                    weight = inner.value.vertex
                    weightIndex = self._labelIndex(labels, weight.label)
                    
                    if not weight.getVisited():
                        weight.setVisited()
                        levelArr[weightIndex] = levelArr[vertexIndex] + 1
                        queue.insert_last(weight)
                    inner = inner.next


            # print grouped by level
            maxLevel = int(np.max(levelArr[levelArr >= 0]))
            print(f"BFS from source: {sourceLabel}")
            print("Reachable locations by level:")
            
            
            for lvl in range(maxLevel + 1): # for each level from 0 to maxLevel, find the nuimbers of vertices at that level and print their labels
                idxs = np.where(levelArr == lvl)[0]
                locationNames = np.empty(len(idxs), dtype=object)
                
                for i in range(len(idxs)): # fill locationNames array with labels of vertices at this level using the idxs to index into labels array
                    locationNames[i] = labels[idxs[i]]
                print(f"Level {lvl}: {', '.join(locationNames)}")

            # report unreachable nodes if any
            unreachable = labels[levelArr == -1]
            
            if len(unreachable) > 0:
                print(f"Unreachable locations: {', '.join(unreachable)}")

            return levelArr, labels

        except Exception as e:
            raise Exception(f"Error in breadth first search: {e}")


    def depthFirstSearch(self, sourceLabel):
        # WARNING - THIS METHOD CONTAINS CODE FROM PAST WORKSHOPS - Workshop 7: Graphs
        # Performs a depth first search starting from the source vertex
        #   using a stack to explore neighbors
        
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            
            if not self.hasVertex(sourceLabel):
                raise Exception("Source vertex not found")

            vertexCount = self.getVertexCount()
            labels = self.getLabelArray()

            # numpy arrays: parent index -1 = no parent,  othar is visited flags
            parentArr = np.full(vertexCount, -1, dtype=int)
            visitedArr = np.zeros(vertexCount, dtype=bool)

            # numpy array to store cycle path with max  length = vertexCount
            cycleArr = np.empty(vertexCount, dtype=object)
            cycleLen = 0
            cycleFound = False

            stack = linklists.LinkedList() # stack for DFS, store vertex objects in stack

            # clear visited flags on vertex objects
            temporary = self.vertices.head
            
            while temporary is not None: # traverse linked list of vertices and clear visited flags before starting the search
                temporary.value.clearVisited()
                temporary = temporary.next

            # initiate DFS by marking source vertex visited, pushing it to stack, and setting its parent to -1 in parentArr
            vertex = self.getVertex(sourceLabel)
            sourceIndex = self._labelIndex(labels, sourceLabel)
            vertex.setVisited()
            visitedArr[sourceIndex] = True
            stack.insert_last(vertex)

            # loop until stack is empty or cycle found. at each step, 
            # look for an unvisited neighbour weight of the vertex vertex on top of the stack. 
            # if found, mark weight visited, set its parent to be vertex in parentArr, and push weight to stack. 
            # if no unvisited neighbour is found, pop vertex from stack. 
            # if an already visited neighbour is found that is not the parent of vertex, then a cycle is detected. 
            # trace back the cycle path using parentArr and store it in cycleArr.
            
            while not stack.isempty() and not cycleFound:
                inner = vertex.links.head
                weight = None
                found = False
                
                while inner is not None and not found: 
                    # look for unvisited neighbour weight of vertex vertex on top of stack by traversing linked list of edges for vertex
                    neighbour = inner.value.vertex
                    nIdx = self._labelIndex(labels, neighbour.label)
                    vertexIndex = self._labelIndex(labels, vertex.label)
                    
                    if not visitedArr[nIdx]:
                        weight = neighbour
                        found = True
                        
                    else:
                        # visited neighbour that is not the direct parent = cycle
                        if parentArr[vertexIndex] != nIdx:
                            cycleFound = True
                            found = True
                            # trace cycle by walking parent chain
                            current = vertex
                            cycleLen = 0
                            cycleArr[cycleLen] = neighbour.label
                            cycleLen += 1
                            stillTracing = True
                            
                            while stillTracing:
                                # add current vertex to cycleArr and check if reached the neighbour that closed the cycle
                                cycleArr[cycleLen] = current.label
                                cycleLen += 1
                                if current.label == neighbour.label:
                                    stillTracing = False
                                    
                                else:
                                    # find parent of current vertex using parentArr until reach the neighbour that closed the cycle, filling cycleArr
                                    curIdx = self._labelIndex(labels, current.label)
                                    pIdx = parentArr[curIdx]
                                    if pIdx == -1:
                                        stillTracing = False
                                        
                                    else:
                                        current = self.getVertex(labels[pIdx])
                                        
                            # reverse the filled portion
                            cycleSlice = cycleArr[:cycleLen].copy() # copy to temporary array before reversing to avoid overwriting during reverse
                            cycleArr[:cycleLen] = cycleSlice[::-1] # reverse the filled portion of cycleArr to get correct order from neighbour that closed the cycle back to itself
                            
                        else:
                            inner = inner.next

                if not cycleFound:
                    # if found an unvisited neighbour weight, mark weight visited and set its parent to be vertex in parentArr, and push weight to stack
                    if weight is not None:
                        weightIndex = self._labelIndex(labels, weight.label)
                        vertexIndex = self._labelIndex(labels, vertex.label)
                        parentArr[weightIndex] = vertexIndex
                        weight.setVisited()
                        visitedArr[weightIndex] = True
                        stack.insert_last(weight)
                        vertex = weight
                        
                    else:
                        vertex = stack.remove_last()

            print(f"DFS from source: {sourceLabel}")
            
            if cycleFound:
                # if a cycle is found, print the cycle path by joining the labels in cycleArr up to cycleLen
                cyclePath = " -> ".join(str(cycleArr[i]) for i in range(cycleLen))
                print(f"Cycle detected!")
                print(f"Locations involved: {cyclePath}")
                
            else:
                print("No cycle found in graph")

            return cycleFound, cycleArr[:cycleLen]

        except Exception as e:
            raise Exception(f"Error in depth first search: {e}")


    def dijkstra(self, sourceLabel, destinationLabel):
        # WARNING - THIS METHOD CONTAINS CODE FROM PAST WORKSHOPS - Workshop 7: Graphs
        # Performs Dijkstra's algorithm starting from the source vertex
        #   to find the shortest path to the destination vertex
        #Reference: Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022).
        #           Introduction to algorithms. MIT press.
        #
        try:
            if self.vertices.isempty():
                raise Exception("Graph is empty")
            
            if not self.hasVertex(sourceLabel):
                raise Exception("Source vertex not found")
            
            if not self.hasVertex(destinationLabel):
                raise Exception("Destination vertex not found")

            vertexCount = self.getVertexCount()
            labels = self.getLabelArray()
            sourceIndex = self._labelIndex(labels, sourceLabel)
            destinationIndex = self._labelIndex(labels, destinationLabel)

            # distances and previous node indices
            dist = np.full(vertexCount, np.inf)
            previousArr = np.full(vertexCount, -1, dtype=int)
            visitedArr = np.zeros(vertexCount, dtype=bool)

            dist[sourceIndex] = 0 # distance to source is 0

            # process all vertices
            processedCount = 0
            
            while processedCount < vertexCount:
                # find unvisited vertex with smallest distance
                u = -1
                minDist = np.inf
                
                for i in range(vertexCount):
                    if not visitedArr[i] and dist[i] < minDist:
                        minDist = dist[i]
                        u = i


                # no reachable unvisited vertex remains
                done = (u == -1) or (dist[u] == np.inf)

                if not done:
                    # mark u visited
                    visitedArr[u] = True
                    processedCount += 1

                    # destination reached, stop algorithm
                    if u == destinationIndex:
                        processedCount = vertexCount

                    else:
                        # update distances to neighbours
                        vertex = self.getVertex(labels[u])
                        inner = vertex.links.head

                        while inner is not None:
                            neighbour = inner.value.vertex
                            edgeWeight = inner.value.weight

                            neighbourIndex = self._labelIndex(labels, neighbour.label)

                            if not visitedArr[neighbourIndex]:
                                alt = dist[u] + edgeWeight

                                if alt < dist[neighbourIndex]:
                                    dist[neighbourIndex] = alt
                                    previousArr[neighbourIndex] = u

                            inner = inner.next

                else:
                    processedCount = vertexCount

            # reconstruct path using numpy array
            pathArray = np.empty(vertexCount, dtype=object)
            pathLength = 0
            reachable = dist[destinationIndex] != np.inf

            if reachable:
                # if destination is reachable, reconstruct path by walking backwards 
                # destination to source using previousArr and filling pathArray, then reverse the filled portion of pathArray
                current = destinationIndex
                still = True
                
                while still:
                    pathArray[pathLength] = labels[current]
                    pathLength += 1
                    
                    if current == sourceIndex:
                        still = False
                        
                    else:
                        if previousArr[current] == -1:
                            still = False
                            
                        else:
                            current = previousArr[current]
                            
                # reverse filled portion 
                pathSlice = pathArray[:pathLength].copy() # copy to temporary array before reversing to avoid overwriting during reverse
                pathArray[:pathLength] = pathSlice[::-1] # reverse the filled portion of pathArray to get correct order from source to destination

            print(f"Shortest Path {sourceLabel} -> {destinationLabel}")
            
            if not reachable:
                print("No path found between source and destination")
                
            else:
                # if reachable, print the shortest driving time and the path by joining the labels in pathArray up to pathLength
                pathStr = " -> ".join(str(pathArray[i]) for i in range(pathLength))
                print(f"  Shortest driving time: {int(dist[destinationIndex])} mins")
                print(f"  Path: {pathStr}")

            return dist[destinationIndex], pathArray[:pathLength]

        except Exception as e:
            raise Exception(f"Error in Dijkstra's algorithm: {e}")


def menu(graphData):
    option = 0
    while option != 10:
        print("=== Graph Menu ===")
        print("1 Add a vertex")
        print("2 Delete a vertex")
        print("3 Add an edge")
        print("4 Delete an edge")
        print("5 Adjacency list")
        print("6 Adjacency matrix")
        print("7 BFS")
        print("8 DFS")
        print("9 Dijkstra")
        print("10 Quit")

        try:
            option = int(input("Enter choice: "))
            
        except ValueError:
            print("Invalid input, please enter a number!")
            option = 0
            continue

        if option == 1:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            label = input("Enter vertex label: ")
            
            try:
                graphData.addVertex(label)
                print(f"Vertex '{label}' added!")
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 2:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            label = input("Enter vertex label to delete: ")
            
            try:
                graphData.deleteVertex(label)
                print(f"Vertex '{label}' deleted!")
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 3:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            label1 = input("Enter first vertex label: ")
            label2 = input("Enter second vertex label: ")
            
            try:
                weight = int(input("Enter edge weight (driving time in mins): "))
                graphData.addEdge(label1, label2, weight)
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
                graphData.deleteEdge(label1, label2)
                print(f"Edge '{label1}' <-> '{label2}' deleted!")
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 5:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            try:
                graphData.displayAsList()
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 6:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            try:
                graphData.displayAsMatrix()
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 7:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            source = input("Enter source location: ")
            
            try:
                graphData.breadthFirstSearch(source)
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 8:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            source = input("Enter source location: ")
            
            try:
                graphData.depthFirstSearch(source)
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 9:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            source = input("Enter source location: ")
            destination = input("Enter destination location: ")
            
            try:
                graphData.dijkstra(source, destination)
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 10:
            os.system('cls' if os.name == 'nt' else 'clear') # clears screen if with win or linux/mac terminal command
            print("Exiting")

        else:
            print("Invalid option, try again!")
