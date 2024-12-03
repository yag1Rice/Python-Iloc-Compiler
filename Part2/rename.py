LEXEMES = {
    "load":14,
    "store":13,
    "loadI":12,
    "add":11,
    "sub":10,
    "mult":9,
    "lshift":8,
    "rshift":7,
    "output":6,
    "nop":5,
    "comma":4,
    "into":3,
    "eol":2,
    "eof":1,
    "error":0
}


class Rename: 
    def __init__(self, num_ops, max_sr, tail_node):
        self.index = num_ops # Keep track of the index using the number of operations
        self.max_sr = max_sr # Get the largest SR from parsing
        self.tail_node = tail_node # Set the tail node as traversing bottom to top
        self.max_live = 0  # Keep track of the maximum live for allocating
        self.curr_live = 0 
        self.SRToVR = ["-"] * (self.max_sr + 1)
        self.LU = [float("inf")] * (self.max_sr + 1)

    def renaming_iloc(self):
        vrname = 0
        curr_node = self.tail_node

        # Iterate through internal representation from bottom to top.
        while curr_node != None: 

            # Ignore nops and outputs block 
            if curr_node.information[1] in [LEXEMES["nop"],LEXEMES["output"]]:
                curr_node = curr_node.prev 
                continue 

            # Get the defines and uses.
            defines = [10]
            uses = [2, 6]

            # Change the defines and uses with the store lexeme.
            if curr_node.information[1] == LEXEMES["store"]:
                defines = []
                uses = [2, 10]

            # Change the defines and uses with loadI lexeme.
            if curr_node.information[1] == LEXEMES["loadI"]:
                uses = []

            # Change the defines and uses with load lexeme.
            if curr_node.information[1] == LEXEMES["load"]:
                uses = [2]

            for pos in defines: # Iterate through the defines SR's
                sr = curr_node.information[pos]

                if self.SRToVR[sr] == "-": # If the SR does not have a mapping
                    self.SRToVR[sr] = vrname # Set the mapping
                    vrname += 1 # Increment the vrname
                    self.curr_live += 1 
                    self.max_live = max(self.max_live, self.curr_live) # Keep track of the maximum live at any given point for allocation
                curr_node.information[pos+1] = self.SRToVR[sr] # Set VR for block
                curr_node.information[pos+3] = self.LU[sr] # Set NU for block 

                self.SRToVR[sr] = "-" # Reset mapping
                self.LU[sr] = float("inf")
                self.curr_live -= 1

            for pos in uses: # Iterate through the uses SR's
                sr = curr_node.information[pos]

                if self.SRToVR[sr] == "-": # If the SR does not have a mapping
                    self.SRToVR[sr] = vrname # Set the mapping
                    vrname += 1  # Increment the vrname
                    self.curr_live += 1
                    self.max_live = max(self.max_live, self.curr_live) # Keep track of the maximum live at any given point for allocation
                curr_node.information[pos+1] = self.SRToVR[sr] # Set VR for block
                curr_node.information[pos+3] = self.LU[sr] # Set NU for block 
            
            for pos in uses: # Iterate through the uses SR's
                self.LU[curr_node.information[pos]] = self.index - 1
            
            self.index -= 1

            curr_node = curr_node.prev # Update the current node to traverse backwards

        return vrname, self.max_live 


    