# Description: Merge sort and quick sort algorithms link to rest of the program with benchmarking of estimated pickup times for passenger requests
# Author: Dylan Baker 22368201
# Date: 30/05/2026

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import timeit
import time
import graph


def _mergeSort(array, opCount, low, high):
    try:
        # Base case if single element is already sorted
        if high - low <= 1:
            return array

        # Recursive case, so split array in half and merge sort each half
        middle = (low + high) // 2
        
        _mergeSort(array, opCount, low, middle)
        
        _mergeSort(array, opCount, middle, high)
        
        _merge(array, opCount, low, middle, high)
        
        return array
    
    except Exception as e:
        raise Exception(f"Merge sort error: {e}")


def _merge(array, opCount, low, middle, high):
    leftLength  = middle - low
    rightLength = high - middle

    left  = np.empty(leftLength, dtype=object)
    right = np.empty(rightLength, dtype=object)

    # Copy data to temp arrays
    for i in range(leftLength):
        left[i]  = array[low + i]
        opCount[0] += 1

    for i in range(rightLength):
        right[i] = array[middle + i]
        opCount[0] += 1

    i = 0
    j = 0
    k = low
    
    # Merge the temp arrays back into array[low..high]
    while i < leftLength and j < rightLength:
        opCount[0] += 1
        
        # Compare the estimatedTime of left[i] and right[j] to maintain stability (keep original order of equal keys)
        if left[i].estimatedTime <= right[j].estimatedTime:
            array[k] = left[i]
            i += 1
            
        else:
            array[k] = right[j]
            j += 1
        k += 1

    # Copy the remaining elements of left
    while i < leftLength:
        array[k] = left[i]
        i += 1
        k += 1
        opCount[0] += 1

    # Copy the remaining elements of right
    while j < rightLength:
        array[k] = right[j]
        j += 1
        k += 1
        opCount[0] += 1


def mergeSort(array):
    try:
        if len(array) == 0:
            return array, 0
        
        # sort by estimatedTime ascending
        opCount = np.zeros(1, dtype=np.int64)
        _mergeSort(array, opCount, 0, len(array))
        
        return array, int(opCount[0])
    
    except Exception as e:
        raise Exception(f"Merge sort failed: {e}")


def _quickSort(array, opCount, low, high):
    try:
        if high - low <= 1:
            return

        # USING A median OF three pivot selection strategy to avoid O(n squared) worst case on sorted/reversed arrays
        middle = (low + high) // 2
        opCount[0] += 3

        # sort low, middle, high so median ends up at middle
        # Compare low vs middle, low vs high, middle vs high and swap as needed to order them.
        # Ensuring the median of the three is at middle.
        
        if array[low].estimatedTime > array[middle].estimatedTime:
            array[low], array[middle] = array[middle], array[low]
            opCount[0] += 1
            
        if array[low].estimatedTime > array[high - 1].estimatedTime:
            array[low], array[high - 1] = array[high - 1], array[low]
            opCount[0] += 1
            
        if array[middle].estimatedTime > array[high - 1].estimatedTime:
            array[middle], array[high - 1] = array[high - 1], array[middle]
            opCount[0] += 1

        # place pivot at high-1 for partitioning
        pivot = array[middle].estimatedTime
        array[middle], array[high - 1] = array[high - 1], array[middle]

        i = low - 1
        j = high - 1

        # Partitioning loop: move i right until find an element >= pivot
        # move j left until we find an element <= pivot
        # swap and repeat until i and j cross.
        done = False
        
        while not done:
            i += 1
            
            while array[i].estimatedTime < pivot:
                i += 1
                opCount[0] += 1
                
            j -= 1
            while j >= low and array[j].estimatedTime > pivot:
                j -= 1
                opCount[0] += 1
                
            if i >= j:
                done = True
                
            else:
                array[i], array[j] = array[j], array[i]
                opCount[0] += 1

        # restore pivot
        array[i], array[high - 1] = array[high - 1], array[i]
        opCount[0] += 1

        # recursively sort partitions
        _quickSort(array, opCount, low, i)
        _quickSort(array, opCount, i + 1, high)
        
    except Exception as e:
        raise Exception(f"Quick sort error: {e}")


def quickSort(array):
    try:
        if len(array) == 0:
            return array, 0
        
        # sort by estimatedTime ascending
        opCount = np.zeros(1, dtype=np.int64)
        _quickSort(array, opCount, 0, len(array))
        return array, int(opCount[0])
    
    except Exception as e:
        raise Exception(f"Quick sort failed: {e}")


class SortableRequest():
    # Wrapper for a passenger request that includes the estimated pickup time
    # For sorting benchmark demonstration
    def __init__(self, passengerID, estimatedTime):
        try:
            self.passengerID = int(passengerID)
            self.estimatedTime = float(estimatedTime)
            
        except Exception as e:
            raise Exception(f"SortableRequest error: {e}")

    def __str__(self):
        return f"[ID={self.passengerID} | T={self.estimatedTime:.2f}]"


def _generateTimes(n, rng, graph, passengerTable, driverTable):
    # Generate n estimated pickup times by sampling random driver and passenger pairs
    times = np.empty(n, dtype=float)

    # collect all driverLocation and passengerLocation pairs from hash tables
    driverLocations = np.empty(50, dtype=object)
    passengerLocations = np.empty(50, dtype=object)
    
    dCount = 0
    pCount = 0

    try:
        dArr = driverTable._hashArray
        # iterate through driver hash table and collect up to 50 current locations of active drivers
        for i in range(len(dArr)):
            if dArr[i].state == 1 and dCount < 50:
                driverLocations[dCount] = dArr[i].value.currentLocation
                dCount += 1

        pArr = passengerTable._hashArray
        # iterate through passenger hash table and collect up to 50 pickup locations of active passengers
        for i in range(len(pArr)):
            if pArr[i].state == 1 and pCount < 50:
                passengerLocations[pCount] = pArr[i].value.pickupLocation
                pCount += 1

    except Exception:
        dCount = 0
        pCount = 0

    for idx in range(n):
        try:
            if dCount > 0 and pCount > 0:
                #sample random driver and passenger locations and get Dijkstra time
                dLoc = driverLocations[rng.integers(0, dCount)]
                pLoc = passengerLocations[rng.integers(0, pCount)]
                t, _ = graph.dijkstra(dLoc, pLoc)
                
                t = float(t)
                
                # handle any infinite or negative times by replacing with random time
                if t == np.inf or t < 0:
                    t = float(rng.integers(5, 120))
                 
            # if no active drivers or passengers then generate random time
            else:
                t = float(rng.integers(5, 120))
                
        except Exception:
            t = float(rng.integers(5, 120))
            
        times[idx] = t

    return times


def generateDataset(n, condition, graph, passengerTable, driverTable):
    # condition: random, nearly_sorted, reversed
    try:
        randomSeed = 42 # fixed seed for reproducibility
        SortedFraction = 0.10 # fraction of records displaced for nearly-sorted
        rng = np.random.default_rng(randomSeed) # FIXED SEED FOR REPRODUCIBILITY
        times = _generateTimes(n, rng, graph, passengerTable, driverTable)

        # sort as baseline with selection sort
        for i in range(len(times)):
            minIndex = i
            
            for j in range(i + 1, len(times)):
                if times[j] < times[minIndex]:
                    minIndex = j
            
            temp = times[i]
            times[i] = times[minIndex]
            times[minIndex] = temp
            
        if condition == "reversed":
            times = times[::-1].copy()

        elif condition == "nearly_sorted":
            nSwaps = max(1, int(n * SortedFraction))
            idxArr = rng.choice(n, size=nSwaps * 2, replace=False)
            
            # swap pairs of elements at random indices to create a nearly sorted array
            for k in range(nSwaps):
                a = int(idxArr[k])
                b = int(idxArr[k + nSwaps])
                times[a], times[b] = times[b], times[a]

        elif condition == "random":
            rng.shuffle(times)

        else:
            raise Exception(f"Unknown condition: {condition}")

        array = np.empty(n, dtype=object)
        for i in range(n):
            array[i] = SortableRequest(i + 1, times[i])
        return array

    except Exception as e:
        raise Exception(f"Error generating dataset: {e}")


def _copyArr(array):
    out = np.empty(len(array), dtype=object)
    
    for i in range(len(array)):
        out[i] = array[i]
        
    return out


def _isSorted(array):
    # sorted check by estimatedTime ascending
    for i in range(len(array) - 1):
        if array[i].estimatedTime > array[i + 1].estimatedTime:
            return False
    return True



def runBenchmarks(graph, passengerTable, driverTable):
    # Benchmark merge sort and quick sort on sets of various sizes and conditions
    dataSize = (100, 500, 1000) # dataset sizes for testing
    conditions = ("random", "nearly_sorted", "reversed")
    nRows      = len(dataSize) * len(conditions) * 2 # 2 algorithms with 3 conditions and 3 sizes
    
    REPEATS    = 3   # average over 3 timing runs

    # array to hold results for easy plotting and analysis
    dtype = np.dtype([("algorithm", "U12"), ("size", np.int32),
                    ("condition", "U14"), ("time_ms", np.float64),
                    ("ops", np.int64), ("correct", bool) ])
    
    results = np.empty(nRows, dtype=dtype)
    row = 0
    
    print("=== SORTING BENCHMARK ===")
    # print header for benchmark results
    print(f"{'Algorithm':<12} {'Size':>6} {'Condition':<15} "f"{'Time (ms)':>10} {'Operations':>12} {'Correct':>8}")
    print("-----------------------------------------------------------------------------------------------------")
    
    for n in dataSize:
        for cond in conditions:
            try:
                base = generateDataset(n, cond, graph, passengerTable, driverTable)
                
            except Exception as e:
                print(f"Error generating {n}/{cond}: {e}")

            # benchmark both algorithms on the same base array
            for algo, sortFn in (("MergeSort", mergeSort), ("QuickSort", quickSort)):
                try:
                    # average timing over REPEATS runs
                    totalTime = 0.0
                    lastOps   = 0
                    lastOk    = False

                    # copy base array for each run to ensure same input
                    for rep in range(REPEATS):
                        array = _copyArr(base)
                        t0 = time.perf_counter()
                        array, ops = sortFn(array)
                        t1 = time.perf_counter()
                        totalTime += (t1 - t0) * 1000  # convert to milliseconds
                        lastOps = ops
                        lastOk = _isSorted(array)

                    avgTime = totalTime / REPEATS

                    results[row] = (algo, n, cond, avgTime, lastOps, lastOk)
                    row += 1

                    print(f"{algo:<12} {n:>6} {cond:<15} "
                          f"{avgTime:>10.3f} {lastOps:>12,} "
                          f"{'YES' if lastOk else 'NO':>8}")

                except Exception as e:
                    print(f"Error in {algo}/{n}/{cond}: {e}")

    print("=== BENCHMARK COMPLETE ===")
    
    return results[:row]


def printFirstLast(array, label, n=5):
    # print the first and last n elements of an array
    print(f"\n  {label} (first {n} and last {n}):")
    count = len(array)
    
    for i in range(min(n, count)):
        print(f" [{i:>4}] {array[i]}")
        
    if count > n * 2:
        print(f" === ")
        
    for i in range(max(n, count - n), count):
        print(f" [{i:>4}] {array[i]}")


def savePlot(results, outputPath="sortingBenchmark.pdf"):
    #
    try:
        # Agg because not interactive so headless is ok
        matplotlib.use("Agg")

        conditions = ("random", "nearly_sorted", "reversed")
        dataSize = (100, 500, 1000) # dataset sizes for testing
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle("Merge Sort to Quick Sort in time", fontsize=14)

        # Plot a grouped bar chart comparing merge sort and quick sort times for each condition and data size
        for column, cond in enumerate(conditions):
            ax = axes[column]
            
            sizes = np.array(dataSize)
            mTimes = np.zeros(len(sizes))
            qTimes = np.zeros(len(sizes))

            for s, n in enumerate(sizes):
                # Create a mask for results for the current algorithm size, and condition
                mask = ((results["algorithm"] == "MergeSort") & (results["size"] == n) & (results["condition"] == cond))
                
                if np.any(mask):
                    mTimes[s] = results["time_ms"][mask][0]

                mask = ((results["algorithm"] == "QuickSort") & (results["size"] == n) & (results["condition"] == cond))
                
                if np.any(mask):
                    qTimes[s] = results["time_ms"][mask][0]

            xPosition  = np.arange(len(sizes))
            width = 0.35
            
            ax.bar(xPosition - width / 2, mTimes, width, label="Merge Sort", color="blue")
            
            ax.bar(xPosition + width / 2, qTimes, width, label="Quick Sort", color="orange")
            
            ax.set_title(cond.replace("_", " ").title())
            ax.set_xlabel("Dataset size")
            ax.set_ylabel("Time in milliseconds")
            ax.set_xticks(xPosition)
            
            ax.set_xticklabels([str(s) for s in sizes])
            
            ax.legend()

        plt.tight_layout()
        plt.savefig(outputPath)
        plt.close()
        
        print(f"\nPlot saved to: {outputPath}")

    except Exception as e:
        print(f"\nPlot skipped: {e}")


def printAnalysis():    
    print("""

""")


def demonstration(graph, passengerTable, driverTable):
    # Demonstrate sorting algorithms:
    #   Generate data then sort the data and verify it is sorted
    #   Then benchmakr it and plot the restults.
    try:
        print("=======================")
        print("MODULE 4 — SORTING DEMO")
        print("=======================")
        print("\n")

        # small demo with 10 random records to show the sorting in action
        print("\n--- Small demo (n=10, random) ---")
        demo = generateDataset(10, "random", graph, passengerTable, driverTable)
        print("Unsorted:")
        
        for i in range(len(demo)):
            print(f"    [{i}] {demo[i]}")

        mainArray = _copyArr(demo)
        mainArray, mergeOperations = mergeSort(mainArray)
        
        printFirstLast(mainArray, "Merge Sort result", n=5)
        print(f"Operations: {mergeOperations:,}")

        qArr = _copyArr(demo)
        qArr, quickOperations = quickSort(qArr)
        printFirstLast(qArr, "Quick Sort result", n=5)
        print(f"Operations: {quickOperations:,}")

        results = runBenchmarks(graph, passengerTable, driverTable)

        savePlot(results, "sortingBenchmark.pdf")

        printAnalysis()

        return results

    except Exception as e:
        raise Exception(f"Demo error: {e}")



def menu(graph, passengerTable, driverTable):
    option = 0
    while option != 4:
        print("===  Sorting Menu ===")
        print("1 Run a benchmark (100, 500 and 1000)")
        print("2 Sort custom data with size and condition")
        print("3 Quit")

        try:
            option = int(input("Enter option: "))
        except ValueError:
            print("Invalid input, please enter a number!")
            option = 0
            

        if option == 1:
            try:
                demonstration(graph, passengerTable, driverTable)
            except Exception as e:
                print(f"Error: {e}")

        elif option == 2:
            try:
                n = int(input("Dataset size: "))
                cond = input("Condition (random / nearly_sorted / reversed): ")
                
                array = generateDataset(n, cond, graph, passengerTable, driverTable)
                mainArray = _copyArr(array)
                qArr = _copyArr(array)

                mainArray, mergeOperations = mergeSort(mainArray)
                
                printFirstLast(mainArray, "Merge Sort", n=5)
                print(f"Merge Sort operations: {mergeOperations:,} | Correct: {_isSorted(mainArray)}")

                qArr, quickOperations = quickSort(qArr)
                
                printFirstLast(qArr, "Quick Sort", n=5)
                print(f"Quick Sort operations: {quickOperations:,} | Correct: {_isSorted(qArr)}")

            except Exception as e:
                print(f"  Error: {e}")

        elif option == 3:
            print("Exiting")

        else:
            print("Invalid option")
