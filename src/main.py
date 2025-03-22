import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Define location to extract road data (replace with your city or area)
place = "New Haven, Connecticut, USA"

# Load the road network (drivable roads only)
G = ox.graph_from_place(place, network_type="drive")

# Choose two random points as source and destination (can be set manually)
orig_node = list(G.nodes())[0]  # First node in the graph
dest_node = list(G.nodes())[-1]  # Last node in the graph

# Compute shortest path using A* algorithm
route = nx.astar_path(G, orig_node, dest_node, weight="length")

# Plot the map and highlight the shortest route
fig, ax = ox.plot_graph_route(G, route, route_linewidth=3, node_size=30, bgcolor="gray")

plt.show()
