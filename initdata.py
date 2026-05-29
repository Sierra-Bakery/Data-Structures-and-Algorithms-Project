# initdata.py - HARDCODED DATA FOR EASE OF STARTING
# This file is meant to be run once to populate the graph with data.
import graph

# Hardcoded edge data for testing: (source, destination, weight in minutes)
EDGE_DATA = [
    ("CBD", "Hospital",  5),
    ("CBD", "Curtin", 14),
    ("CBD", "Airport", 25),
    ("CBD", "Fremantle", 25),
    ("CBD", "SubNorth", 30),
    ("CBD", "SubSouth", 22),
    ("CBD", "CaroShops", 20),
    ("CBD", "Kingspark", 8),
    ("Hospital", "Curtin", 18),
    ("Hospital", "Airport", 22),
    ("Hospital", "CaroShops",    18),
    ("Hospital", "Kingspark", 7),
    ("Curtin", "Airport", 15),
    ("Curtin", "CaroShops",    10),
    ("Curtin", "SubSouth",     18),
    ("Curtin", "Fremantle", 20),
    ("Airport", "SubNorth", 28),
    ("Airport", "Industrial", 10),
    ("Airport", "BelmontShops", 12),
    ("Industrial", "BelmontShops", 8),
    ("Industrial", "SubSouth", 25),
    ("Industrial", "Curtin",    20),
    ("CaroShops", "SubSouth", 12),
    ("CaroShops", "Fremantle", 28),
    ("BelmontShops", "SubNorth", 35),
    ("SubNorth", "Fremantle", 40),
    ("SubNorth", "Joondalup", 5),
    ("Joondalup", "Fremantle", 42),
    ("SubSouth", "Fremantle", 15),
    ("Kingspark", "Fremantle", 22),
    ("Kingspark", "SubNorth", 35),
    ("Midland", "Airport", 18),
    ("Midland", "Industrial", 20),
]

def populateGraph(g):
    """
    Populates the given Graph instance with all hardcoded nodes and edges.
    Vertices are automatically derived from the edge data so there is no
    duplicate node list to maintain.
    """
    try:
        # add every unique vertex found in the edge data
        for src, dst, _ in EDGE_DATA:
            if not g.hasVertex(src):
                g.addVertex(src)
            if not g.hasVertex(dst):
                g.addVertex(dst)
 
        # add every edge with its weight
        for src, dst, weight in EDGE_DATA:
            try:
                g.addEdge(src, dst, weight)
            except Exception as e:
                print(f"  Warning: could not add edge {src} <-> {dst}: {e}")
 
        print(f"Graph populated: {g.getVertexCount()} vertices, {g.getEdgeCount()} edges.")
 
    except Exception as e:
        raise Exception(f"Error populating graph: {e}")
