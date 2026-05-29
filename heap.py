import numpy as np

# ================================================================== CONSTANTS

INITIAL_CAPACITY = 50   # numpy array size; doubled on resize if needed

# ================================================================== PICKUP REQUEST

class PickupRequest():
    """
    Represents a single passenger pickup request.

    Fields
    ------
    passengerID      : int   - unique passenger identifier
    passengerName    : str   - passenger name (for display)
    pickupLocation   : str   - graph node label
    membershipTier   : int   - 1 (Platinum) to 5 (Standard)
    assignedDriverID : int   - driver selected for this request
    assignedDriverName: str  - driver name (for display)
    estimatedTime    : float - shortest driving time T (from Dijkstra)
    priority         : float - (6 - M) + 1000 / T
    """
    def __init__(self, passengerID, passengerName, pickupLocation,
                 membershipTier, assignedDriverID, assignedDriverName,
                 estimatedTime):
        try:
            self._validate(passengerID, membershipTier, estimatedTime)
            self.passengerID       = int(passengerID)
            self.passengerName     = str(passengerName).strip()
            self.pickupLocation    = str(pickupLocation).strip()
            self.membershipTier    = int(membershipTier)
            self.assignedDriverID  = int(assignedDriverID)
            self.assignedDriverName= str(assignedDriverName).strip()
            self.estimatedTime     = float(estimatedTime)
            self.priority          = self._calcPriority(membershipTier,
                                                        estimatedTime)
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
            raise Exception("MembershipTier must be an integer 1–5")
        try:
            t = float(estimatedTime)
            if t < 0:
                raise Exception("EstimatedPickupTime must be >= 0")
        except (ValueError, TypeError):
            raise Exception("EstimatedPickupTime must be a number")

    def _calcPriority(self, membershipTier, estimatedTime):
        """
        Priority = (6 - M) + 1000 / T
        Special case: if T == 0 (driver already at pickup location),
        we use a large constant (10000) so the request still scores
        highly without a division-by-zero error.
        """
        t = float(estimatedTime)
        if t == 0:
            timeBonus = 10000.0
        else:
            timeBonus = 1000.0 / t
        return (6 - int(membershipTier)) + timeBonus

    def updateTier(self, newTier):
        """Recompute priority after a membership tier change."""
        try:
            tier = int(newTier)
            if tier not in (1, 2, 3, 4, 5):
                raise Exception("MembershipTier must be 1–5")
            self.membershipTier = tier
            self.priority = self._calcPriority(tier, self.estimatedTime)
        except Exception as e:
            raise Exception(f"Error updating tier: {e}")

    def __str__(self):
        tierLabel = {1:"Platinum", 2:"Gold", 3:"Silver",
                     4:"Bronze",  5:"Standard"}
        return (f"Passenger {self.passengerID} ({self.passengerName}) | "
                f"Pickup: {self.pickupLocation} | "
                f"Tier: {self.membershipTier} ({tierLabel[self.membershipTier]}) | "
                f"Driver: {self.assignedDriverID} ({self.assignedDriverName}) | "
                f"ETA: {self.estimatedTime:.1f} min | "
                f"Priority: {self.priority:.2f}")


# ================================================================== MAX HEAP
#
# Max-Heap choice rationale
# -------------------------
# A Max-Heap is used so the highest-priority request always sits at index 0
# and can be extracted in O(log n) without any key inversion.
# Higher priority = more urgent dispatch (high-tier passenger OR nearest driver),
# so the root always holds the request that should be dispatched next.
# A Min-Heap would require negating the priority key, making the code less
# readable and the priority formula harder to reason about.

class PickupHeap():
    """
    Array-based Max-Heap for pickup request scheduling.
    Backed by a numpy array of PickupRequest objects (dtype=object).

    Operations
    ----------
    insert(request)        O(log n)  – add request, percolate up
    peek()                 O(1)      – view highest-priority request
    extract_priority()     O(log n)  – remove & return highest-priority request
    update_tier(pid, tier) O(n)      – find, update, re-heapify
    remove_driver(driverID)O(n)      – remove all requests for a given driver
    """

    def __init__(self, capacity=INITIAL_CAPACITY):
        try:
            self._capacity = int(capacity)
            # numpy object array holds PickupRequest references
            self._heap  = np.empty(self._capacity, dtype=object)
            self._count = 0
        except Exception as e:
            raise Exception(f"PickupHeap init error: {e}")

    # -------------------------------------------------------------- public API

    def insert(self, request):
        """
        Add a PickupRequest to the heap and percolate up.
        Prints the heap array after insertion.
        """
        try:
            if not isinstance(request, PickupRequest):
                raise Exception("Only PickupRequest objects can be inserted")

            # resize if needed
            if self._count >= self._capacity:
                self._resize()

            # place at end, then percolate up
            self._heap[self._count] = request
            self._count += 1
            self._percolateUp(self._count - 1)

            print(f"\n  [Heap] Inserted: {request}")
            self._printHeap()

        except Exception as e:
            raise Exception(f"Error inserting request: {e}")

    def peek(self):
        """Return the highest-priority request without removing it."""
        try:
            if self._count == 0:
                raise Exception("Heap is empty – nothing to peek")
            return self._heap[0]
        except Exception as e:
            raise Exception(f"Error peeking heap: {e}")

    def extract_priority(self):
        """
        Remove and return the highest-priority request.
        Swaps root with last element, shrinks count, percolates down.
        Prints the heap array after extraction.
        """
        try:
            if self._count == 0:
                raise Exception("Heap is empty – nothing to extract")

            top = self._heap[0]

            # move last element to root and shrink
            self._count -= 1
            self._heap[0] = self._heap[self._count]
            self._heap[self._count] = None

            if self._count > 0:
                self._percolateDown(0)

            print(f"\n  [Heap] Extracted: {top}")
            self._printHeap()
            return top

        except Exception as e:
            raise Exception(f"Error extracting from heap: {e}")

    def update_tier(self, passengerID, newTier):
        """
        Find the request for passengerID, update its membership tier,
        recompute priority, and restore heap order (full heapify).
        Used when a passenger's tier changes mid-queue.
        """
        try:
            idx = self._findByPassengerID(passengerID)
            if idx == -1:
                raise Exception(f"Passenger {passengerID} not found in heap")
            self._heap[idx].updateTier(newTier)
            print(f"\n  [Heap] Tier updated for passenger {passengerID} "
                  f"-> new priority: {self._heap[idx].priority:.2f}")
            self._heapify()
            self._printHeap()
        except Exception as e:
            raise Exception(f"Error updating tier: {e}")

    def remove_driver(self, driverID):
        """
        Remove all requests assigned to driverID (driver went Busy/Offline).
        Rebuilds the heap after removal.
        """
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
                    # don't advance i – recheck the swapped element
                else:
                    i += 1
            if removed == 0:
                print(f"  [Heap] No requests found for driver {driverID}.")
            else:
                print(f"  [Heap] Removed {removed} request(s) for driver "
                      f"{driverID} (driver no longer available).")
                self._heapify()
                self._printHeap()
        except Exception as e:
            raise Exception(f"Error removing driver requests: {e}")

    def isEmpty(self):
        return self._count == 0

    def size(self):
        return self._count

    # -------------------------------------------------------------- private

    def _percolateUp(self, idx):
        """Swap upward while child priority > parent priority."""
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

    def _percolateDown(self, idx):
        """Swap downward while parent priority < largest child priority."""
        current = idx
        done = False
        while not done:
            left  = 2 * current + 1
            right = 2 * current + 2
            largest = current

            if left < self._count and \
               self._heap[left].priority > self._heap[largest].priority:
                largest = left
            if right < self._count and \
               self._heap[right].priority > self._heap[largest].priority:
                largest = right

            if largest != current:
                self._heap[current], self._heap[largest] = \
                    self._heap[largest], self._heap[current]
                current = largest
            else:
                done = True

    def _heapify(self):
        """Rebuild heap property from scratch (used after bulk changes)."""
        i = (self._count // 2) - 1
        while i >= 0:
            self._percolateDown(i)
            i -= 1

    def _findByPassengerID(self, passengerID):
        """Linear scan for a passenger ID; returns index or -1."""
        for i in range(self._count):
            if self._heap[i].passengerID == passengerID:
                return i
        return -1

    def _resize(self):
        """Double capacity when heap is full."""
        try:
            newCapacity = self._capacity * 2
            newHeap = np.empty(newCapacity, dtype=object)
            for i in range(self._count):
                newHeap[i] = self._heap[i]
            self._heap = newHeap
            self._capacity = newCapacity
            print(f"  [Heap] Resized to capacity {newCapacity}")
        except Exception as e:
            raise Exception(f"Error resizing heap: {e}")

    def _printHeap(self):
        """Print the current heap array and a simple tree layout."""
        print(f"  [Heap] Size: {self._count} | Contents (index: priority | passenger):")
        if self._count == 0:
            print("    (empty)")
            return

        # flat array view
        for i in range(self._count):
            req = self._heap[i]
            print(f"    [{i:>2}] P={req.priority:>8.2f} | "
                  f"ID={req.passengerID} ({req.passengerName}) | "
                  f"Tier={req.membershipTier} | "
                  f"ETA={req.estimatedTime:.1f}min | "
                  f"Driver={req.assignedDriverName}")

        # tree layout (up to 4 levels for readability)
        print(f"  [Heap] Tree view:")
        level = 0
        idx   = 0
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
            indent = "    " + "  " * (3 - level)
            row = indent + "  ".join(str(levelNodes[j])
                                     for j in range(filled))
            print(row)
            idx  += levelSize
            level += 1
        if idx < self._count:
            print(f"    ... ({self._count - idx} more nodes)")


# ================================================================== SCHEDULER

class ZipRideScheduler():
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
                print(f"\n  [Scheduler] No available drivers can reach "
                      f"{pickupLoc}. Request for passenger "
                      f"{passengerID} rejected.")
                return None

            print(f"\n  [Scheduler] Passenger {passengerID} "
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
            print(f"\n  [Scheduler] DISPATCHING: {req}")

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
            print(f"\n  [Scheduler] Next to dispatch: {req}")
            return req
        except Exception as e:
            raise Exception(f"Error peeking scheduler: {e}")

    def heapSize(self):
        return self._heap.size()


# ================================================================== MENU

def menu(scheduler):
    option = 0
    while option != 6:
        print("\n=== ZipRide Scheduler Menu ===")
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