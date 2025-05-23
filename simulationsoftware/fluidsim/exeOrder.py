from .models import Connections,functionBlockData
def get_execution_order(net_id):
    connections = Connections.objects.filter(network_id = net_id).order_by("pk")
    print(connections)
    if(len(connections) != 0):  
        graph = {}
        for connection in connections:
            source = connection.source
            destination = connection.destination
            if(destination!=None):
                if source not in graph:
                    graph[source] = []
                graph[source].append(destination)
        return topological_sort(graph)
    else:
        if(len(functionBlockData.objects.filter(network_id = net_id)) == 1):
            return functionBlockData.objects.filter(network_id = net_id)
        else:
            return []
        
# def  topological_sort(graph):
#     print(graph)
#     visited = set()  # Nodes that are fully processed
#     processing = set()
#     stack = []
#     cycles = []
#     def visit(node):
        
#         if node in processing:
#             cycle_index = stack.index(node)
#             cycles.append(stack[cycle_index:])
#             return
         
#         if node in visited:
#             return
        
#         processing.add(node)  # Mark node as being processed
#         visited.add(node) 
#         # print(visited) # Mark as fully processed
#         stack.append(node)

#         for neighbor in graph.get(node, []):
#             visit(neighbor)

#         processing.remove(node)  # Remove from processing set
#         stack.pop()
    
#     for node in graph:
#         if(node not in visited):
#             visit(node)
#     print(visited)
#     return visited,cycles  # Reverse to get execution order

def topological_sort(graph):
    visited = set()  # Nodes that are fully processed
    path = []
    stack = []
    cycles = set()

    def visit(node):

        if node in path:
            cycles.add(node)        
            return 
        
        if node not in visited:
            path.append(node)  # Mark node as being processed
            for neighbor in graph.get(node, []):
                visit(neighbor)

            path.pop()
            visited.add(node)   # Remove from processing set # Mark as fully processed
            stack.append(node)
            return
    
    for node in graph:
        visit(node)

    # cycles = directed_graph(stack[::-1],graph)
    
    return stack[::-1],cycles  # Reverse to get execution order
    
# s
# def  topological_sort(graph):
#     print(graph)
#     visited = set()  # Nodes that are fully processed
#     processing = set()
#     path = []
#     stack = []
#     cycles = []

#     def visit(node):
#         if node in processing:
#             raise ValueError(f"Circular dependency detected at node {node}")
#         if node not in visited:
#             processing.add(node)  # Mark node as being processed
#             for neighbor in graph.get(node, []):
#                 visit(neighbor)
#             processing.remove(node)  # Remove from processing set
#             visited.add(node)  # Mark as fully processed
#             stack.append(node)
    
#     for node in graph:
#         visit(node)
    
#     return stack[::-1]  # Reverse to get execution order