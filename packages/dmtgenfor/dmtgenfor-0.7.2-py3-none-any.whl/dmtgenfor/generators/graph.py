# Python program to print topological sorting of a DAG
from collections import defaultdict


class Graph:
    """Class to represent a graph
    https://www.geeksforgeeks.org/python-program-for-topological-sorting/
    """

    def __init__(self, vertices):
        self.vertices = vertices
        self.graph = defaultdict(list)  # dictionary containing adjacency List
        self.V = len(vertices)  # No. of vertices

    # function to add an edge to graph
    def addEdge(self, u, v):
        iu = self.vertices.index(u)
        iv = self.vertices.index(v)
        self.graph[iu].append(iv)

    # A recursive function used by topologicalSort
    def __topological_sort_internal(self, v, visited, stack):

        # Mark the current node as visited.
        visited[v] = True

        # Recur for all the vertices adjacent to this vertex
        for i in self.graph[v]:
            if not visited[i]:
                self.__topological_sort_internal(i, visited, stack)

        # Push current vertex to stack which stores result
        stack.insert(0, v)

    def sort(self):
        """Return topological sort of vertices
        """
        # Mark all the vertices as not visited
        visited = [False]*self.V
        stack = []

        # Call the recursive helper function to store Topological
        # Sort starting from all vertices one by one
        for i in range(self.V):
            if not visited[i]:
                self.__topological_sort_internal(i, visited, stack)

        # Print contents of stack
        vsorted = list()
        for i in stack:
            vsorted.append(self.vertices[i])
        return vsorted


if __name__ == "__main__":
    g = Graph(["a", "b", "c"])
    g.addEdge("b", "a")
    g.addEdge("c", "a")

    print("Following is a Topological Sort of the given graph")
    sorted_vertices = g.sort()
    print(sorted_vertices)
