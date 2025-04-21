import networkx as nx
import matplotlib.pyplot as plt
import random
import csv
import os
from collections import deque

# Set up graphs
city = nx.DiGraph()
nodes = {
    "A": "Intersection 1", "B": "Intersection 2", "C": "Intersection 3",
    "D": "Intersection 4", "E": "Intersection 5", "F": "Intersection 6"
}
for node in nodes:
    city.add_node(node, label = nodes[node])

edges = [
    ("A", "B"), ("A", "C"), ("B", "D"),
    ("C", "E"), ("D", "F"), ("E", "F")
]

# Randomization for edges
for u, v in edges:
    city.add_edge(u, v, 
                  distance = random.randint(3, 10),
                  speed_limit = random.choice(range(25, 71, 5)),
                  traffic = round(random.uniform(1.0, 3.0), 2))

# Functions
def calculate_travel_time(distance, speed_limit, traffic):
    return (distance / speed_limit) * 50 * traffic

def bfs(graph, start):
    visited, queue, order, edges = set(), [start], [], []
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            order.append(node)
            for neighbor in graph.neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)
                    edges.append((node, neighbor))
    return order, edges

def extract_bfs_path(start, goal, edges):
    parent_map = {v: u for u, v in edges}
    path, current = [goal], goal
    while current != start:
        if current not in parent_map:
            return None
        current = parent_map[current]
        path.append(current)
    return list(reversed(path))

def total_travel_time(graph, path):
    return sum(
        calculate_travel_time(graph[u][v]['distance'], graph[u][v]['speed_limit'], graph[u][v]['traffic'])
        for u, v in zip(path[:-1], path[1:])
    ) if path and len(path) > 1 else float('inf')

def tabu_search(graph, start, goal, max_iterations=100, tabu_size=5):
    def travel_time(path):
        return total_travel_time(graph, path)
    def get_neighbors(path):
        return [path + [nbr] for nbr in graph.neighbors(path[-1]) if nbr not in path]

    current_solution = [start]
    best_solution, best_cost = None, float("inf")
    tabu_list = deque(maxlen = tabu_size)
    tabu_history = []

    for _ in range(max_iterations):
        neighbors = [n for n in get_neighbors(current_solution) if n not in tabu_list]
        if not neighbors:
            break
        neighbors.sort(key = travel_time)
        current_solution = neighbors[0]
        tabu_list.append(list(current_solution))
        tabu_history.append(list(current_solution))
        current_cost = travel_time(current_solution)
        if current_solution[-1] == goal and current_cost < best_cost:
            best_solution, best_cost = list(current_solution), current_cost

    return best_solution, best_cost, tabu_history

# Main execution
bfs_order, bfs_edges = bfs(city, "A")
bfs_path = extract_bfs_path("A", "F", bfs_edges)
bfs_time = total_travel_time(city, bfs_path)
tabu_path, tabu_time, tabu_list_log = tabu_search(city, "A", "F")

# Visualize graphs
pos = nx.spring_layout(city, seed = 42)
edge_colors = ['red' if a['traffic'] >= 2.0 else 'orange' if a['traffic'] >= 1.5 else 'yellow'
               for _, _, a in city.edges(data = True)]

edge_labels = {}
for u, v, attr in city.edges(data=True):
    base = (attr['distance'] / attr['speed_limit']) * 50
    total = calculate_travel_time(attr['distance'], attr['speed_limit'], attr['traffic'])
    edge_labels[(u, v)] = (
        f"Time: {total:.1f} min\n"
        f"Speed: {attr['speed_limit']} mph\n"
        f"Traffic: (+{total - base:.1f} min)"
    )

fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (18, 8), facecolor='white')
fig.suptitle("City Network Comparison: Breadth First Search (BFS) vs Tabu Search (TS)", fontsize = 18, fontweight = 'bold')
y_pos = 0.91
fig.text(0.30, y_pos, "High Traffic", color = 'red', fontsize = 10, weight = 'bold')
fig.text(0.45, y_pos, "Medium Traffic", color = 'orange', fontsize = 11, weight = 'bold')
fig.text(0.60, y_pos, "Low Traffic", color = 'gold', fontsize = 11, weight = 'bold')

for ax, path, color, label in [(ax1, bfs_path, 'dodgerblue', "BFS Path (Blue Line)"),
                               (ax2, tabu_path, 'forestgreen', "TS Path (Green Dashed Line)")]:
    nx.draw(city, pos, ax = ax, with_labels = True, labels = nodes, node_color = 'lightsteelblue',
            node_size = 2000, font_size = 10, edge_color = edge_colors, width = 2, arrows = True)

    if path:
        edge_list = list(zip(path, path[1:]))
        style = 'solid' if color == 'dodgerblue' else 'dashed'
        nx.draw_networkx_edges(city, pos, edgelist = edge_list, edge_color = color, style = style,
                               width = 4, ax = ax, arrows = True, connectionstyle = "arc3,rad=0.05",
                               min_source_margin = 12, min_target_margin = 12)
        nx.draw_networkx_nodes(city, pos, nodelist = path, node_color = color, ax = ax)
        ax.text(pos[path[0]][0], pos[path[0]][1] - 0.12, "Start", ha = 'center', fontsize = 9)
        ax.text(pos[path[-1]][0], pos[path[-1]][1] + 0.12, "End", ha = 'center', fontsize = 9)

    for (u, v), label_text in edge_labels.items():
        x, y = (pos[u][0]+pos[v][0])/2, (pos[u][1]+pos[v][1])/2
        ax.text(x, y, label_text, fontsize = 8, ha = 'center', va = 'center',
                bbox = dict(facecolor = 'white', alpha = 0.8, edgecolor = 'none'))

    ax.set_title(label, fontsize=14)
    ax.axis('off')

# Display Tabu list beside the Tabu Search graph
if tabu_list_log:
    tabu_str = "\n".join(" → ".join(p) for p in tabu_list_log[-6:])
    ax2.text(1.05, 0.5, "Recent Tabu List:\n" + tabu_str, transform = ax2.transAxes,
             fontsize = 9, verticalalignment = 'center', bbox = dict(facecolor = 'white', alpha = 0.9))

plt.tight_layout(rect = [0, 0.03, 1, 0.93])
plt.show()

#  Console Output
print()
print("    **Path Comparison**    ") 
outputFile = r'C:\Users\rahso\OneDrive\Documents\CS 215 Project\output.csv'

# Store runtimes
bfs_times = []
tabu_times = []

if os.path.isfile(outputFile):
    with open(outputFile, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) >= 3 and row[0] == "BFS" and row[2] != "N/A":
                bfs_times.append(float(row[2]))
            elif len(row) >= 3 and row[0] == "Tabu" and row[2] != "N/A":
                tabu_times.append(float(row[2]))

# Append to end of file
with open(outputFile, 'a', newline='') as file:
    writer = csv.writer(file)

    if not os.path.isfile(outputFile) or os.path.getsize(outputFile) == 0:
        writer.writerow(["Algorithm", "Path", "Time (mins)", "Average Time (mins)"])

    if bfs_path:
        bfs_path_str = " -> ".join(bfs_path)
        print("BFS Path:   " + bfs_path_str)
        print("BFS Time:   {:.2f} mins".format(bfs_time))
        bfs_times.append(bfs_time)
        aveBFS = sum(bfs_times) / len(bfs_times)
        writer.writerow(["BFS", bfs_path_str, "{:.2f}".format(bfs_time), "{:.2f}".format(aveBFS)])
        
    else:
        print("BFS Path:   No path to F")
        writer.writerow(["BFS", "No path to F", "N/A", "N/A"])

    if tabu_path:
        tabu_path_str = " -> ".join(tabu_path)
        print("Tabu Path:  " + tabu_path_str)
        print("Tabu Time:  {:.2f} mins".format(tabu_time))
        tabu_times.append(tabu_time)
        aveTabu = sum(tabu_times) / len(tabu_times)
        writer.writerow(["Tabu", tabu_path_str, "{:.2f}".format(tabu_time), "{:.2f}".format(aveTabu)])
    else:
        print("Tabu Path:  No valid path to F")
        writer.writerow(["Tabu", "No valid path to F", "N/A", "N/A"])

    # Time comparison
    if bfs_time != float('inf') and tabu_time != float('inf'):
        time_diff = tabu_time - bfs_time
        if abs(time_diff) < 1e-6:
            print("Tabu Search and BFS resulted in the same time: {:.2f} mins".format(bfs_time))
        else:
            percentage_diff = abs(time_diff) / bfs_time * 100
            comparison = "faster" if time_diff < 0 else "slower"
            print("Tabu Search was {:.2f}% or {:.2f} minutes {} than BFS.".format(
                percentage_diff,
                abs(time_diff),
                comparison
            ))
