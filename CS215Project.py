import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import psutil

try:
    from networkx.drawing.nx_agraph import graphviz_layout
except ImportError:
    raise ImportError("You need to install pygraphviz or pydot for tree layout support.")

# Create city graph
city = nx.DiGraph()

# Label the nodes
nodes = {
    "A": "Intersection 1", "B": "Intersection 2", "C": "Intersection 3",
    "D": "Intersection 4", "E": "Intersection 5", "F": "Intersection 6"
}

for node in nodes:
    city.add_node(node, label=nodes[node])

# Define the edges of the network
edges = [
    ("A", "B", {"distance": 5, "speed_limit": 50, "traffic": 1.0}),
    ("A", "C", {"distance": 4, "speed_limit": 50, "traffic": 1.2}),
    ("B", "D", {"distance": 7, "speed_limit": 50, "traffic": 1.5}),
    ("C", "E", {"distance": 6, "speed_limit": 50, "traffic": 2.0}),
    ("D", "F", {"distance": 8, "speed_limit": 50, "traffic": 1.0}),
    ("E", "F", {"distance": 5, "speed_limit": 50, "traffic": 1.3}),
]

city.add_edges_from([(u, v, attr) for u, v, attr in edges])

# Calculate travel time
def calculate_travel_time(distance, speed_limit, traffic):
    return (distance / speed_limit) * 50 * traffic

# Update traffic conditions
def update_traffic():
    for u, v in city.edges:
        city[u][v]['traffic'] = round(random.uniform(1.0, 3.0), 2)

# Implement BFS
def bfs_traversal(graph, start_node):
    visited = set()
    queue = [start_node]
    traversal_order = []
    explored_edges = []

    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            traversal_order.append(node)
            for neighbor in graph.neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)
                    explored_edges.append((node, neighbor))  # Store explored edge
    
    return traversal_order, explored_edges

# Metrics
start_time = time.time()
memory_before = psutil.Process().memory_info().rss / (1024 * 1024)  # In MB

# Start BFS
start_node = "A"
bfs_result, bfs_edges = bfs_traversal(city, start_node)

# Metrics
execution_time = time.time() - start_time
memory_after = psutil.Process().memory_info().rss / (1024 * 1024)  # In MB
memory_usage = memory_after - memory_before

# Display the network
pos = graphviz_layout(city, prog = "dot")
fig, ax = plt.subplots(figsize = (8, 6))
ax.set_title("BFS Traversal Visualization with Travel Times")

# Draw graph with all nodes in blue
nx.draw(city, pos, with_labels = True, labels = nodes, node_color = 'lightblue',
        edge_color = 'gray', node_size = 3000, font_size = 10, arrows = True, ax = ax)

# Draw edge labels (travel times)
edge_labels = {(u, v): f"{calculate_travel_time(attr['distance'], attr['speed_limit'], attr['traffic']):.1f} min"
               for u, v, attr in city.edges(data = True)}
nx.draw_networkx_edge_labels(city, pos, edge_labels = edge_labels, ax = ax, font_size = 9)

# Animate BFS step by step
for i, (node, edge) in enumerate(zip(bfs_result, bfs_edges)):
    plt.pause(0.5)
    nx.draw_networkx_nodes(city, pos, nodelist = [node], node_color = 'red', node_size = 3000, ax = ax)
    nx.draw_networkx_edges(city, pos, edgelist = [edge], edge_color = 'red', width = 2.5, ax = ax)
    plt.draw()

# Show final graph
plt.show()

# Output BFS traversal order
print("\n=== BFS Traversal Order ===")
print(" -> ".join(bfs_result))

# Output performance metrics
print("\n=== Performance Metrics ===")
print(f"Runtime: {execution_time:.6f} seconds")
print(f"Memory Usage: {memory_usage:.3f} MB")
print(f"Solution Quality: ???")
print(f"Convergence Rate: ???")
