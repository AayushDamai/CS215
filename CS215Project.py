import networkx as nx
import matplotlib.pyplot as plt
import random
from collections import deque

# --- Graph Setup ---
city = nx.DiGraph()
nodes = {
    "A": "Intersection 1", "B": "Intersection 2", "C": "Intersection 3",
    "D": "Intersection 4", "E": "Intersection 5", "F": "Intersection 6"
}
for node in nodes:
    city.add_node(node, label=nodes[node])

edges = [
    ("A", "B"), ("A", "C"), ("B", "D"),
    ("C", "E"), ("D", "F"), ("E", "F")
]

# Randomize edge attributes
for u, v in edges:
    city.add_edge(u, v, 
                  distance=random.randint(3, 10),
                  speed_limit=random.randint(30, 70),
                  traffic=round(random.uniform(1.0, 3.0), 2))

# --- Utility Functions ---
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
    tabu_list = deque(maxlen=tabu_size)
    tabu_history = []

    for _ in range(max_iterations):
        neighbors = [n for n in get_neighbors(current_solution) if n not in tabu_list]
        if not neighbors:
            break
        neighbors.sort(key=travel_time)
        current_solution = neighbors[0]
        tabu_list.append(list(current_solution))
        tabu_history.append(list(current_solution))
        current_cost = travel_time(current_solution)
        if current_solution[-1] == goal and current_cost < best_cost:
            best_solution, best_cost = list(current_solution), current_cost

    return best_solution, best_cost, tabu_history

# --- Main Execution ---
bfs_order, bfs_edges = bfs(city, "A")
bfs_path = extract_bfs_path("A", "F", bfs_edges)
bfs_time = total_travel_time(city, bfs_path)
tabu_path, tabu_time, tabu_list_log = tabu_search(city, "A", "F")

# --- Visualization ---
pos = nx.spring_layout(city, seed=42)
edge_colors = ['red' if a['traffic'] >= 2.0 else 'orange' if a['traffic'] >= 1.5 else 'yellow'
               for _, _, a in city.edges(data=True)]

edge_labels = {}
for u, v, attr in city.edges(data=True):
    base = (attr['distance'] / attr['speed_limit']) * 50
    total = calculate_travel_time(attr['distance'], attr['speed_limit'], attr['traffic'])
    edge_labels[(u, v)] = (
        f"Time: {total:.1f} min\n"
        f"Speed: {attr['speed_limit']} mph\n"
        f"Traffic: (+{total - base:.1f} min)"
    )

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8), facecolor='white')
fig.suptitle("City Network Comparison: Breadth First Search vs Tabu Search", fontsize=18, fontweight='bold')

for ax, path, color, label in [(ax1, bfs_path, 'dodgerblue', "Breadth First Search Path (Blue)"),
                               (ax2, tabu_path, 'forestgreen', "Tabu Search Path (Green Dashed)")]:
    nx.draw(city, pos, ax=ax, with_labels=True, labels=nodes, node_color='lightsteelblue',
            node_size=2000, font_size=10, edge_color=edge_colors, width=2, arrows=True)

    if path:
        edge_list = list(zip(path, path[1:]))
        style = 'solid' if color == 'dodgerblue' else 'dashed'
        nx.draw_networkx_edges(city, pos, edgelist=edge_list, edge_color=color, style=style,
                               width=4, ax=ax, arrows=True, connectionstyle="arc3,rad=0.05",
                               min_source_margin=12, min_target_margin=12)
        nx.draw_networkx_nodes(city, pos, nodelist=path, node_color=color, ax=ax)
        ax.text(pos[path[0]][0], pos[path[0]][1] - 0.12, "Start", ha='center', fontsize=9)
        ax.text(pos[path[-1]][0], pos[path[-1]][1] + 0.12, "End", ha='center', fontsize=9)

    for (u, v), label_text in edge_labels.items():
        x, y = (pos[u][0]+pos[v][0])/2, (pos[u][1]+pos[v][1])/2
        ax.text(x, y, label_text, fontsize=8, ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    ax.set_title(label, fontsize=14)
    ax.axis('off')

# Tabu list beside the Tabu Search graph
if tabu_list_log:
    tabu_str = "\n".join(" → ".join(p) for p in tabu_list_log[-6:])
    ax2.text(1.05, 0.5, "Recent Tabu List:\n" + tabu_str, transform=ax2.transAxes,
             fontsize=9, verticalalignment='center', bbox=dict(facecolor='white', alpha=0.9))

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.show()

# --- Console Output ---
print("=== Path Comparison ===")
if bfs_path:
    print("BFS Path:   " + " -> ".join(bfs_path))
    print("BFS Time:   {:.2f} mins".format(bfs_time))
else:
    print("BFS Path:   No path to F")

if tabu_path:
    print("Tabu Path:  " + " -> ".join(tabu_path))
    print("Tabu Time:  {:.2f} mins".format(tabu_time))
else:
    print("Tabu Path:  No valid path to F")

if bfs_time != float('inf') and tabu_time != float('inf'):
    time_diff = tabu_time - bfs_time
    if abs(time_diff) < 1e-6:
        print("Tabu Search and BFS resulted in the same time: {:.2f} mins".format(bfs_time))
    else:
        percentage_diff = abs(time_diff) / bfs_time * 100
        print("Tabu Search was {:.2f}% or {:.2f} minutes {} than BFS.".format(
            percentage_diff,
            abs(time_diff),
            "faster" if time_diff < 0 else "slower"
        ))
