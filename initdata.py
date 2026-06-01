# initdata.py - HARDCODED DATA FOR EASE OF STARTING
# This file is meant to be run once to populate the graph with data.
import graph
import hash

# source, destination, weight in minutes
EDGE_DATA = [
    ("CBD", "Hospital", 5),
    ("CBD", "Curtin", 14),
    ("CBD", "Airport", 25),
    ("CBD", "Fremantle", 25),
    ("CBD", "SubNorth", 30),
    ("CBD", "SubSouth", 22),
    ("CBD", "CaroShops", 20),
    ("CBD", "Kingspark", 8),
    ("Hospital", "Curtin", 18),
    ("Hospital", "Airport", 22),
    ("Hospital", "CaroShops", 18),
    ("Hospital", "Kingspark", 7),
    ("Curtin", "Airport", 15),
    ("Curtin", "CaroShops", 10),
    ("Curtin", "SubSouth", 18),
    ("Curtin", "Fremantle", 20),
    ("Airport", "SubNorth", 28),
    ("Airport", "Industrial", 10),
    ("Airport", "BelmontShops", 12),
    ("Industrial", "BelmontShops", 8),
    ("Industrial", "SubSouth", 25),
    ("Industrial", "Curtin", 20),
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

# passengerID, name, pickupLocation, membershipTier, phoneNumber
PASSENGER_DATA = [
    (1001, "Alice Nguyen", "CBD", 1, "0411000001"),
    (1002, "Bob Smith", "Fremantle", 2, "0411000002"),
    (1003, "Carol White", "Airport", 3, "0411000003"),
    (1004, "Dan Brown", "Curtin", 4, "0411000004"),
    (1005, "Eve Jones", "Kingspark", 5, "0411000005"),
    (1006, "Frank Lee", "SubNorth", 1, "0411000006"),
    (1007, "Grace Kim", "CaroShops", 2, "0411000007"),
    (1008, "Hank Yung", "SubSouth", 3, "0411000008"),
    (1009, "Isla Martin", "Hospital", 1, "0411000009"),
    (1010, "Jack Turner", "Industrial", 5, "0411000010"),
    (1011, "Karen Hall", "CBD", 2, "0411000011"),
    (1012, "Liam Chen", "BelmontShops", 3, "0411000012"),
    (1013, "Mia Patel", "Joondalup", 1, "0411000013"),
    (1014, "Noah Wilson", "Midland", 4, "0411000014"),
    (1015, "Olivia Scott", "Fremantle", 2, "0411000015"),
]
 
# driverID, name, currentLocation, availabilityStatus, vehicleType, rating
DRIVER_DATA = [
    (2001, "Tom Hardy", "CBD", "Available", "Sedan", 4.8),
    (2002, "Sara Connor", "Airport", "Busy", "SUV", 4.5),
    (2003, "Mike Ross", "Fremantle", "Available", "Sedan", 4.9),
    (2004, "Lisa Ray", "Curtin", "Offline", "Sedan", 4.2),
    (2005, "James Dean", "Kingspark", "Available", "SUV", 4.7),
    (2006, "Nina Watts", "SubNorth", "Busy", "Van", 4.3),
    (2007, "Omar Sharif", "BelmontShops", "Available", "Sedan", 4.6),
    (2008, "Paula Bose", "Hospital", "Available", "Sedan", 5.0),
    (2009, "Quinn Blake", "SubSouth", "Offline", "Sedan", 3.9),
    (2010, "Rosa Parks", "Midland", "Available", "SUV", 4.8),
    (2011, "Steve Irwin", "CBD", "Busy", "Van", 4.4),
    (2012, "Tina Turner", "Joondalup", "Available", "Sedan", 4.7),
    (2013, "Uma Thurman", "Industrial", "Offline", "SUV", 4.1),
    (2014, "Victor Hugo", "CaroShops", "Available", "Van", 4.5),
    (2015, "Wendy Chang", "Airport", "Busy", "Sedan", 4.6),
]


def populateRecords(passengerTable, driverTable):
    # Populates the given HashTable instances with all hardcoded
    # passenger and driver records.
    
    try:
        passengerCount = 0
        for pid, name, loc, tier, phone in PASSENGER_DATA:
            try:
                rec = hash.PassengerRecord(pid, name, loc, tier, phone)
                passengerTable.insert(rec)
                passengerCount += 1
                
            except Exception as e:
                print(f"  Warning: could not add passenger {pid}: {e}")
 
        driverCount = 0
        
        for did, name, loc, status, vehicle, rating in DRIVER_DATA:
            try:
                rec = hash.DriverRecord(did, name, loc, status, vehicle, rating)
                driverTable.insert(rec)
                driverCount += 1
                
            except Exception as e:
                print(f"  Warning: could not add driver {did}: {e}")
 
        print(f"Records populated: {passengerCount} passengers, "
              f"{driverCount} drivers.")
 
    except Exception as e:
        raise Exception(f"Error populating records: {e}")


def populateGraph(graphData):
    try:
        # add every unique vertex found in the edge data
        for src, dst, _ in EDGE_DATA:
            if not graphData.hasVertex(src):
                graphData.addVertex(src)
                
            if not graphData.hasVertex(dst):
                graphData.addVertex(dst)
 
        # add every edge with its weight
        for src, dst, weight in EDGE_DATA:
            try:
                graphData.addEdge(src, dst, weight)
                
            except Exception as e:
                print(f"  Warning: could not add edge {src} <-> {dst}: {e}")
 
        print(f"Graph populated: {graphData.getVertexCount()} vertices, {graphData.getEdgeCount()} edges.")
 
    except Exception as e:
        raise Exception(f"Error populating graph: {e}")
