import numpy as np
import linklists

# WARNING: THIS FILE CONTAINS CODE FROM PAST WORKSHOPS
# From Workshop 7: Hash Tables

NEVER_USED   =  0 # slot has never held a record (search can stop at this marker)
USED         =  1 # slot currently holds a record
OLD_USED = -1 # tombstone marker for deleted slots (allows probing to continue)

LOAD_FACTOR_THRESHOLD = 0.7   # resize / warn when load exceeds this
LOAD_PRINT_INTERVAL   = 10    # print load factor every N inserts

VALID_MEMBERSHIP_TIERS    = (1, 2, 3, 4, 5) # 1 = Platinum (highest) 5 = Standard (lowest)
VALID_DRIVER_STATUSES     = ("Available", "Busy", "Offline")


class PassengerRecord():
    """
    passengerID
    name
    pickupLocation
    membershipTier
    phoneNumber (for realism)
    """
    def __init__(self, passengerID, name, pickupLocation, membershipTier, phoneNumber=""):
        try:
            self._validate(passengerID, name, pickupLocation, membershipTier)
            self.passengerID    = int(passengerID)
            self.name           = str(name).strip()
            self.pickupLocation = str(pickupLocation).strip()
            self.membershipTier = int(membershipTier)
            self.phoneNumber    = str(phoneNumber).strip()
        except Exception as e:
            raise Exception(f"PassengerRecord error: {e}")

    def _validate(self, passengerID, name, pickupLocation, membershipTier):
        try:
            int(passengerID)
        except (ValueError, TypeError):
            raise Exception("PassengerID must be an integer")
        if not str(name).strip():
            raise Exception("Name must not be empty")
        if not str(pickupLocation).strip():
            raise Exception("PickupLocation must not be empty")
        try:
            tier = int(membershipTier)
        except (ValueError, TypeError):
            raise Exception("MembershipTier must be an integer")
        if tier not in VALID_MEMBERSHIP_TIERS:
            raise Exception(f"MembershipTier must be one of {VALID_MEMBERSHIP_TIERS}")

    def getKey(self):
        return self.passengerID

    def __str__(self):
        tierLabel = {1:"Platinum", 2:"Gold", 3:"Silver", 4:"Bronze", 5:"Standard"}
        return (f"Passenger [{self.passengerID}] | {self.name} | "
                f"Pickup: {self.pickupLocation} | "
                f"Tier: {self.membershipTier} ({tierLabel[self.membershipTier]}) | "
                f"Phone: {self.phoneNumber if self.phoneNumber else 'N/A'}")


class DriverRecord():
    """
    driverID
    name
    currentLocation
    availabilityStatus
    vehicleType (optional, default "Sedan")
    rating (optional, default 5.0)
    """
    def __init__(self, driverID, name, currentLocation,
                 availabilityStatus, vehicleType="Sedan", rating=5.0):
        try:
            self._validate(driverID, name, currentLocation,
                           availabilityStatus, rating)
            self.driverID           = int(driverID)
            self.name               = str(name).strip()
            self.currentLocation    = str(currentLocation).strip()
            self.availabilityStatus = str(availabilityStatus).strip()
            self.vehicleType        = str(vehicleType).strip()
            self.rating             = float(rating)
        except Exception as e:
            raise Exception(f"DriverRecord error: {e}")

    def _validate(self, driverID, name, currentLocation,
                  availabilityStatus, rating):
        try:
            int(driverID)
        except (ValueError, TypeError):
            raise Exception("DriverID must be an integer")
        if not str(name).strip():
            raise Exception("Name must not be empty")
        if not str(currentLocation).strip():
            raise Exception("CurrentLocation must not be empty")
        if str(availabilityStatus).strip() not in VALID_DRIVER_STATUSES:
            raise Exception(f"AvailabilityStatus must be one of {VALID_DRIVER_STATUSES}")
        try:
            r = float(rating)
            if not (0.0 <= r <= 5.0):
                raise Exception("Rating must be between 0.0 and 5.0")
        except (ValueError, TypeError):
            raise Exception("Rating must be a number")

    def getKey(self):
        return self.driverID

    def __str__(self):
        return (f"Driver   [{self.driverID}] | {self.name} | "
                f"Location: {self.currentLocation} | "
                f"Status: {self.availabilityStatus} | "
                f"Vehicle: {self.vehicleType} | "
                f"Rating: {self.rating:.1f}")


class HashEntry():
    """Single slot in the hash table (linear probing)."""
    def __init__(self):
        self.key   = None
        self.value = None # PassengerRecord or DriverRecord
        self.state = NEVER_USED # 0 = never used, 1 = used, -1 = formerly used

    def setEntry(self, key, value):
        self.key   = key
        self.value = value
        self.state = USED

    def removeEntry(self):
        self.key   = None
        self.value = None
        self.state = OLD_USED



class HashTable():
    """
    Linear-probing hash table
    Linear probing is chosen over chaining because:
    - It keeps all data in a single numpy array (cache-friendly, no linked list
      overhead per slot).
    - O(1) expected insert / search / delete.
    - Simpler to reason about load factor thresholds.
    Clustering is mitigated by:
    - Sizing the table with a prime number (reduces periodic clustering).
    - Keeping load factor ≤ 0.7 (triggers a resize warning/auto-resize).
    - Using a secondary step hash (double-hashing probe) to spread probes.

    Parameters
    ----------
    tableSize : int – requested capacity; rounded up to next prime internally.
    """

    def __init__(self, tableSize=100):
        try:
            actualSize       = self._nextPrime(tableSize)
            # numpy array of HashEntry objects (dtype=object so entries are refs)
            self._hashArray  = np.empty(actualSize, dtype=object)
            for i in range(actualSize):
                self._hashArray[i] = HashEntry()
            self._count          = 0
            self._insertsSinceLog = 0
        except Exception as e:
            raise Exception(f"HashTable init error: {e}")

    def insert(self, record):
        """
        Insert a PassengerRecord or DriverRecord.
        Duplicates: existing record is updated with a warning message.
        Prints load factor every LOAD_PRINT_INTERVAL inserts.
        """
        try:
            key = record.getKey()
            self._validateKey(key)

            # check for duplicate – update if found
            idx = self._findKey(key)
            if idx != -1:
                print(f"  [Hash] Duplicate key {key}: record updated.")
                self._hashArray[idx].setEntry(key, record)
                return

            # find an empty/formerly-used slot
            emptyIdx = self._findEmpty(key)
            if emptyIdx == -1:
                raise Exception("Hash table is full – cannot insert")

            self._hashArray[emptyIdx].setEntry(key, record)
            self._count += 1
            self._insertsSinceLog += 1

            # print load factor every N inserts
            if self._insertsSinceLog >= LOAD_PRINT_INTERVAL:
                print(f"  [Hash] Load factor after {self._count} records: "
                      f"{self.getLoadFactor():.2f}")
                self._insertsSinceLog = 0

            # warn (and auto-resize) if load factor exceeds threshold
            if self.getLoadFactor() > LOAD_FACTOR_THRESHOLD:
                print(f"  [Hash] WARNING: Load factor {self.getLoadFactor():.2f} "
                      f"exceeds threshold {LOAD_FACTOR_THRESHOLD}. Resizing...")
                self._resize(len(self._hashArray) * 2)

        except Exception as e:
            raise Exception(f"Error inserting record: {e}")

    def search(self, key):
        """
        Return the record for key, or raise an exception if not found.
        O(1) expected time.
        """
        try:
            self._validateKey(key)
            idx = self._findKey(int(key))
            if idx == -1:
                raise Exception(f"Key {key} not found in hash table")
            return self._hashArray[idx].value
        except Exception as e:
            raise Exception(f"Error searching record: {e}")

    def delete(self, key):
        """
        Remove the record for key.  Marks slot as OLD_USED so probing
        chains remain intact.  Raises exception if key not found.
        O(1) expected time.
        """
        try:
            self._validateKey(key)
            idx = self._findKey(int(key))
            if idx == -1:
                raise Exception(f"Key {key} not found – nothing deleted")
            self._hashArray[idx].removeEntry()
            self._count -= 1
            print(f"  [Hash] Record with key {key} deleted successfully.")
        except Exception as e:
            raise Exception(f"Error deleting record: {e}")

    def getLoadFactor(self):
        """Returns current load factor (count / table size)."""
        return self._count / len(self._hashArray)

    def display(self):
        """Print every occupied slot with its index."""
        try:
            print(f"\n  Table size: {len(self._hashArray)} | "
                  f"Records: {self._count} | "
                  f"Load factor: {self.getLoadFactor():.2f}")
            print(f"  {'Idx':>6}  {'Key':>8}  Record")
            print(f"  {'-'*70}")
            for i in range(len(self._hashArray)):
                if self._hashArray[i].state == USED:
                    print(f"  {i:>6}  {self._hashArray[i].key:>8}  "
                          f"{self._hashArray[i].value}")
        except Exception as e:
            raise Exception(f"Error displaying hash table: {e}")

    def demonstrateCollision(self, key1, key2):
        """
        Show the probe sequence for two keys that map to the same initial slot,
        illustrating how linear probing resolves the collision.
        """
        try:
            size  = len(self._hashArray)
            h1    = self._hash(key1)
            h2    = self._hash(key2)
            step1 = self._stepHash(key1)
            step2 = self._stepHash(key2)
            print(f"\n  === Collision Demonstration ===")
            print(f"  Key {key1}: initial slot = {h1},  probe step = {step1}")
            print(f"  Key {key2}: initial slot = {h2},  probe step = {step2}")
            if h1 == h2:
                print(f"  --> COLLISION: both keys hash to slot {h1}")
                probe = (h2 + step2) % size
                print(f"  --> Key {key2} probes forward to slot {probe}")
            else:
                print(f"  --> No collision between these two keys at insertion time")
        except Exception as e:
            raise Exception(f"Error in collision demonstration: {e}")


    def _hash(self, key):
        """
        Primary hash: key modulo table size.
        Table size is prime → reduces clustering by avoiding common factors
        between key patterns and the modulus.
        """
        return int(key) % len(self._hashArray)

    def _stepHash(self, key):
        """
        Secondary hash used as the probe step (double hashing).
        step = prime2 - (key % prime2), where prime2 < table size.
        Guarantees step != 0 and varies per key, reducing primary clustering.
        """
        prime2 = self._nextPrime(len(self._hashArray) // 2)
        step   = prime2 - (int(key) % prime2)
        return step if step != 0 else 1

    def _findKey(self, key):
        """
        Return the index of key in the table, or -1 if not found.
        Stops at NEVER_USED slots (key can't be further along the chain).
        """
        hashIdx  = self._hash(key)
        origIdx  = hashIdx
        step     = self._stepHash(key)
        found    = False
        giveUp   = False

        while not found and not giveUp:
            state = self._hashArray[hashIdx].state
            if state == NEVER_USED:
                giveUp = True
            elif state == USED and self._hashArray[hashIdx].key == key:
                found = True
            else:
                hashIdx = (hashIdx + step) % len(self._hashArray)
                if hashIdx == origIdx:
                    giveUp = True

        return hashIdx if found else -1

    def _findEmpty(self, key):
        """
        Return the index of the first empty (NEVER_USED or OLD_USED) slot
        following the probe sequence for key, or -1 if table is full.
        """
        hashIdx = self._hash(key)
        origIdx = hashIdx
        step    = self._stepHash(key)
        found   = False
        giveUp  = False

        while not found and not giveUp:
            state = self._hashArray[hashIdx].state
            if state == NEVER_USED or state == OLD_USED:
                found = True
            else:
                hashIdx = (hashIdx + step) % len(self._hashArray)
                if hashIdx == origIdx:
                    giveUp = True

        return hashIdx if found else -1

    def _nextPrime(self, startVal):
        """
        Return the smallest prime >= startVal.
        Only odd candidates are tested; divisors checked up to sqrt(candidate).
        """
        try:
            startVal = int(startVal)
            if startVal < 2:
                return 2
            candidate = startVal if startVal % 2 != 0 else startVal + 1
            isPrime   = False
            while not isPrime:
                isPrime  = True
                rootVal  = int(candidate ** 0.5)
                ii       = 3
                while ii <= rootVal and isPrime:
                    if candidate % ii == 0:
                        isPrime = False
                    else:
                        ii += 2
                if not isPrime:
                    candidate += 2
            return candidate
        except Exception as e:
            raise Exception(f"Error finding next prime: {e}")

    def _resize(self, newSize):
        """
        Rebuild the hash table at newSize (rounded to next prime).
        All existing USED entries are re-inserted into the new array.
        Must re-hash because the modulus changes with table size.
        """
        try:
            oldArray  = self._hashArray
            actualSize = self._nextPrime(newSize)
            self._hashArray = np.empty(actualSize, dtype=object)
            for i in range(actualSize):
                self._hashArray[i] = HashEntry()
            self._count = 0

            for i in range(len(oldArray)):
                if oldArray[i].state == USED:
                    emptyIdx = self._findEmpty(oldArray[i].key)
                    self._hashArray[emptyIdx].setEntry(
                        oldArray[i].key, oldArray[i].value)
                    self._count += 1

            print(f"  [Hash] Resized to {actualSize} slots. "
                  f"New load factor: {self.getLoadFactor():.2f}")
        except Exception as e:
            raise Exception(f"Error resizing hash table: {e}")

    def _validateKey(self, key):
        try:
            int(key)
        except (ValueError, TypeError):
            raise Exception(f"Key must be an integer, got: {key}")



def _inputInt(prompt, minVal=None, maxVal=None):
    """Prompt until a valid integer (within optional range) is entered."""
    while True:
        try:
            val = int(input(prompt))
            if minVal is not None and val < minVal:
                print(f"  Value must be >= {minVal}")
            elif maxVal is not None and val > maxVal:
                print(f"  Value must be <= {maxVal}")
            else:
                return val
        except ValueError:
            print("  Please enter a valid integer.")

def _inputStr(prompt, choices=None):
    """Prompt until a non-empty string (optionally from choices) is entered."""
    while True:
        val = input(prompt).strip()
        if not val:
            print("  Input must not be empty.")
        elif choices and val not in choices:
            print(f"  Must be one of: {choices}")
        else:
            return val

def _inputFloat(prompt, minVal=0.0, maxVal=5.0):
    """Prompt until a valid float within range is entered."""
    while True:
        try:
            val = float(input(prompt))
            if not (minVal <= val <= maxVal):
                print(f"  Value must be between {minVal} and {maxVal}")
            else:
                return val
        except ValueError:
            print("  Please enter a valid number.")



def menu(passengerTable, driverTable):
    option = 0
    while option != 9:
        print("\n=== ZipRide Hash Table Menu ===")
        print("--- Passengers ---")
        print("1. Add passenger")
        print("2. Search passenger")
        print("3. Delete passenger")
        print("4. Display all passengers")
        print("--- Drivers ---")
        print("5. Add driver")
        print("6. Search driver")
        print("7. Delete driver")
        print("8. Display all drivers")
        print("---")
        print("9. Quit")

        try:
            option = int(input("Enter option: "))
        except ValueError:
            print("Invalid input, please enter a number!")
            option = 0
            continue

        # ---- Passengers ----
        if option == 1:
            try:
                pid   = _inputInt("  Passenger ID (integer): ") # '_' used to indicate this is a helper (in lecture slides)
                name  = _inputStr("  Name: ")
                loc   = _inputStr("  Pickup location (graph node): ")
                tier  = _inputInt("  Membership tier (1=Platinum … 5=Standard): ", 1, 5)
                phone = input("  Phone number (optional, press Enter to skip): ").strip()
                rec   = PassengerRecord(pid, name, loc, tier, phone)
                passengerTable.insert(rec)
                print(f"  Passenger {pid} added.")
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 2:
            try:
                pid = _inputInt("  Passenger ID to search: ")
                rec = passengerTable.search(pid)
                print(f"  Found: {rec}")
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 3:
            try:
                pid = _inputInt("  Passenger ID to delete: ")
                passengerTable.delete(pid)
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 4:
            try:
                print("\n=== Passenger Table ===")
                passengerTable.display()
            except Exception as e:
                print(f"  Error: {e}")

        # ---- Drivers ----
        elif option == 5:
            try:
                did     = _inputInt("  Driver ID (integer): ")
                name    = _inputStr("  Name: ")
                loc     = _inputStr("  Current location (graph node): ")
                status  = _inputStr(f"  Availability status {VALID_DRIVER_STATUSES}: ",
                                    choices=list(VALID_DRIVER_STATUSES))
                vehicle = input("  Vehicle type (optional, Enter for 'Sedan'): ").strip() or "Sedan"
                rating  = _inputFloat("  Rating (0.0–5.0, Enter for 5.0): ")
                rec     = DriverRecord(did, name, loc, status, vehicle, rating)
                driverTable.insert(rec)
                print(f"  Driver {did} added.")
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 6:
            try:
                did = _inputInt("  Driver ID to search: ")
                rec = driverTable.search(did)
                print(f"  Found: {rec}")
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 7:
            try:
                did = _inputInt("  Driver ID to delete: ")
                driverTable.delete(did)
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 8:
            try:
                print("\n=== Driver Table ===")
                driverTable.display()
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 9:
            print("Goodbye!")

        else:
            print("Invalid option, try again!")