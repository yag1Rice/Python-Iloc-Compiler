class IR_Node:
    def __init__(self):
        # Pointer to the previous node
        self.prev = None
        # Pointer to the next node
        self.next = None
        # List to store information related to the node
        self.information = ["-" for i in range(14)]

