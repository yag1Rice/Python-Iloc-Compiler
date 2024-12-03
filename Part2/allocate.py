from node import IR_Node

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

class Allocate: 
    def __init__(self, max_pr, vrname, head_node, max_live):
        self.max_vr = vrname - 1 # Set the maximum range of VRs
        self.max_pr = max_pr - 1 # Set the maximum range of PRs
        self.max_live = max_live # Set the maximum live at any given point to figure out if a spill will occur

        self.curr_node = head_node
        self.spill_register = max_pr - 1 # Register that could be designated for spills
        self.PRStack = [pr for pr in range(self.max_pr)] # Stack to keep track of PRs

        self.VRToPR = ["-"] * (self.max_vr + 1)
        self.PRToVR = ["-"] * (self.max_pr + 1)
        self.VrToSpill = ["-"] * (self.max_vr + 1)
        self.PRToNU = [float("inf")] * (self.max_pr + 1)

        self.spill_location = 32768 # Intial possible memory spill location
        self.prev_used = set() # Keep track of the previously used pr in an iloc block
        self.can_remater = ["-"] * (self.max_vr + 1)

        if self.max_live > max_pr: 
            self.PRToNU[-1] = float("-inf") # If maxlive is greater than k then designate the last register to have its next use be super close
        else: 
            self.PRStack.append(self.spill_register) # If maxlive is less than or equal to k then no longer need to reserve register


    def allocating_iloc(self):

        while self.curr_node != None:   # Iterate through internal representation from top to bottom
            
            if self.curr_node.information[1] in [LEXEMES["nop"], LEXEMES["output"]]:  # Ignore nops and outputs block 
                self.curr_node = self.curr_node.next 
                continue 

            # Get the defines and uses.
            defines = [11]
            uses = [3, 7]

            # Change the defines and uses with the store lexeme.
            if self.curr_node.information[1] == LEXEMES["store"]:
                defines = []
                uses = [3, 11]

            # Change the defines and uses with loadI lexeme.
            elif self.curr_node.information[1] == LEXEMES["loadI"]:
                uses = []

            # Change the defines and uses with load lexeme.
            elif self.curr_node.information[1] == LEXEMES["load"]:
                uses = [3]

            # Designate the loadI to be ignored and be rematerialized later on 
            loadI_ignored = False 
            for pos in defines: 
                if self.curr_node.information[pos] != "-" and self.curr_node.information[1] == LEXEMES["loadI"]:
                    loadI_ignored = True
                    self.can_remater[self.curr_node.information[pos]] = self.curr_node.information[2] # Store the constant
                    self.curr_node.ignore = True
                    self.curr_node = self.curr_node.next # Move to the next node
            

            if loadI_ignored: # Move onto the next iteration if the block was a loadI 
                continue 
            

            # Iterate through each VR in the first two blocks
            for pos in uses: 

                if self.curr_node.information[pos] != "-": # Skip the VR if it missing
                    # Check if there is already a mapping between VR to PR
                    pr = self.VRToPR[self.curr_node.information[pos]]
                    if pr == "-": # If there is no corresponding PR, get a PR and see if a restore or rematerialize necessary
                        self.curr_node.information[pos+1] = self.get_set_pr(self.curr_node.information[pos], self.curr_node.information[pos+2]) # Get a PR
                        self.rematerialize_restore(self.curr_node.information[pos+1], self.curr_node.information[pos]) # Restore or rematerialize
                    else: 
                        self.curr_node.information[pos+1] = pr # Use the previously found PR to the corresponding VR
                        self.PRToNU[pr] = self.curr_node.information[pos+2] # Update the PR to NU mapping
                    
                    self.prev_used.add(self.curr_node.information[pos+1]) # Add the PR to the set 

            for pos in uses:  # Iterate through each VR in the first two blocks
                if self.curr_node.information[pos] != "-": # Skip the VR if it missing
                    # Check if this the last use for the VR
                    if self.curr_node.information[pos+2] == float("inf") and self.PRToVR[self.curr_node.information[pos+1]] != "-":
                        # If so update all the mappings, to unlink the VR to PR
                        vr = self.PRToVR[self.curr_node.information[pos+1]] 
                        self.VRToPR[vr] = "-"
                        self.PRToVR[self.curr_node.information[pos+1]] = "-"
                        self.PRToNU[self.curr_node.information[pos+1]] = float("inf")

                        self.PRStack.append(self.curr_node.information[pos+1]) # Add the PR back to the stack

            self.prev_used = set() # Reset


            for pos in defines: # Iterate through each VR in the last block
                if self.curr_node.information[pos] != "-": # If the VR isn't empty
                    # Get the corresponding PR
                    self.curr_node.information[pos+1] = self.get_set_pr(self.curr_node.information[pos], self.curr_node.information[pos+2]) 

            self.curr_node = self.curr_node.next # Move to the next node


    def get_set_pr(self, vr, nu):
        real_nu = nu # Keep of the track passed nu to update PRToNU later on
        if self.PRStack: # If there are still PRs to use, get them over spilling
            pr = self.PRStack.pop()
        else: 
            # If there are no PRs left, we need to spill
            farthest = float("-inf") 
            pr = None
            for idx, nu in enumerate(self.PRToNU): # Find the PR that corresponds to the farthest NU to mitigate spilling and that has not been already used
                if nu > farthest and idx not in self.prev_used:
                    farthest = nu
                    pr = idx
    
            spill_vr = self.PRToVR[pr] # Get corresponding VR to the PR to check if can be spilled
            self.VRToPR[spill_vr] = "-" 
            
            if self.can_remater[spill_vr] == "-" and self.VrToSpill[spill_vr] == "-": # If this vr is not designated to be rematerlized or restored, spill  
                spill = self.spill_location # Get the location in memory to spill
                self.VrToSpill[spill_vr] = spill 
                self.spill_location += 4 # Update the spill location
                self.create_loadI_node(self.spill_register, spill) # Add a loadI node 
                self.create_store_node(pr, self.spill_register) # Add store node 
        
        # Update the PRs, VRs, & NUs. 
        self.PRToVR[pr] = vr
        self.VRToPR[vr] = pr
        self.PRToNU[pr] = real_nu

        return pr 


    def create_store_node(self, pr, pr2):
        # Create a store node and set appropriate fields. 
        store_node = IR_Node()
        store_node.information[1] = LEXEMES["store"]
        store_node.information[4] = pr
        store_node.information[12] = pr2

        # Insert store node into linked list 
        old_prev = self.curr_node.prev
        self.curr_node.prev = store_node
        store_node.next = self.curr_node
        old_prev.next = store_node
        store_node.prev = old_prev


    def create_load_node(self, pr, pr2):
        # Create a load node and set appropriate fields. 
        load_node = IR_Node()
        load_node.information[1] = LEXEMES["load"]
        load_node.information[4] = pr
        load_node.information[12] = pr2

        # Insert load node into linked list 
        old_prev = self.curr_node.prev
        self.curr_node.prev = load_node
        load_node.next = self.curr_node
        old_prev.next = load_node
        load_node.prev = old_prev


    def create_loadI_node(self, pr, constant):
        # Create a loadI node and set appropriate fields. 
        loadI_node = IR_Node()
        loadI_node.information[1] = LEXEMES["loadI"]
        loadI_node.information[2] = constant
        loadI_node.information[12] = pr
        
        # Insert loadI node into linked list 
        old_prev = self.curr_node.prev
        self.curr_node.prev = loadI_node
        old_prev.next = loadI_node
        loadI_node.prev = old_prev
        loadI_node.next = self.curr_node


    def rematerialize_restore(self, pr, vr):
        if self.can_remater[vr] != "-": # If the block can be rematerialized
            constant = self.can_remater[vr]
            self.create_loadI_node(pr, constant) # Rematerialize by inserting the loadI node
        elif self.VrToSpill[vr] != "-": # If the block was spilled previously
            spill = self.VrToSpill[vr]
            self.create_loadI_node(self.spill_register, spill) # Create the loadI and load necessary to restore what was spilled
            self.create_load_node(self.spill_register, pr)





    