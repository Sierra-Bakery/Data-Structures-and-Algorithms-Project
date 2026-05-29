# COMP1002 - ZipRide Dispatch System
# This is the main file for the ZipRide Dispatch System.
# Made by Dylan Baker 22368201

import graph
import initdata
import hash
import heap

cont = "Y"

# Initialize the graph and populate it with hardcoded data
g = graph.Graph()
initdata.populateGraph(g)
# Initialize the hash tables and populate them with hardcoded data
passengerTable = hash.HashTable(20)
driverTable    = hash.HashTable(20)
initdata.populateRecords(passengerTable, driverTable)
# Initialize the scheduler with the graph and hash tables
scheduler = heap.ZipRideScheduler(g, passengerTable, driverTable)

while cont == "Y":
    print("Welcome to the ZipRide Dispatch System!")
    graph.menu(g)
    hash.menu(passengerTable, driverTable)
    heap.menu(scheduler)
    cont = input("Would you like to continue? (Y/N): ").upper()
