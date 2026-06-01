import numpy as np

INITIAL_CAPACITY = 50   # numpy array size and doubled on resize if needed

class PickupRequest():
    # Just a single pickup request object to hold all relevant info and compute the priority
    def __init__(self, passengerID, passengerName, pickupLocation, membershipTier, assignedDriverID, assignedDriverName, estimatedTime):
        try:
            self._validate(passengerID, membershipTier, estimatedTime)
            self.passengerID = int(passengerID)
            self.passengerName = str(passengerName).strip()
            self.pickupLocation = str(pickupLocation).strip()
            self.membershipTier = int(membershipTier)
            self.assignedDriverID = int(assignedDriverID)
            self.assignedDriverName = str(assignedDriverName).strip()
            self.estimatedTime = float(estimatedTime)
            self.priority = self._calcPriority(membershipTier, estimatedTime)
            
        except Exception as e:
            raise Exception(f"PickupRequest error: {e}")

    def _validate(self, passengerID, membershipTier, estimatedTime):
        try:
            int(passengerID)
            
        except (ValueError, TypeError):
            raise Exception("PassengerID must be an integer")
        
        try:
            tier = int(membershipTier)
            if tier not in (1, 2, 3, 4, 5):
                raise Exception("MembershipTier must be 1–5")
            
        except (ValueError, TypeError):
            raise Exception("MembershipTier must be an integer")
        
        try:
            t = float(estimatedTime)
            
            if t < 0:
                raise Exception("EstimatedPickupTime must be >= 0")
            
        except (ValueError, TypeError):
            raise Exception("EstimatedPickupTime must be a number")

    def _calcPriority(self, membershipTier, estimatedTime):
        
        t = float(estimatedTime)
        
        if t == 0:
            # Avoids division by zero error by assigning high time bonus for immediate pickup
            timeBonus = 9999.0
            
        else:
            timeBonus = 1000.0 / t
            
        return (6 - int(membershipTier)) + timeBonus

    def updateTier(self, newTier):
        # Update the membership tier and recalculate priority
        try:
            tier = int(newTier)
            
            if tier not in (1, 2, 3, 4, 5):
                raise Exception("MembershipTier must be 1–5")
            
            self.membershipTier = tier
            self.priority = self._calcPriority(tier, self.estimatedTime)
            
        except Exception as e:
            raise Exception(f"Error updating tier: {e}")

    def __str__(self):
        tierLabel = [None, "Platinum", "Gold", "Silver", "Bronze", "Standard"]
        return (f"Passenger {self.passengerID} ({self.passengerName}) | "
                f"Pickup: {self.pickupLocation} | "
                f"Tier: {self.membershipTier} ({tierLabel[self.membershipTier]}) | "
                f"Driver: {self.assignedDriverID} ({self.assignedDriverName}) | "
                f"ETA: {self.estimatedTime:.1f} min | "
                f"Priority: {self.priority:.2f}")


class PickupHeap():
    def __init__(self, capacity=INITIAL_CAPACITY):
        try:
            self._capacity = int(capacity)
            self._heap  = np.empty(self._capacity, dtype=object)
            self._count = 0
            
        except Exception as e:
            raise Exception(f"PickupHeap init error: {e}")

    def insert(self, request):
        # Insert a PickupRequest into the heap then trickle up to maintain the max heap
        try:
            if not isinstance(request, PickupRequest):
                raise Exception("Only PickupRequest objects can be inserted")

            # resize if needed
            if self._count >= self._capacity:
                self._resize()

            # place at end, then trickle up
            self._heap[self._count] = request
            self._count += 1
            self._trickleUp(self._count - 1)

            print(f"Inserted: {request}")
            self._printHeap()

        except Exception as e:
            raise Exception(f"Error inserting request: {e}")

    def peek(self):
        # Shows the highest priority request
        try:
            if self._count == 0:
                raise Exception("Heap is empty – nothing to peek")
            
            return self._heap[0]
        
        except Exception as e:
            raise Exception(f"Error peeking heap: {e}")

    def extract_priority(self):
        # Swaps root with last element and trickles down

        try:
            if self._count == 0:
                raise Exception("Heap is empty")

            top = self._heap[0]

            # move last element to root and shrink
            self._count -= 1
            
            self._heap[0] = self._heap[self._count]
            
            self._heap[self._count] = None

            if self._count > 0:
                self._trickleDown(0)


            print(f"Extracted: {top}")
            
            self._printHeap()
            return top

        except Exception as e:
            raise Exception(f"Error extracting from heap: {e}")

    def update_tier(self, passengerID, newTier):
        #Find the request for passengerID, update its membership tier, recompute priority, and fix heap order -  full heapify.
        try:
            idx = self._findByPassengerID(passengerID)
            if idx == -1:
                raise Exception(f"Passenger {passengerID} not found in heap")
            
            self._heap[idx].updateTier(newTier)
            
            print(f"Tier updated for passenger {passengerID} " f" new priority: {self._heap[idx].priority:.2f}")
            
            self._heapify()
            
            self._printHeap()
            
        except Exception as e:
            raise Exception(f"Error updating tier: {e}")

    def remove_driver(self, driverID):
        # Remove all requests assigned to a driver and fix heap order - full heapify.
        try:
            removed = 0
            i = 0
            
            while i < self._count:
                if self._heap[i].assignedDriverID == driverID:
                    
                    # overwrite with last element
                    self._count -= 1
                    self._heap[i] = self._heap[self._count]
                    self._heap[self._count] = None
                    removed += 1
                    
                else:
                    i += 1
                    
            if removed == 0:
                print(f"   No requests found for driver {driverID}.")
                
            else:
                print(f"Removed {removed} request(s) for driver " f"{driverID} driver is no not available")
                
                self._heapify()
                self._printHeap()
                
        except Exception as e:
            raise Exception(f"Error removing driver requests: {e}")

    def isEmpty(self):
        return self._count == 0

    def size(self):
        return self._count

    def _trickleUp(self, idx):
        # Swap upward when child priority > parent priority.
        current = idx
        done = False
        while current > 0 and not done:
            parent = (current - 1) // 2
            if self._heap[current].priority > self._heap[parent].priority:
                self._heap[current], self._heap[parent] = \
                    self._heap[parent], self._heap[current]
                current = parent
            else:
                done = True

    def _trickleDown(self, idx):
        # Swap downward when parent priority < largest child priority.
        current = idx
        done = False
        while not done:
            left  = 2 * current + 1
            right = 2 * current + 2
            largest = current

            # Check left and right children against current largest
            if left < self._count and \
               self._heap[left].priority > self._heap[largest].priority:
                largest = left
            # Check right child against current largest
            if right < self._count and \
               self._heap[right].priority > self._heap[largest].priority:
                largest = right

            # If largest is not current, swap and continue down
            if largest != current:
                self._heap[current], self._heap[largest] = \
                    self._heap[largest], self._heap[current]
                current = largest
            else:
                done = True

    def _heapify(self):
        # Build heap from bottom up by trickling down all nodes
        i = (self._count // 2) - 1
        
        while i >= 0:
            self._trickleDown(i)
            i -= 1

    def _findByPassengerID(self, passengerID):
        # Linear search to find the index of a passengerID
        
        for i in range(self._count):
            if self._heap[i].passengerID == passengerID:
                return i
            
        return -1

    def _resize(self):
        # Double capacity when heap is full
        try:
            newCapacity = self._capacity * 2
            newHeap = np.empty(newCapacity, dtype=object)
            
            for i in range(self._count):
                newHeap[i] = self._heap[i]
                
            self._heap = newHeap
            self._capacity = newCapacity
            
            print(f"Resized to capacity {newCapacity}")
            
        except Exception as e:
            raise Exception(f"Error resizing heap: {e}")

    def _printHeap(self):
        print(f"Size: {self._count} | Contents (index: priority | passenger):")
        
        if self._count == 0:
            print("empty heap")
            return

        # flat array view
        for i in range(self._count):
            req = self._heap[i]
            print(f"    [{i:>2}] P={req.priority:>8.2f} | "
                  f"ID={req.passengerID} ({req.passengerName}) | "
                  f"Tier={req.membershipTier} | "
                  f"ETA={req.estimatedTime:.1f}min | "
                  f"Driver={req.assignedDriverName}")

        # tree layout
        print(f"   Tree view:")
        
        level = 0
        idx = 0
        
        while idx < self._count and level < 4:
            levelSize  = 2 ** level
            
            levelNodes = np.empty(levelSize, dtype=object)
            
            filled = 0
            i = idx
            
            while i < idx + levelSize and i < self._count:
                levelNodes[filled] = (f"[{self._heap[i].passengerID}"
                                      f"|{self._heap[i].priority:.1f}]")
                
                filled += 1
                i += 1
                
            indent = "    " + "  " * (3 - level) # indent for tree structure
            
            # Join the filled nodes with spacing, leaving empty slots blank
            row = indent + "  ".join(str(levelNodes[j]) for j in range(filled))
            
            
            print(row)
            
            idx  += levelSize
            level += 1
            
        if idx < self._count: # if more nodes exist beyond the displayed levels
            print(f"    ... ({self._count - idx} more nodes)")


class Scheduler():
    """
    Integrates the Graph (Module 1) and Hash Tables (Module 2) to build
    PickupRequests and manage the dispatch heap.

    Driver selection strategy
    -------------------------
    For each incoming request:
    1. Scan the driver hash table for every driver with status "Available".
    2. Run Dijkstra from each available driver's CurrentLocation to the
       passenger's PickupLocation.
    3. Select the driver with the minimum EstimatedPickupTime (T).
    4. Compute Priority = (6 - M) + 1000 / T and insert into the heap.

    Update handling
    ---------------
    - Tier change    : update_tier() adjusts priority in-place and re-heapifies.
    - Driver goes busy: remove_driver() purges their requests; if re-requested,
      a new nearest-available driver is selected automatically.
    - No drivers available: request is rejected with a clear message.
    """

    def __init__(self, graph, passengerTable, driverTable):
        try:
            self._graph          = graph
            self._passengerTable = passengerTable
            self._driverTable    = driverTable
            self._heap           = PickupHeap()
        except Exception as e:
            raise Exception(f"Scheduler init error: {e}")

    def requestPickup(self, passengerID):
        """
        Main entry point: retrieve passenger, find nearest available driver,
        compute priority, and insert request into the heap.
        """
        try:
            # --- retrieve passenger ---
            passenger = self._passengerTable.search(passengerID)
            pickupLoc = passenger.pickupLocation
            tier      = passenger.membershipTier

            # --- find nearest available driver ---
            bestDriverID   = -1
            bestDriverName = ""
            bestTime       = float('inf')
            bestPath       = None

            cur = self._driverTable._hashArray
            for i in range(len(cur)):
                if cur[i].state == 1:           # USED slot
                    driver = cur[i].value
                    if driver.availabilityStatus == "Available":
                        driverLoc = driver.currentLocation
                        try:
                            time, path = self._graph.dijkstra(driverLoc,
                                                              pickupLoc)
                            timVal = float(time)
                            if timVal < bestTime:
                                bestTime       = timVal
                                bestDriverID   = driver.driverID
                                bestDriverName = driver.name
                                bestPath       = path
                        except Exception:
                            pass    # driver unreachable – skip silently

            if bestDriverID == -1:
                print(f"records  [Scheduler] No available drivers can reach "
                      f"{pickupLoc}. Request for passenger "
                      f"{passengerID} rejected.")
                return None

            print(f"records  [Scheduler] Passenger {passengerID} "
                  f"({passenger.name}) @ {pickupLoc} "
                  f"| Tier {tier} "
                  f"| Nearest driver: {bestDriverName} "
                  f"(ID {bestDriverID}) "
                  f"| ETA: {bestTime:.1f} min")

            # --- build and insert request ---
            req = PickupRequest(passengerID, passenger.name, pickupLoc,
                                tier, bestDriverID, bestDriverName, bestTime)
            self._heap.insert(req)
            return req

        except Exception as e:
            raise Exception(f"Error requesting pickup: {e}")

    def dispatchNext(self):
        """Extract the highest-priority request and mark driver as Busy."""
        try:
            req = self._heap.extract_priority()
            print(f"records  [Scheduler] DISPATCHING: {req}")

            # mark driver as Busy in the hash table
            try:
                driver = self._driverTable.search(req.assignedDriverID)
                driver.availabilityStatus = "Busy"
                self._driverTable.insert(driver)   # update (duplicate → overwrite)
                print(f"  [Scheduler] Driver {req.assignedDriverID} "
                      f"({req.assignedDriverName}) marked Busy.")
            except Exception as e:
                print(f"  [Scheduler] Warning: could not update driver status: {e}")

            return req
        except Exception as e:
            raise Exception(f"Error dispatching: {e}")

    def updatePassengerTier(self, passengerID, newTier):
        """Update a passenger's tier in both the hash table and the heap."""
        try:
            passenger = self._passengerTable.search(passengerID)
            passenger.membershipTier = int(newTier)
            self._passengerTable.insert(passenger)  # overwrite
            self._heap.update_tier(passengerID, newTier)
        except Exception as e:
            raise Exception(f"Error updating passenger tier: {e}")

    def driverUnavailable(self, driverID):
        """Remove a driver's requests from the heap when they go Busy/Offline."""
        try:
            self._heap.remove_driver(driverID)
            driver = self._driverTable.search(driverID)
            driver.availabilityStatus = "Busy"
            self._driverTable.insert(driver)
            print(f"  [Scheduler] Driver {driverID} marked Busy/Offline.")
        except Exception as e:
            raise Exception(f"Error marking driver unavailable: {e}")

    def peekNext(self):
        """Show the highest-priority request without dispatching."""
        try:
            req = self._heap.peek()
            print(f"records  [Scheduler] Next to dispatch: {req}")
            return req
        except Exception as e:
            raise Exception(f"Error peeking scheduler: {e}")

    def heapSize(self):
        return self._heap.size()


# ================================================================== MENU

def menu(scheduler):
    option = 0
    while option != 6:
        print("records===  Scheduler Menu ===")
        print("1. Request pickup (by Passenger ID)")
        print("2. Dispatch next (highest priority)")
        print("3. Peek next request")
        print("4. Update passenger membership tier")
        print("5. Mark driver unavailable")
        print("6. Quit")

        try:
            option = int(input("Enter option: "))
        except ValueError:
            print("Invalid input, please enter a number!")
            option = 0
            continue

        if option == 1:
            try:
                pid = int(input("  Passenger ID: "))
                scheduler.requestPickup(pid)
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 2:
            try:
                scheduler.dispatchNext()
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 3:
            try:
                scheduler.peekNext()
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 4:
            try:
                pid  = int(input("  Passenger ID: "))
                tier = int(input("  New membership tier (1–5): "))
                scheduler.updatePassengerTier(pid, tier)
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 5:
            try:
                did = int(input("  Driver ID to mark unavailable: "))
                scheduler.driverUnavailable(did)
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 6:
            print("Goodbye!")

        else:
            print("Invalid option, try again!")