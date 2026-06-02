# Description: Linked list double classes for later use in the prigram
# Author: Dylan Baker 22368201
# Date: 30/05/2026

# WARNING: This file contains code from past workshop classes

class ListNode: #node class, acts as an object used by linked list class, contains value and pointer attributes
    def __init__(self, value):
        self.value = value
        self.next = None #pointer attribute, points to none as the data structure points to null
        self.prev = None #points to the previous node as it is a doubly linked list

class LinkedList:
    def __init__(self):
        #specifies the first and last node
        self.head = None 
        self.tail = None
        
    def isempty(self):
        return self.head is None #returns if the list is empty
        
    def insert_first(self, value):
        new_node = ListNode(value)
        
        if self.isempty():
            #means it is the only node in the list, so it is both the head and tail (new node)
            self.head = new_node
            self.tail = new_node
            
        else:
            #links new node to the current head
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
            
    def insert_last(self, value):
        #essentially the insert_first class but mirrored
        new_node = ListNode(value)
        
        if self.isempty():
            self.head = new_node
            self.tail = new_node
            
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
            
    def peek_first(self):
        if self.isempty():
            return
        
        else:
            return self.head.value #returns val ue
        
    def peek_last(self):
        if self.isempty(): #exception handling
            return
        
        else:
            return self.tail.value
        
    def remove_first(self):
        if self.isempty(): #exception handling
            return
        
        elif self.head == self.tail:
            #if head = tail then the head and tail nodes esentially get removed
            temphead = self.head.value #stores the head value tempoarily
            
            self.head = None 
            self.tail = None
            return temphead
        
        else:
            temphead = self.head.value
            self.head = self.head.next
            self.head.prev = None
            return temphead
        
    def remove_last(self):
        if self.isempty(): #exception handling
            return
        
        elif self.head == self.tail:
            temphead = self.head.value
            self.head = None
            self.tail = None
            return temphead
        
        else:
            temptail = self.tail.value
            self.tail = self.tail.prev
            self.tail.next = None
            return temptail
        
    def display(self):
        if self.isempty():
            print("Empty List")
            
        else:
            cur = self.head
            while cur is not None:
                print(cur.value)
                cur = cur.next #moves through the linked list

class Stack:
    def __init__(self): #constructor is simplified massively by LinkedList implementation
        self._list = LinkedList()  # LinkedList not List!

    def push(self, value):
        self._list.insert_first(value)

    def pop(self):
        value = self._list.peek_first()  # peeks first
        self._list.remove_first() #then removes
        return value

    def top(self):
        return self._list.peek_first()

    def is_empty(self):
        return self._list.isempty()

    def display(self):
        self._list.display()

class Queue:

    DEFAULT_CAPACITY = 100
    # Constructor

    def __init__(self):
        self._list = LinkedList()  # LinkedList

    def is_empty(self):
        return self._list.isempty()

    def enqueue(self, value):
        return self._list.insert_last(value)

    def dequeue(self):
        value = self._list.peek_first()
        self._list.remove_first()
        return value

    def peek(self):
        return self._list.peek_first()
    
    def display(self):
        self._list.display()

def menu():
    LL = LinkedList()
    choice = 0
    while choice != 6:
        print(" === LIST MENU ===")
        print("1. Insert First")
        print("2. Insert Last")
        print("3. Remove First")
        print("4. Remove Last")
        print("5. Display")
        print("6. Exit")
        
        choice = int(input("Enter your choice: "))
        if choice == 1:
            value = input("Enter value to insert at the beginning: ")
            LL.insert_first(value)
            
        elif choice == 2:
            value = input("Enter value to insert at the end: ")
            LL.insert_last(value)
            
        elif choice == 3:
            if not LL.isempty():
                removed_value = LL.remove_first()
                print("Removed value from the beginning:", removed_value)
                
            else:
                print("List is empty. Cannot remove.")
                
        elif choice == 4:
            if not LL.isempty():
                removed_value = LL.remove_last()
                print("Removed value from the end: ", removed_value)
                
            else:
                print("List is empty. Cannot remove.")
                
        elif choice == 5:
            print("Current List:")
            LL.display()
            
        elif choice == 6:
            print("Exiting...")
            
        else:
            print("Invalid choice. Please try again.")