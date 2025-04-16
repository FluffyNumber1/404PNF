# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import osmnx as ox
# import networkx as nx

# import geopandas as gpd

# # allow the python to take requests from the app.tsx
# app = Flask(__name__)
# CORS(app)

# # take data from roads.shp and make it into a graph
# shapefile_path = "./public/roads.shp"
# gdf = gpd.read_file(shapefile_path)
# # graphifying (idk if thats a word) WE SHOULD CHANGE THIS TO MAKE THE GRAPH MANUALLY (more learning)
# G = ox.graph_from_gdfs(gdf, gdf)

# #for seeing data
# # print(gdf.head())  
# # print(gdf.columns)  
# # print(gdf.crs)  
# # print(gdf.geometry)  

# @app.route("/")
# def home():
#     return "flask works happy times"

# @app.route("/shortest-path", methods=["POST"])
# def shortest_path():
#     try:
#         #take the data from App.tsx to use later
#         data = request.json
#         point1 = tuple(data["point1"])
#         point2 = tuple(data["point2"])

#         # finds the nearest nodes using the two points
#         node1 = ox.distance.nearest_nodes(G, point1[1], point1[0])
#         node2 = ox.distance.nearest_nodes(G, point2[1], point2[0])

#         # get shortest path *****WE NEED TO MAKE THIS OURSELVES AND USING THE SPECIFIED ALGORITHM*****
#         path = nx.shortest_path(G, node1, node2, weight="length")

#         # get coordinates of path
#         path_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]

#         #return path coordinates in a format that leaflet drawing can understand
#         return jsonify({"path": path_coords})

#     #error handling
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# #run flash server
# if __name__ == "__main__":
#     app.run(debug=True)

#import all required libraries
from collections import deque
from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import LineString, Point
from scipy.spatial import KDTree
from geopy.distance import geodesic
import math

app = Flask(__name__)
CORS(app, supports_credentials=True)

print("connection established")

# load the road gainesville shapefile
gainesville_shapefile_path = "./public/Gainesville/BetterGainesville.shp"
gdf = gpd.read_file(gainesville_shapefile_path)


# Load the road south florida shapefiles
# southFL_shapefile_paths = [
#     "./public/South_Florida/FL1.shp",
#     "./public/South_Florida/FL2_1.shp",
#     "./public/South_Florida/FL2_2.shp",
#     "./public/South_Florida/FL3.shp",
#     "./public/South_Florida/FL4.shp",
#     "./public/South_Florida/FL5.shp",
#     "./public/South_Florida/FL6.shp"
# ]
# gdf_list = []
# for path in southFL_shapefile_paths:
#     gdf = gpd.read_file(path)
    
#     if gdf.crs is None:
#         gdf.set_crs("EPSG:4326", allow_override=True, inplace=True)
#     else:
#         if gdf.crs != "EPSG:4326":
#             gdf = gdf.to_crs(epsg=4326)
#     gdf_list.append(gdf)

# gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))
# gdf = gdf.drop_duplicates(subset='geometry', keep='first')

# for seeing data
print(gdf.head())  
print(gdf.columns)  
print(gdf.crs)  
print(gdf.geometry)  

# make sure the units used are the same.
if gdf.crs is None:
    gdf.set_crs(epsg=4326, inplace=True)
gdf = gdf.to_crs(epsg=4326)

# create empty graph
# G = nx.Graph()

# # Extract road segment endpoints and add to graph
# nodes = set()
# edges = []

# for _, row in gdf.iterrows():
#     if isinstance(row.geometry, LineString):
#         coords = list(row.geometry.coords)
#         for i in range(len(coords) - 1):
#             node1, node2 = tuple(coords[i]), tuple(coords[i+1])
#             nodes.add(node1)
#             nodes.add(node2)
#             distance = Point(node1).distance(Point(node2))  # Euclidean distance
#             G.add_edge(node1, node2, weight=distance)

# this is the same function from the App.tsx just in python syntax now.
def haversine(node1, node2):
    R = 3958.8  # radius of earth in miles. if you want distance in other units, then change this to another unit.

    lat1, lon1 = node1
    lat2, lon2 = node2
    # below is the haversine function that will get the distance between two coordinates
    # d = 2 * R * asin(sqrt(a))
    # a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlong/2)

    # convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # differences
    diff_lat = lat2_rad - lat1_rad
    diff_lon = lon2_rad - lon1_rad

    # haversine formula
    a = (math.sin(diff_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(diff_lon / 2) ** 2)
    d = 2 * R * math.asin(math.sqrt(a))

    return d

# create empty nx graph (this works as an adjacency list)
G = nx.Graph()

# dictionary to store unique nodes
node_dict = {}

# edges storage
edges = []

# extract edges from data and put into the graph
for _, row in gdf.iterrows():
    if isinstance(row.geometry, LineString):
        coords = np.array(row.geometry.coords)  # convert to NumPy array which is faster

        for i in range(len(coords) - 1):
            node1, node2 = tuple(coords[i]), tuple(coords[i+1])

            
            # get weights for each edge
            distance = haversine(node1, node2)
            distance = round(distance, 6)

            # add edge to list only if the edge is proper (not a jump or an error)
            if distance<5:
                edges.append((node1, node2, distance))
                if ((node2 == (-82.3682424, 29.6288011) and node1 == (-82.3313539, 29.6777634)) or (node1 == (-82.3682424, 29.6288011) and node2 == (-82.3313539, 29.6777634))):
                    print(distance)
                    print(distance)
                    print(distance)
                # store unique nodes in a dictionary
                if node1 not in node_dict:
                    node_dict[node1] = node1
                if node2 not in node_dict:
                    node_dict[node2] = node2
edges.append(((-82.276725, 29.741686),(-82.276667, 29.741039),0.05)) # manually put back a key error point that isnt in the data
edges.append(((-82.3307558, 29.686998),(-82.3307559, 29.6866266),0.05)) # manually put back a key error point that isnt in the data
edges = [
    e for e in edges if not (
        (
            (e[0] == (-82.3682424, 29.6288011) and e[1] == (-82.3313539, 29.6777634)) or
            (e[1] == (-82.3682424, 29.6288011) and e[0] == (-82.3313539, 29.6777634))
        ) or
        (
            (e[0] == (-82.3676, 29.629102) and e[1] == (-82.3313539, 29.6777634)) or
            (e[1] == (-82.3676, 29.629102) and e[0] == (-82.3313539, 29.6777634))
        )
    )
]#lines above removes bad things and not fun things that make me sad. sads times. not happys.

# add all edges to graph
G.add_nodes_from(node_dict.keys())
G.add_weighted_edges_from(edges)

print(f"Graph created with {len(G.nodes)} nodes and {len(G.edges)} edges.")


# convert the node list to a KDTree for faster closest neighbor lookup
node_list = list(node_dict.keys())
kdtree = KDTree(node_list)

def find_nearest_node(point):
    """Find the nearest graph node to a given lat/lon point."""
    print(f"Querying for point: {point.x}, {point.y}")  # print to console
    _, index = kdtree.query((point.x, point.y))  # use kdtree.query this is a O(V) time complexity due to spindly tree
    nearest_node = node_list[index]
    print(f"Found nearest node: {nearest_node}")  # print to console
    return nearest_node

@app.route("/")
def home():
    return "flask works happy times"

#This is a test function to see how the methods would plot on the graph using networkx
# def shortest_path():
#     try:
#         data = request.json
#         point1 = tuple(data["point1"])
#         point2 = tuple(data["point2"])

#         # find nearest nodes
#         node1 = find_nearest_node(Point(point1[1], point1[0]))
#         node2 = find_nearest_node(Point(point2[1], point2[0]))

#         print(f"Nearest nodes: {node1} and {node2}")  # print to console

#         # compute shortest path
#         path = nx.shortest_path(G, node1, node2, weight="weight")

#         print(f"Shortest path: {path}")  # print to console

#         # convert path nodes to lat/lon
#         path_coords = [[p[1], p[0]] for p in path]  

#         return jsonify({"path": path_coords})

#     except Exception as e:
#         print("Error:", str(e))  # print to console
#         return jsonify({"error": str(e)}), 500
    
#DIJKSTRAS IMPLEMENTATION WITH LIST AND NO HEAP
# def dijkstras():
#     try:
#         data = request.json
#         point1 = tuple(data["point1"])
#         point2 = tuple(data["point2"])
#         node1 = find_nearest_node(Point(point1[1], point1[0]))
#         node2 = find_nearest_node(Point(point2[1], point2[0]))
#         #initialize a dictionary to ensure that: 
#         #for all vertexes in the graph G, dist[v]=infinity and prev[v] = None (or undefined)
#         #change distance of start to 0 and create a list of unvisited nodes using all the vertexes in graph G
#         distances = {node: float('inf') for node in G.nodes()}
#         previous_nodes = {node: None for node in G.nodes()}
#         distances[node1] = 0
#         unvisited_nodes = list(G.nodes())
#         #While there are still destinations unexplored, set the current node to be the smallest distance
#         #set the current node to explored, meaning take it out of the list
#         #then at the end update each of the distances from the start to a given node
#         #if the distance to any of the nodes to the start is smaller than the previous expected, change the distance and the previous node to the current node
#         #NOTE this can be done with a minheap to make it faster, but it is slightly more complex
#         while unvisited_nodes:
#             current_node = min(unvisited_nodes, key=lambda node: distances[node])

#             if current_node == node2:
#                 path = []
#                 while previous_nodes[current_node] is not None:
#                     path.append(current_node)
#                     current_node = previous_nodes[current_node]
#                 path.append(node1)
#                 path.reverse()

#                 # convert the path nodes to lat/lon
#                 path_coords = [[p[1], p[0]] for p in path]
#                 return jsonify({"path": path_coords})

#             # remove current node from unvisited list
#             unvisited_nodes.remove(current_node)

#             # update distances to neighbors
#             for neighbor in G.neighbors(current_node):
#                 weight = G[current_node][neighbor]['weight']
#                 new_distance = distances[current_node] + weight
#                 if new_distance < distances[neighbor]:
#                     distances[neighbor] = new_distance
#                     previous_nodes[neighbor] = current_node

#         return jsonify({"error": "No path found"}), 404

#     except Exception as e:
#         print("Error:", str(e))  # Debugging log
#         return jsonify({"error": str(e)}), 500
# 
import heapq 
# this is where the request is sent to when the App.tsx calls
@app.route("/dijkstras", methods=["POST"])
def dijkstras():
    try:
        data = request.json
        point1 = tuple(data["point1"])
        point2 = tuple(data["point2"])

        node1 = find_nearest_node(Point(point1[1], point1[0]))
        node2 = find_nearest_node(Point(point2[1], point2[0]))

        # initialize distances to all nodes as infinity but the start node like before
        distances = {node: float('inf') for node in G.nodes()}
        previous_nodes = {node: None for node in G.nodes()}
        distances[node1] = 0

        # min-heap stores nodes based on shortest distance
        heap = [(0, node1)]  # (distance, node)

        while heap:
            #extract the node with the smallest current distance
            current_distance, current_node = heapq.heappop(heap)
            #if the target end is reached, reconstruct the path like before
            if current_node == node2:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = previous_nodes[current_node]
                path.reverse()

                # convert path nodes to lat/lon like before
                path_coords = [[p[1], p[0]] for p in path]
                return jsonify({"path": path_coords})

            # if the current distance is greater than the recorded one, skip processing
            if current_distance > distances[current_node]:
                continue
            #for each of the neighbors to the current node, update the distances if a shorter path presents itself
            #like before
            for neighbor in G.neighbors(current_node):
                weight = G[current_node][neighbor]['weight']
                new_distance = current_distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(heap, (new_distance, neighbor))

        return jsonify({"error": "No path found"}), 404

    except Exception as e:
        print("Error:", str(e))  # print to console
        return jsonify({"error": str(e)}), 500
    #NOTE the min-heap method performs far better,
    #the original method uses O(N^2) where N is the number of nodes because of curr_node = min(unvisited, node: distances)
    #the new one is much faster in that regard. With the first method 1 million nodes would take 1 trillion operations. Not happening.

@app.route("/bfs", methods=["POST"])
def bfs():
    try:
        data = request.json
        point1 = tuple(data["point1"])
        point2 = tuple(data["point2"])

        node1 = find_nearest_node(Point(point1[1], point1[0]))
        node2 = find_nearest_node(Point(point2[1], point2[0]))

        q = deque([(node1, [node1])]) #(current_node, [path])
        visited = set() #tracks visited nodes

        while q:
            current_node, path = q.popleft()

            if current_node == node2: #if target node is reached
                path_coords = [[p[1], p[0]] for p in path] #converts node path from format (lat, lon) to [[lon, lat]]
                return jsonify({"path": path_coords})

            if current_node not in visited:
                visited.add(current_node)

                for neighbor in G.neighbors(current_node):
                    if neighbor not in visited:
                        new_path = path + [neighbor]
                        q.append((neighbor, new_path))
                       
        return jsonify({"error": "No path found"}), 404

    except Exception as e:
        print("Error:", str(e))  # Debugging log
        return jsonify({"error": str(e)}), 500


@app.route("/dfs", methods=["POST"])
def dfs():
    try:
        data = request.json
        point1 = tuple(data["point1"])
        point2 = tuple(data["point2"])

        node1 = find_nearest_node(Point(point1[1], point1[0]))
        node2 = find_nearest_node(Point(point2[1], point2[0]))

        stack = [(node1, [node1])] #(current_node, [path])
        visited = set() #tracks visited nodes

        while stack:
            current_node, path = stack.pop()

            if current_node == node2: #if target node is reached
                path_coords = [[p[1], p[0]] for p in path] #converts node path from format (lat, lon) to [[lon, lat]]
                return jsonify({"path": path_coords})

            if current_node not in visited:
                visited.add(current_node)
                for neighbor in G.neighbors(current_node):
                    if neighbor not in visited:
                        stack.append((neighbor, path + [neighbor]))
                       
        return jsonify({"error": "No path found"}), 404

    except Exception as e:
        print("Error:", str(e))  # Debugging log
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
