# COMP1002 - ZipRide Dispatch System
# This is the main file for the ZipRide Dispatch System.
# Made by Dylan Baker 22368201
# Date: 30/05/2026

import dependencies
dependencies.checkDependencies()

import graph
import initdata
import hash
import heap
import sort    

cont = "Y"

# Initialize the graph and populate it with hardcoded data
graphData = graph.Graph()
initdata.populateGraph(graphData)

# Initialize the hash tables and populate them with hardcoded data
passengerTable = hash.HashTable(20)
driverTable = hash.HashTable(20)
initdata.populateRecords(passengerTable, driverTable)

# Initialize the scheduler with the graph and hash tables
scheduler = heap.Scheduler(graphData, passengerTable, driverTable)

while cont == "Y":
    print("Welcome to the ZipRide Dispatch System!")
    graph.menu(graphData)
    hash.menu(passengerTable, driverTable)
    heap.menu(scheduler)
    sort.menu(graphData, passengerTable, driverTable)
    cont = input("Would you like to continue? (Y/N): ").upper()


# When i awake in the morning, may i be a better programmer than yesterday...