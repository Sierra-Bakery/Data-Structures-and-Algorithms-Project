class DSAListNode: #node class, acts as an object used by linked list class, contains value and pointer attributes
    def __init__(self, value):
        self.value = value
        self.next = None #pointer attribute, points to none as the data structure points to null
        self.prev = None #points to the previous node as it is a doubly linked list

class DSALinkedList:
    def __init__(self):
        #specifies the first and last node
        self.head = None 
        self.tail = None
    def isempty(self):
        return self.head is None
        #returns if the list is empty
    def insert_first(self, value):
        new_node = DSAListNode(value)
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
        new_node = DSAListNode(value)
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

