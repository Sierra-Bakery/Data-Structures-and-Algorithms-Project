# COMP1002 - ZipRide Dispatch System
# This is the main file for the ZipRide Dispatch System.
# Made by Dylan Baker 22368201

import graph
g = graph.Graph()
cont = "Y"

while cont == "Y":
    print("Welcome to the ZipRide Dispatch System!")
    graph.menu(g)
    cont = input("Would you like to continue? (Y/N): ").upper()
