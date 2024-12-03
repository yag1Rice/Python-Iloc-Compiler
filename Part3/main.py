import sys
from node import IR_Node
from rename import Rename
from graph import Graph_Node
import heapq


BUFFER = "" # Initialize an empty buffer to store input data

INDEX_BUFFER= 0 # Index pointer to keep track of the current position in the buffer

LINE_NUMBER = 1 # Line number counter for input tracking

FILENAME = "" # Filename of the input source

# Define categories for different types of tokens
CATEGS = {
    "MEMOP":11,
    "LOADI":10,
    "ARITHOP":9,
    "OUTPUT":8,
    "NOP":7,
    "CONSTANT":6,
    "REGISTER":5,
    "COMMA":4,
    "INTO":3,
    "EOL":2,
    "ERROR":1,
    "EOF":0
}

# Define lexeme values
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

# Create a reverse mapping from category values back to their names
REVERSE_CATEGS = {v:k for k,v in CATEGS.items()}

# Create a reverse mapping from lexeme values back to their names
REVERSE_LEXEMES = {v:k for k,v in LEXEMES.items()}

# List of whitespace characters for token separation
WHITESPACE_CHECK = [' ', '\t']

HEAD_NODE = IR_Node() # Initialize the head 

TAIL_NODE = None # Pointer to the current node,

WEIGHTS = {14: 6, 13: 6, 9:3}

#main routine
def main():
    global FILENAME, BUFFER, HEAD_NODE  # Reference global variables to keep track of and modify
    
    #Parse command line flags
    inputted_flags = sys.argv[1:]
    
    # Handle the "-h" flag
    if "-h" in inputted_flags:
        print("""schedule -h.
            When a -h flag is detected, schedule must produce a list of valid
            command-line arguments that includes a description of all
            command-line arguments required for Lab 3 as well as any
            additional command-line arguments supported by your schedule
            implementation. schedule is not required to process command-line arguments that
            appear after the -h flag.""")
        print("""schedule <name>
            This command will be used to invoke schedule on the input block
            contained in <name>. <name> specifies the name of the input file. <name> is a valid
            Linux pathname relative to the current working directory.
            schedule will produce, as output, an ILOC program that is
            equivalent to the input program, albeit reordered to improve
            (shorten) its execution time on the Lab 3 ILOC Simulator. The
            output code must use the square bracket notation [ op1 ; op2 ] to
            designate operations that should issue in the same cycle.
            schedule is not required to process command-line arguments that
            appear after <file name>.""")
        sys.exit()
    
    # Only filename is inputted with no flags
    else:
        try:
            # Open the specified file
            FILENAME = open(inputted_flags[-1])
            BUFFER = FILENAME.readline()
            errors_total, num_ops , max_sr = parsing_iloc() # Parse the file and check for errors
            if errors_total == 0: # If no errors, print the intermediate representation
                rename = Rename(num_ops, max_sr, TAIL_NODE) # Intialize process for renaming
                rename.renaming_iloc() # Rename the SR's to VR's 
                leaf_nodes = graphing_iloc() # Build the graph representation and add weights for scheduling
                scheduled_nodes = scheduling_iloc(leaf_nodes) # Schedule the nodes and return a list of tuples to print
                printing_schedule(scheduled_nodes) # Print the nodes and format accordingly  
            else:
                # Display an error if there were issues parsing the ILOC
                print("ERROR: Cannot display internal representation because there exists an error withiin the ILOC", file=sys.stderr)
            
            FILENAME.close() # Close the opened file after processing
        except:
            # Handle errors that occur when trying to open the file
            print(f"ERROR: Could not open the given file path", file=sys.stderr)
            sys.exit()       

    return

#scanning function  
def scanning_iloc():
    global BUFFER, INDEX_BUFFER, FILENAME

    while BUFFER[INDEX_BUFFER:INDEX_BUFFER+1] in WHITESPACE_CHECK: # Skip any whitespace characters
        INDEX_BUFFER += 1

    character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1] # Get the current character
    
    if character == "l": # Check if the character sequence is loadi or load or lshift
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == "o":
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "a":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character == "d":
                    INDEX_BUFFER += 1
                    character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                    if character == "I": # Check if the character sequence is loadi
                        INDEX_BUFFER += 1
                        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                        if character in WHITESPACE_CHECK:
                            return (CATEGS["LOADI"], LEXEMES["loadI"])
                    elif character in WHITESPACE_CHECK:
                        return (CATEGS["MEMOP"], LEXEMES["load"])
        
        elif character == "s": # Check if the character sequence is lshift
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "h":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character == "i":
                    INDEX_BUFFER += 1
                    character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                    if character == "f":
                        INDEX_BUFFER += 1
                        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                        if character == "t":
                            INDEX_BUFFER += 1
                            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                            if character in WHITESPACE_CHECK:
                                return (CATEGS["ARITHOP"], LEXEMES["lshift"])

    elif character == "n": # Check if the character sequence is nop
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == "o":
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "p":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character in WHITESPACE_CHECK or character in ["\n", "\r", ""] or (character == '/' and BUFFER[INDEX_BUFFER+1:INDEX_BUFFER+2] == '/'):
                    return (CATEGS["NOP"], LEXEMES["nop"])

    elif character == "a": # Check if the character sequence is add
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == "d":
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "d":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character in WHITESPACE_CHECK:
                    return (CATEGS["ARITHOP"], LEXEMES["add"])
    
    
    elif character == "s": # Check if the character sequence is store or sub
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character=="t":
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "o":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character == "r":
                    INDEX_BUFFER += 1
                    character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                    if character == "e":
                        INDEX_BUFFER += 1
                        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                        if character in WHITESPACE_CHECK:
                            return (CATEGS["MEMOP"], LEXEMES["store"])
        
        elif character == "u": # Check if the character sequence is sub
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "b":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character in WHITESPACE_CHECK:
                    return (CATEGS["ARITHOP"], LEXEMES["sub"])   
                
    elif character == "r": # Check if the character sequence is register or rshift
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == "s":
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "h":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character == "i":
                    INDEX_BUFFER += 1
                    character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                    if character == "f":
                        INDEX_BUFFER += 1
                        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                        if character == "t":
                            INDEX_BUFFER += 1
                            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                            if character in WHITESPACE_CHECK:
                                return (CATEGS["ARITHOP"], LEXEMES["rshift"])
        
        elif character.isdigit():     # Check for register number
            number_string = ""
            while character.isdigit():
                number_string += character
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            # If the register is valid and is followed by an appropriate terminator
            if (character in ["\n", "\r", "", "=",","] or character in WHITESPACE_CHECK or (character == '/' and BUFFER[INDEX_BUFFER+1:INDEX_BUFFER+2] == '/')) and int(number_string) >= 0:
                return (CATEGS["REGISTER"], int(number_string))
    
    elif character == "m": # Check if the character sequence is mult
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == "u":
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "l":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character == "t":
                    INDEX_BUFFER += 1
                    character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                    if character in WHITESPACE_CHECK:
                        return (CATEGS["ARITHOP"], LEXEMES["mult"])
                

    elif character.isdigit(): # Check for a constant number
        number_string = ""
        while character.isdigit():
            number_string += character
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        # If the constant is valid and is followed by an appropriate terminator
        if  (character in WHITESPACE_CHECK or character in ["\n", "\r", "", "="] or (character == '/' and BUFFER[INDEX_BUFFER+1:INDEX_BUFFER+2] == '/')) and (0 <= int(number_string) <= (2**31)-1):
            return (CATEGS["CONSTANT"], int(number_string))

    elif character == "o": # Check if the character sequence is output
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == "u":
            INDEX_BUFFER += 1
            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
            if character == "t":
                INDEX_BUFFER += 1
                character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                if character == "p":
                    INDEX_BUFFER += 1
                    character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                    if character == "u":
                        INDEX_BUFFER += 1
                        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                        if character == "t":
                            INDEX_BUFFER += 1
                            character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
                            if character in WHITESPACE_CHECK:
                                return (CATEGS["OUTPUT"], LEXEMES["output"])   
        
    elif character == ",": # Check if the character is a comma
        INDEX_BUFFER += 1
        return (CATEGS["COMMA"], LEXEMES["comma"])
        
    elif character == "/": # Check if the character is a comment 
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == "/":
            BUFFER = FILENAME.readline()  # Read the next line for further processing
            INDEX_BUFFER = 0
            return (CATEGS["EOL"], LEXEMES["eol"])
    
    elif character == "=": # Check if the character is into 
        INDEX_BUFFER += 1
        character = BUFFER[INDEX_BUFFER:INDEX_BUFFER+1]
        if character == ">":
            INDEX_BUFFER += 1
            return (CATEGS["INTO"], LEXEMES["into"])
    
    elif character == "\n" or character == "\r": # Check if the character represents the end of a line
       BUFFER = FILENAME.readline() # Read the next line for further processing
       INDEX_BUFFER = 0
       return (CATEGS["EOL"], LEXEMES["eol"])     
    
    elif character == "": # Check if the character represents the end of the file
        return (CATEGS["EOF"], LEXEMES["eof"])
    
    
    INDEX_BUFFER = len(BUFFER)-1 # If no valid token is recognized, move to the end of the line and return an error
    
    return (CATEGS["ERROR"], LEXEMES["error"])

#parsing function
def parsing_iloc():
    global LINE_NUMBER, TAIL_NODE, HEAD_NODE  # Reference global variables to keep track of and modify


    final_token = [CATEGS["EOL"], CATEGS["EOF"]] # Define final tokens representing end of line (EOL) or end of file (EOF)
    error_word = None    # Variable to store the category of the word that caused an error
    errors_total = 0     # Counter for the total number of errors encountered
    parsing_error = False # Flag to indicate if a parsing error has occurred
    operations_total = 0 # Counter for the total number of operations parsed successfully
    max_sr = 0

    #Scanning to get the first category and lexeme
    first_categ, first_lexeme = scanning_iloc()

    # Continue parsing until end of file
    while first_categ != CATEGS["EOF"]:
        if first_categ == CATEGS["MEMOP"]: # Handle memory operations
            next_category, lexeme1 = scanning_iloc()
            if next_category != CATEGS["REGISTER"]:             # Expect a REGISTER category after MEMOP
                print(f"ERROR {LINE_NUMBER}: Expected REGISTER but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)
                error_word = next_category
                parsing_error = True 
            else: 
                next_category, _ = scanning_iloc()
                if next_category != CATEGS["INTO"]:                 # Expect an INTO category after REGISTER
                    error_word = next_category
                    parsing_error = True
                    print(f"ERROR {LINE_NUMBER}: Expected INTO but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)
                else: 
                    next_category, lexeme2 = scanning_iloc()
                    if next_category != CATEGS["REGISTER"]:                     # Expect another REGISTER category
                        error_word = next_category
                        parsing_error = True
                        print(f"ERROR {LINE_NUMBER}: Expected REGISTER but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)
                    else: 
                        next_category, _ = scanning_iloc()
                        if next_category in final_token:                             # Create the node for the intermediate representation
                            if TAIL_NODE is None:
                                max_sr = max(max_sr, lexeme1, lexeme2)
                                HEAD_NODE.information[0] = LINE_NUMBER
                                HEAD_NODE.information[1] = first_lexeme
                                HEAD_NODE.information[2] = lexeme1
                                HEAD_NODE.information[10] = lexeme2
                                TAIL_NODE = HEAD_NODE
                            else:
                                new = IR_Node()
                                max_sr = max(max_sr, lexeme1, lexeme2)
                                new.information[0] = LINE_NUMBER
                                new.information[1] = first_lexeme
                                new.information[2] = lexeme1
                                new.information[10] = lexeme2
                                new.prev = TAIL_NODE
                                TAIL_NODE.next = new
                                TAIL_NODE = new
                            parsing_error = False 
                        else: 
                            error_word = next_category
                            parsing_error = True
                            print(f"ERROR {LINE_NUMBER}: Expected EOL or EOF but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)
                
        elif first_categ == CATEGS["ARITHOP"]:         # Handle arithmetic operations
            next_category, lexeme1 = scanning_iloc()
            if next_category != CATEGS["REGISTER"]:             # Expect a REGISTER category after ARITHOP
                error_word = next_category
                parsing_error = True
                print(f"ERROR {LINE_NUMBER}: Expected REGISTER but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)               
            else:
                next_category, _ = scanning_iloc()
                if next_category != CATEGS["COMMA"]:                 # Expect a COMMA after REGISTER
                    error_word = next_category
                    parsing_error = True
                    print(f"ERROR {LINE_NUMBER}: Expected COMMA but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)

                else:
                    next_category, lexeme2 = scanning_iloc()
                    if next_category != CATEGS["REGISTER"]:                     # Expect another REGISTER after COMMA

                        error_word = next_category
                        parsing_error = True
                        print(f"ERROR {LINE_NUMBER}: Expected REGISTER but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)

                    else:
                        next_category, _ = scanning_iloc()
                        if next_category != CATEGS["INTO"]:                         # Expect INTO after REGISTER

                            error_word = next_category
                            parsing_error = True
                            print(f"ERROR {LINE_NUMBER}: Expected INTO but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)

                        else:
                            next_category, lexeme3 = scanning_iloc()
                            if next_category != CATEGS["REGISTER"]:                             # Expect a REGISTER after INTO

                                error_word = next_category
                                parsing_error = True
                                print(f"ERROR {LINE_NUMBER}: Expected REGISTER but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)

                            else:
                                next_category, _ = scanning_iloc()
                                if next_category in final_token: # Create the node for the intermediate representation
                                    parsing_error = False 
                                    if TAIL_NODE is None:
                                        max_sr = max(max_sr, lexeme1, lexeme2)
                                        HEAD_NODE.information[0] = LINE_NUMBER
                                        HEAD_NODE.information[1] = first_lexeme
                                        HEAD_NODE.information[2] = lexeme1
                                        HEAD_NODE.information[6] = lexeme2
                                        HEAD_NODE.information[10] = lexeme3
                                        TAIL_NODE = HEAD_NODE
                                    else:
                                        new = IR_Node()
                                        max_sr = max(max_sr, lexeme1, lexeme2)
                                        new.information[0] = LINE_NUMBER
                                        new.information[1] = first_lexeme
                                        new.information[2] = lexeme1
                                        new.information[6] = lexeme2
                                        new.information[10] = lexeme3
                                        new.prev = TAIL_NODE
                                        TAIL_NODE.next = new
                                        TAIL_NODE = new
                                else:
                                    error_word = next_category
                                    parsing_error = True
                                    print(f"ERROR {LINE_NUMBER}: Expected EOL or EOF but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)


        elif first_categ == CATEGS["NOP"]:  # Handle no-operation
            next_category, _ = scanning_iloc()
            if next_category in final_token: # Create the node for the intermediate representation
                parsing_error = False 
                if TAIL_NODE is None:
                    HEAD_NODE.information[0] = LINE_NUMBER
                    HEAD_NODE.information[1] = first_lexeme
                    TAIL_NODE = HEAD_NODE
                else:
                    new = IR_Node()
                    new.information[0] = LINE_NUMBER
                    new.information[1] = first_lexeme
                    new.prev = TAIL_NODE
                    TAIL_NODE.next = new
                    TAIL_NODE = new
            else:
                error_word = next_category
                parsing_error = True
                print(f"ERROR {LINE_NUMBER}: Expected EOL or EOF but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)


        elif first_categ == CATEGS["OUTPUT"]: # Handle output instructions
            next_category, lexeme1 = scanning_iloc()
            if next_category != CATEGS["CONSTANT"]: # Expect a CONSTANT category after OUTPUT
                error_word = next_category
                parsing_error = True
                print(f"ERROR {LINE_NUMBER}: Expected CONSTANT but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)

            else: 
                next_category, _ = scanning_iloc()
                if next_category in final_token: # Create the node for the intermediate representation
                    parsing_error = False 
                    if TAIL_NODE is None:
                        HEAD_NODE.information[0] = LINE_NUMBER
                        HEAD_NODE.information[1] = first_lexeme
                        HEAD_NODE.information[2] = lexeme1
                        TAIL_NODE = HEAD_NODE
                    else:
                        new = IR_Node()
                        new.information[0] = LINE_NUMBER
                        new.information[1] = first_lexeme
                        new.information[2] = lexeme1
                        new.prev = TAIL_NODE
                        TAIL_NODE.next = new
                        TAIL_NODE = new
                else:
                    error_word = next_category
                    parsing_error = True
                    print(f"ERROR {LINE_NUMBER}: Expected EOL or EOF but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)


        elif first_categ == CATEGS["LOADI"]: # Handle immediate load instructions
            next_category, lexeme1 = scanning_iloc()
            if next_category != CATEGS["CONSTANT"]: # Expect a CONSTANT after LOADI
                error_word = next_category
                parsing_error = True
                print(f"ERROR {LINE_NUMBER}: Expected CONSTANT but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)
                
            else:
                next_category, _ = scanning_iloc()
                if next_category != CATEGS["INTO"]:                 # Expect INTO after CONSTANT
                    error_word = next_category
                    parsing_error = True
                    print(f"ERROR {LINE_NUMBER}: Expected INTO but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)
                    
                else:
                    next_category, lexeme2 = scanning_iloc()
                    if next_category != CATEGS["REGISTER"]:                     # Expect a REGISTER after INTO
                        error_word = next_category
                        parsing_error = True
                        print(f"ERROR {LINE_NUMBER}: Expected REGISTER but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)
                        
                    else:
                        next_category, _ = scanning_iloc()
                        if next_category in final_token:
                            # Create the node for the internal representation 
                            parsing_error = False 
                            if TAIL_NODE is None:
                                max_sr = max(max_sr, lexeme1, lexeme2)
                                HEAD_NODE.information[0] = LINE_NUMBER
                                HEAD_NODE.information[1] = first_lexeme
                                HEAD_NODE.information[2] = lexeme1
                                HEAD_NODE.information[10] = lexeme2
                                TAIL_NODE = HEAD_NODE
                            else:
                                new = IR_Node()
                                max_sr = max(max_sr, lexeme1, lexeme2)
                                new.information[0] = LINE_NUMBER
                                new.information[1] = first_lexeme
                                new.information[2] = lexeme1
                                new.information[10] = lexeme2
                                new.prev = TAIL_NODE
                                TAIL_NODE.next = new
                                TAIL_NODE = new
                        else:
                            error_word = next_category
                            parsing_error = True
                            print(f"ERROR {LINE_NUMBER}: Expected EOF or EOL but encountered " + str(REVERSE_CATEGS[next_category]) , file=sys.stderr)

        elif first_categ == CATEGS["EOL"]: # Handle end of line
            parsing_error = False 
        else: 
            parsing_error = True
            error_word = first_categ
            print(f"ERROR {LINE_NUMBER}: Expected valid OPCODE but encountered " + str(REVERSE_CATEGS[first_categ]), file=sys.stderr)

        # If there is no parsing error and the current token is not EOL, it's a valid operation
        if not parsing_error and first_categ != CATEGS["EOL"]:
            operations_total += 1
            
        elif parsing_error:
            errors_total += 1

        # If an error occurred that isn't at EOL, skip to the next EOL or EOF
        if parsing_error and error_word != CATEGS["EOL"]:
            while first_categ not in final_token:
                first_categ, first_lexeme = scanning_iloc()
                error_word = None
                parsing_error = False

        if first_categ == CATEGS["EOF"]:
            break 

        LINE_NUMBER += 1          # Increment line number for the next operation

        first_categ, first_lexeme = scanning_iloc()         # Continue scanning for the next category and lexeme

    return errors_total, operations_total, max_sr

#graphing function
def graphing_iloc():
    """
    Constructs a dependency graph for ILOC instructions, representing relationships between nodes
    (operations) such as control dependencies, serial dependencies, and normal dependencies.
    Computes weights for scheduling and identifies root and leaf nodes in the graph.

    Returns:
    --------
    leaf_nodes : list
        A list of leaf nodes in the graph, representing the end of all dependencies.
    """

    # Global head node to start the graph traversal
    global HEAD_NODE
    curr_node = HEAD_NODE

    # Initialize graph structures
    graph_mapping = {}  # Maps register identifiers to graph nodes for dependency linking
    graph = []          # List of all graph nodes
    output_nodes = []   # Track output operation nodes
    store_nodes = []    # Track store operation nodes
    load_nodes = []     # Track load operation nodes

    # Traverse through the list of instructions
    while curr_node is not None:
        if curr_node.information[1] != LEXEMES["nop"]:  # Skip 'nop' instructions

            if curr_node.information[1] == LEXEMES["load"]:
                # Handle 'load' operation
                node = Graph_Node(graph_info=curr_node.information)
                graph_mapping[curr_node.information[11]] = node
                graph.append(node)

                # Establish normal dependencies
                for use in [3]:
                    child = graph_mapping[curr_node.information[use]]
                    node.normal_chils.append(child)
                    child.normal_pars.append(node)

                # Establish control dependencies with previous store nodes
                for i in range(len(store_nodes) - 1, -1, -1):
                    if store_nodes[i] not in node.normal_chils:
                        node.con_chils.append(store_nodes[i])
                        store_nodes[i].con_pars.append(node)
                        break

                load_nodes.append(node)

            elif curr_node.information[1] == LEXEMES["store"]:
                # Handle 'store' operation
                node = Graph_Node(graph_info=curr_node.information)
                graph.append(node)

                # Establish normal dependencies
                for use in [3, 11]:
                    child = graph_mapping[curr_node.information[use]]
                    node.normal_chils.append(child)
                    child.normal_pars.append(node)

                # Establish serial and control dependencies
                for node_list in [output_nodes, load_nodes, store_nodes]:
                    for i in range(len(node_list) - 1, -1, -1):
                        if node_list[i] not in node.normal_chils:
                            node.ser_chils.append(node_list[i])
                            node_list[i].ser_pars.append(node)
                            if node_list is store_nodes:  # Control dependencies only for store nodes
                                break

                store_nodes.append(node)

            elif curr_node.information[1] == LEXEMES["output"]:
                # Handle 'output' operation
                node = Graph_Node(graph_info=curr_node.information)
                graph.append(node)

                # Establish serial and control dependencies with previous output or store nodes
                if output_nodes:
                    node.ser_chils.append(output_nodes[-1])
                    output_nodes[-1].ser_pars.append(node)
                if store_nodes:
                    node.con_chils.append(store_nodes[-1])
                    store_nodes[-1].con_pars.append(node)

                output_nodes.append(node)

            elif curr_node.information[1] == LEXEMES["loadI"]:
                # Handle 'loadI' (load immediate) operation
                node = Graph_Node(graph_info=curr_node.information)
                graph_mapping[curr_node.information[11]] = node
                graph.append(node)

            else:
                # Handle arithmetic or other operations
                node = Graph_Node(graph_info=curr_node.information)
                graph_mapping[curr_node.information[11]] = node
                graph.append(node)

                # Establish normal dependencies
                for use in [3, 7]:
                    child = graph_mapping[curr_node.information[use]]
                    node.normal_chils.append(child)
                    child.normal_pars.append(node)

        # Move to the next instruction
        curr_node = curr_node.next

    # Identify root nodes (nodes with no parents)
    root_nodes = []
    for node in graph:
        if not (node.con_pars or node.ser_pars or node.normal_pars):
            root_nodes.append(node)

    # Propagate weights through the graph for scheduling
    while root_nodes:
        cur = root_nodes.pop()
        cur_weight = cur.weight

        for child in cur.normal_chils + cur.ser_chils + cur.con_chils:
            # Update child weight based on parent's weight and operation cost
            child.weight = max(child.weight, cur_weight + 10 * WEIGHTS.get(child.graph_info[1], 1) + 1)
            if child in cur.ser_chils:  # Serial dependencies reduce weight penalty
                child.weight -= 48
            root_nodes.append(child)

    # Identify leaf nodes (nodes with no children)
    leaf_nodes = []
    for node in graph:
        if not (node.con_chils or node.ser_chils or node.normal_chils):
            leaf_nodes.append(node)

    return leaf_nodes

#scheduling function
def scheduling_iloc(leaf_nodes):
    # Initialize lists for active nodes, ready nodes, and scheduled nodes
    active_nodes, ready_nodes = [], []
    scheduled_nodes = []
    
    # Create a "no operation" (nop) node to fill scheduling gaps
    nop_node = Graph_Node(graph_info=["-" for i in range(15)])
    nop_node.graph_info[1] = LEXEMES["nop"]
    
    cycle = 1  # Initialize the scheduling cycle counter
    
    # Add leaf nodes to the ready queue with negative weights for prioritization
    for i, node in enumerate(leaf_nodes):
        ready_nodes.append((-node.weight, i, node))       
    heapq.heapify(ready_nodes)

    size = len(leaf_nodes)  # Track the number of nodes processed
    while ready_nodes or active_nodes:
        op1, op2 = None, None  # Initialize scheduled operations for this cycle

        if not ready_nodes:
            # If no nodes are ready, schedule two nop nodes
            scheduled_nodes.append((nop_node, nop_node))
        else:
            # Schedule the first operation (op1) from the ready queue
            op1 = heapq.heappop(ready_nodes)[-1]
            incompatible_nodes = []  # Track nodes incompatible with op1
            
            if op1.graph_info[1] != LEXEMES["output"]:
                # Find a compatible second operation (op2) for the cycle
                while len(ready_nodes) > 0:
                    invalid = {
                        LEXEMES["load"]: [LEXEMES["load"], LEXEMES["store"]],
                        LEXEMES["store"]: [LEXEMES["load"], LEXEMES["store"]],
                        LEXEMES["mult"]: [LEXEMES["mult"]]
                    }
                    latency, index, node = heapq.heappop(ready_nodes)
                    
                    if node.graph_info[1] != LEXEMES["output"] and (node.graph_info[1] not in invalid.get(op1.graph_info[1], [])):
                        op2 = node
                        break 
                    else:
                        incompatible_nodes.append((latency, index, node))
                
                # Re-add incompatible nodes back to the ready queue
                for pair in incompatible_nodes:
                    heapq.heappush(ready_nodes, pair)

            # Determine scheduling format for one or two operations
            if not op2:
                if op1.graph_info[1] in [LEXEMES["load"], LEXEMES["store"]]:
                    single = (op1, nop_node)
                    scheduled_nodes.append(single)
                else:
                    single = (nop_node, op1)
                    scheduled_nodes.append(single)
            else:
                if op1.graph_info[1] in [LEXEMES["load"], LEXEMES["store"]]:
                    double = (op1, op2)
                    scheduled_nodes.append(double)
                elif op2.graph_info[1] in [LEXEMES["load"], LEXEMES["store"]]:
                    double = (op2, op1)
                    scheduled_nodes.append(double)
                elif op1.graph_info[1] in [LEXEMES["mult"]]:
                    double = (op2, op1)
                    scheduled_nodes.append(double)
                elif op2.graph_info[1] in [LEXEMES["mult"]]:
                    double = (op1, op2)
                    scheduled_nodes.append(double)
                else:
                    double = (op1, op2)
                    scheduled_nodes.append(double)

        # Mark scheduled operations and process their children
        for op in [op1, op2]:
            if op:
                op.check_scheduled = True
                active_nodes.append((WEIGHTS.get(op.graph_info[1], 1) + cycle, op))
                if op.graph_info[1] in [LEXEMES["store"], LEXEMES["load"], LEXEMES["output"]]:
                    for child in op.ser_chils + op.con_chils:
                        if child.ready_check() and not child.check_visited:
                            heapq.heappush(ready_nodes, (-child.weight, size, child))
                            size += 1
                            child.check_visited = True  

        # Increment the cycle counter and process active nodes
        cycle += 1
        idx = 0
        while idx < len(active_nodes):
            if cycle < active_nodes[idx][0]:
                idx += 1
            else:
                # If an active node's execution is complete, mark it as executed
                node = active_nodes.pop(idx)[-1]
                node.check_executed_self = True
                node_parents = node.normal_pars + node.ser_pars + node.con_pars
                for par in node_parents:
                    if not par.check_visited and par.ready_check():
                        heapq.heappush(ready_nodes, (-par.weight, size, par))
                        size += 1
                        par.check_visited = True
                
    return scheduled_nodes  # Return the scheduled nodes for the program

#printing schedule function
def printing_schedule(scheduled_nodes):
    for index in range(len(scheduled_nodes)):  # iterate through the list of node pairs
        f0_node = scheduled_nodes[index][0]  # extract the first node in the pair
        f0_lexeme = REVERSE_LEXEMES[f0_node.graph_info[1]]  # map node's operation type
        if f0_lexeme == "load" or f0_lexeme == "store":  # handle load/store operations
            f0_print = f"{f0_lexeme} r{f0_node.graph_info[3]} => r{f0_node.graph_info[11]}"
        elif f0_lexeme in ["add", "sub", "mult", "lshift", "rshift"]:  # handle arithmetic operations
            f0_print = f"{f0_lexeme} r{f0_node.graph_info[3]}, r{f0_node.graph_info[7]} => r{f0_node.graph_info[11]}"
        elif f0_lexeme == "output":  # handle output operation
            f0_print = f"{f0_lexeme} {f0_node.graph_info[2]}"
        elif f0_lexeme == "nop":  # handle no-operation
            f0_print = "nop"
        elif f0_lexeme == "loadI":  # handle load immediate
            f0_print = f"loadI {f0_node.graph_info[2]} => r{f0_node.graph_info[11]}"

        f1_node = scheduled_nodes[index][1]  # extract the second node in the pair
        f1_lexeme = REVERSE_LEXEMES[f1_node.graph_info[1]]  # map node's operation type
        
        if f1_lexeme == "load" or f1_lexeme == "store":  # handle load/store operations
            f1_print = f"{f1_lexeme} r{f1_node.graph_info[3]} => r{f1_node.graph_info[11]}"
        elif f1_lexeme in ["add", "sub", "mult", "lshift", "rshift"]:  # handle arithmetic operations
            f1_print = f"{f1_lexeme} r{f1_node.graph_info[3]}, r{f1_node.graph_info[7]} => r{f1_node.graph_info[11]}"
        elif f1_lexeme == "output":  # handle output operation
            f1_print = f"{f1_lexeme} {f1_node.graph_info[2]}"
        elif f1_lexeme == "nop":  # handle no-operation
            f1_print = "nop"
        elif f1_lexeme == "loadI":  # handle load immediate
            f1_print = f"loadI {f1_node.graph_info[2]} => r{f1_node.graph_info[11]}"

        # Print the formatted instruction pair
        print(f"[ {f0_print} ; {f1_print} ]")

#Used to be able to run the file from command line
if __name__ == '__main__':
    main()