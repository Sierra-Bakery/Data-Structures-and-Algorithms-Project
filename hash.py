import numpy as np
import linklists

# WARNING: THIS FILE CONTAINS CODE FROM PAST WORKSHOPS
# From Workshop 7: Hash Tables

# Globals for slot states in the hash table
NEVER_USED =  0 # slot has never held a record (search can stop at this marker)
USED =  1 # slot currently holds a record
OLD_USED = -1 # tombstone marker for deleted slots (allows probing to )

# Globals for hash table behavior
LOAD_FACTOR_THRESHOLD = 0.7   # resize / warn when load exceeds this
LOAD_PRINT_INTERVAL = 10    # print load factor every N inserts

# Globals for valid field values for tiers and statuses
VALID_MEMBERSHIP_TIERS = (1, 2, 3, 4, 5) # 1 = Platinum (highest) 5 = Standard (lowest)
VALID_DRIVER_STATUSES = ("Available", "Busy", "Offline")


class PassengerRecord():
    def __init__(self, passengerID, name, pickupLocation, membershipTier, phoneNumber=""):
        try:
            self._validate(passengerID, name, pickupLocation, membershipTier)
            self.passengerID = int(passengerID)
            self.name = str(name)
            self.pickupLocation = str(pickupLocation)
            self.membershipTier = int(membershipTier)
            self.phoneNumber = str(phoneNumber)
            
        except Exception as e:
            raise Exception(f"PassengerRecord error: {e}")

    def _validate(self, passengerID, name, pickupLocation, membershipTier):
        try:
            int(passengerID)
            
        except (ValueError, TypeError):
            raise Exception("PassengerID must be an integer")
        
        if not str(name):
            raise Exception("Name must not be empty")
        
        if not str(pickupLocation):
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
        tierName = {1:"Platinum", 2:"Gold", 3:"Silver", 4:"Bronze", 5:"Standard"}
        return (f"Passenger [{self.passengerID}] | {self.name} | "f"Pickup: {self.pickupLocation} | "f"Tier: {self.membershipTier} ({tierName[self.membershipTier]}) | "
                f"Phone: {self.phoneNumber if self.phoneNumber else 'N/A'}")


class DriverRecord():
    def __init__(self, driverID, name, currentLocation, availabilityStatus, vehicleType="Sedan", rating=5.0):
        try:
            self._validate(driverID, name, currentLocation, availabilityStatus, rating)
            self.driverID = int(driverID)
            self.name = str(name)
            self.currentLocation = str(currentLocation)
            self.availabilityStatus = str(availabilityStatus)
            self.vehicleType = str(vehicleType)
            self.rating = float(rating)
            
        except Exception as e:
            raise Exception(f"DriverRecord error: {e}")

    def _validate(self, driverID, name, currentLocation, availabilityStatus, rating):
        try:
            int(driverID)
            
        except (ValueError, TypeError):
            raise Exception("DriverID must be an integer")
        
        if not str(name):
            raise Exception("Name must not be empty")
        
        if not str(currentLocation):
            raise Exception("CurrentLocation must not be empty")
        
        if str(availabilityStatus) not in VALID_DRIVER_STATUSES:
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
        return (f"Driver   [{self.driverID}] | {self.name} | " f"Location: {self.currentLocation} | "
                f"Status: {self.availabilityStatus} | " f"Vehicle: {self.vehicleType} | " f"Rating: {self.rating:.1f}")


class HashEntry():
    # single entry in the hash table
    def __init__(self):
        self.key = None
        self.value = None # PassengerRecord or DriverRecord
        self.state = NEVER_USED

    def setEntry(self, key, value):
        self.key = key
        self.value = value
        self.state = USED

    def removeEntry(self):
        self.key = None
        self.value = None
        self.state = OLD_USED



class HashTable():
    def __init__(self, tableSize=100):
        try:
            realSize = self._nextPrime(tableSize)
            self._hashArray  = np.empty(realSize, dtype=object)
            
            for i in range(realSize):
                self._hashArray[i] = HashEntry()
                
            self._count = 0
            self._insertsSinceLog = 0
            
        except Exception as e:
            raise Exception(f"HashTable init error: {e}")

    def insert(self, record):
        try:
            key = record.getKey()
            self._validateKey(key)

            # check for duplicate key first and update record if found
            index = self._findKey(key)
            
            if index != -1:
                print(f" Duplicate key {key}")
                self._hashArray[index].setEntry(key, record)
                return

            # find an empty or formerly-used slot
            emptyIndex = self._findEmpty(key)
            
            if emptyIndex == -1:
                raise Exception("Hash table is full")

            self._hashArray[emptyIndex].setEntry(key, record)
            self._count += 1
            self._insertsSinceLog += 1

            # print load factor every N inserts
            if self._insertsSinceLog >= LOAD_PRINT_INTERVAL:
                print(f" Load factor after {self._count} records: " f"{self.getLoadFactor():.2f}")
                
                self._insertsSinceLog = 0

            # warn (and auto-resize) if load factor exceeds threshold
            if self.getLoadFactor() > LOAD_FACTOR_THRESHOLD:
                print(f" WARNING: Load factor {self.getLoadFactor():.2f} " f"exceeds threshold {LOAD_FACTOR_THRESHOLD}")
                self._resize(len(self._hashArray) * 2)

        except Exception as e:
            raise Exception(f"Error inserting record: {e}")

    def search(self, key):
        try:
            self._validateKey(key)
            index = self._findKey(int(key))
            
            if index == -1:
                raise Exception(f" {key} not found in hash table")
            
            return self._hashArray[index].value
        
        except Exception as e:
            raise Exception(f"Error searching record: {e}")

    def delete(self, key):
        try:
            self._validateKey(key)
            index = self._findKey(int(key))
            
            if index == -1:
                raise Exception(f"Key {key} not found")
            
            self._hashArray[index].removeEntry()
            self._count -= 1
            print(f"Record with key {key} deleted successfully.")
            
        except Exception as e:
            raise Exception(f"Error deleting record: {e}")

    def getLoadFactor(self):
        # Returns current load factor
        return self._count / len(self._hashArray)

    def display(self):
        # Print every occupied slot with its index
        try:
            print(f"  Table size: {len(self._hashArray)} | " f"Records: {self._count} | " f"Load factor: {self.getLoadFactor():.2f}")
            print(f" {'index':>6} {'Key':>8} Record")
            print(f" {'-'*70}")
            
            for i in range(len(self._hashArray)):
                # Only print slots that are currently in use
                if self._hashArray[i].state == USED:
                    print(f" {i:>6} {self._hashArray[i].key:>8} " f"{self._hashArray[i].value}")
                    
        except Exception as e:
            raise Exception(f"Error displaying hash table: {e}")

    def demonstrateCollision(self, key1, key2):
        # Show the probe sequence for two keys that map to the same initial slot
        # showing how linear probing resolves the collision
        try:
            size = len(self._hashArray)
            h1 = self._hash(key1)
            h2 = self._hash(key2)
            step1 = self._stepHash(key1)
            step2 = self._stepHash(key2)
            
            print(f"  === Collision Demonstration ===")
            print(f" Key {key1}: initial slot = {h1}, probe step = {step1}")
            print(f" Key {key2}: initial slot = {h2}, probe step = {step2}")
            
            if h1 == h2:
                print(f"COLLISION {h1}")
                probe = (h2 + step2) % size
                print(f"Key {key2} probes forward to slot {probe}")
                
            else:
                print(f"No collision")
                
        except Exception as e:
            raise Exception(f"Error in collision demo {e}")


    def _hash(self, key):
        # Primary hash key modulo table size
        return int(key) % len(self._hashArray)

    def _stepHash(self, key):
        # Secondary hash used as the probe step
        # logic ensures step doesn not equal 0 and unique per key and reduces primary clustering
        prime2 = self._nextPrime(len(self._hashArray) // 2)
        step   = prime2 - (int(key) % prime2)
        return step if step != 0 else 1

    def _findKey(self, key):
        hashIndex = self._hash(key)
        originIndex = hashIndex
        step = self._stepHash(key)
        found = False
        giveUp = False

        while not found and not giveUp:
            state = self._hashArray[hashIndex].state
            
            if state == NEVER_USED:
                giveUp = True
                
            elif state == USED and self._hashArray[hashIndex].key == key:
                found = True
                
            else:
                hashIndex = (hashIndex + step) % len(self._hashArray)
                if hashIndex == originIndex:
                    giveUp = True

        return hashIndex if found else -1

    def _findEmpty(self, key):
        hashIndex = self._hash(key)
        originIndex = hashIndex
        step = self._stepHash(key)
        found = False
        giveUp = False

        while not found and not giveUp:
            state = self._hashArray[hashIndex].state
            if state == NEVER_USED or state == OLD_USED:
                found = True
                
            else:
                hashIndex = (hashIndex + step) % len(self._hashArray)
                if hashIndex == originIndex:
                    giveUp = True

        return hashIndex if found else -1

    def _nextPrime(self, startValue):
        # Returns the next prime number >= startValue
        try:
            startValue = int(startValue)
            if startValue < 2:
                return 2
            candidate = startValue if startValue % 2 != 0 else startValue + 1
            isPrime = False
            
            while not isPrime:
                isPrime = True
                rootVal = int(candidate ** 0.5)
                ii = 3
                
                # check divisibility by 2 first, then test odd factors up to root of candidate
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
        # Resizes the hash table to the next prime number >= newSize and rehashes all existing records
        try:
            oldArray  = self._hashArray
            realSize = self._nextPrime(newSize)
            self._hashArray = np.empty(realSize, dtype=object)
            
            for i in range(realSize):
                self._hashArray[i] = HashEntry()
                
            self._count = 0

            for i in range(len(oldArray)):
                if oldArray[i].state == USED:
                    emptyIndex = self._findEmpty(oldArray[i].key)
                    self._hashArray[emptyIndex].setEntry(oldArray[i].key, oldArray[i].value)
                    self._count += 1

            print(f"Resized to {realSize} slots. " f"New load factor: {self.getLoadFactor():.2f}")
            
        except Exception as e:
            raise Exception(f"Error resizing hash table {e}")

    def _validateKey(self, key):
        try:
            int(key)
            
        except (ValueError, TypeError):
            raise Exception(f"Key must be an integer")



def _inputInt(prompt, minVal = None, maxVal = None):
    while True:
        try:
            value = int(input(prompt))
            
            if minVal is not None and value < minVal:
                print(f"Value must be >= {minVal}")
                
            elif maxVal is not None and value > maxVal:
                print(f"Value must be <= {maxVal}")
                
            else:
                return value
            
        except ValueError:
            print("Please enter a valid integer.")

def _inputStr(prompt, choices = None):
    while True:
        value = input(prompt)
        
        if not value:
            print("Input must not be empty.")
            
        elif choices and value not in choices:
            print(f"Must be one of: {choices}")
            
        else:
            return value

def _inputFloat(prompt, minVal = 0.0, maxVal = 5.0):
    while True:
        try:
            value = float(input(prompt))
            
            if not (minVal <= value <= maxVal):
                print(f"Value must be between {minVal} and {maxVal}")
                
            else:
                return value
            
        except ValueError:
            print("Please enter a valid number.")



def menu(passengerTable, driverTable):
    option = 0
    while option != 9:
        print("=== Hash Table ===")
        print("1 Add a passenger")
        print("2 Search for a passenger")
        print("3 Delete a passenger")
        print("4 Display all passengers")
        print("5 Add a driver")
        print("6 Search for a driver")
        print("7 Delete a driver")
        print("8 Display all drivers")
        print("9 Quit")

        try:
            option = int(input("Enter option: "))
            
        except ValueError:
            print("Invalid input, please enter a number!")
            option = 0
            

        if option == 1:
            try:
                # '_' used to indicate this is a helper (in lecture slides)
                pid = _inputInt("Passenger ID (integer): ") 
                name = _inputStr("Name: ")
                location = _inputStr("Pickup location (graph node): ")
                tier = _inputInt("Membership tier (1=Platinum … 5=Standard): ", 1, 5)
                phone = input("Phone number (optional, press Enter to skip): ")
                records = PassengerRecord(pid, name, location, tier, phone)
                passengerTable.insert(records)
                
                print(f" Passenger {pid} added.")
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 2:
            try:
                pid = _inputInt("Passenger ID to search: ")
                records = passengerTable.search(pid)
                print(f"  Found: {records}")
                
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 3:
            try:
                pid = _inputInt("Passenger ID to delete: ")
                passengerTable.delete(pid)
                
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 4:
            try:
                print("=== Passenger Table ===")
                passengerTable.display()
                
            except Exception as e:
                print(f"  Error: {e}")

        elif option == 5:
            try:
                did = _inputInt("Driver ID (integer): ")
                name = _inputStr("Name: ")
                location = _inputStr("Current location (graph node): ")
                status = _inputStr(f"Availability status {VALID_DRIVER_STATUSES}: ", choices=list(VALID_DRIVER_STATUSES))
                vehicle = input("Vehicle type (optional, Enter for 'Sedan'): ") or "Sedan"
                rating = _inputFloat("  Rating (0.0–5.0, Enter for 5.0): ")
                records = DriverRecord(did, name, location, status, vehicle, rating)
                driverTable.insert(records)
                print(f"Driver {did} added.")
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 6:
            try:
                did = _inputInt("Driver ID to search: ")
                records = driverTable.search(did)
                print(f"Found: {records}")
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 7:
            try:
                did = _inputInt("Driver ID to delete: ")
                driverTable.delete(did)
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 8:
            try:
                print("=== Driver Table ===")
                driverTable.display()
                
            except Exception as e:
                print(f"Error: {e}")

        elif option == 9:
            print("Goodbye!")

        else:
            print("Invalid option, try again!")