import sys
from allocate import Allocate
from node import IR_Node
from rename import Rename 

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


# Function to print an intermediate representation
def ir_representation(labels, data): 
    maxiumum = [max(len(str(a)), len(str(b))) for a, b in zip(labels, data)]
    print(" ".join(f"{item:<{width}}" for item, width in zip(labels, maxiumum)))
    print(" ".join(f"{item:<{width}}" for item, width in zip(data, maxiumum)))


#main routine
def main():
    global FILENAME, BUFFER, HEAD_NODE  # Reference global variables to keep track of and modify
    
    #Parse command line flags
    inputted_flags = sys.argv[1:]
    
    # Check for multiple flags or incorrect flags
    number_of_flags = 0
    for flag in inputted_flags: 
        if flag.startswith("-"):
            if flag in ["-h", "-x"]:
                number_of_flags +=1
            elif flag.isnumeric():
                number_of_flags +=1
            else:
                print("ERROR: Be sure to use only a supported flag.", file=sys.stderr)
                sys.exit() 
        
    if number_of_flags > 1:
        print("ERROR: Be sure to use only one flag. The highest priority inputted_flags will be implemented.", file=sys.stderr)
    
    # Handle the "-h" flag
    if "-h" in inputted_flags:
        print("""-h. When the -h inputted_flags is detected, 412fe will produce a list of valid command-line arguments that includes a 
              description of all command-line arguments required for Lab 1 as well as any additional command-line arguments 
              supported by your 412fe implementation.""")
        print("""-x <name>. Scans and parses the input block, then renames the code from the input block and prints the result. 
              <name> is a Linux pathname""")
        print("""k <name>. k is the number of registers available to the allocator where 3 <= k <= 64. <name> is a Linux pathname.
              Scans, parses, and allocates the input block so that it only uses registers r0 to rk-1. Prints the resulting code. ”""")
        sys.exit()
    
    # Handle the "-x" flag
    elif "-x" in inputted_flags:
        try:
            # Open the specified file
            FILENAME = open(inputted_flags[-1])
            BUFFER = FILENAME.readline()
            
            errors_total, num_ops , max_sr = parsing_iloc() # Parse the file and check for errors
            if errors_total == 0: # If no errors, print the intermediate representation
                rename = Rename(num_ops, max_sr, TAIL_NODE) # Intialize process for renaming
                rename.renaming_iloc() # Rename the SR's to VR's 
                curr_node = HEAD_NODE  # Start from the head of the instruction list

                while curr_node != None:
                    lexeme = REVERSE_LEXEMES[curr_node.information[1]] # Get the lexeme (operation)
                    # Print instruction based on its type (load, store, add, sub, etc.)
                    if lexeme == "load" or lexeme == "store":
                        print(f"{lexeme} r{curr_node.information[3]} => r{curr_node.information[11]}")
                    elif lexeme in ["add","sub","mult","lshift","rshift"]:
                        print(f"{lexeme} r{curr_node.information[3]}, r{curr_node.information[7]} => r{curr_node.information[11]}")
                    elif lexeme == "output":
                        print(f"{lexeme} {curr_node.information[2]}")
                    elif lexeme == "nop":
                        print(f"{lexeme}")
                    elif lexeme == "loadI":
                        print(f"loadI {curr_node.information[2]} => r{curr_node.information[11]}")
                        
                    curr_node = curr_node.next # Move to the next instruction node
                    
            else:
                # Display an error if there were issues parsing the ILOC
                print("ERROR: Cannot display internal representation because there exists an error withiin the ILOC", file=sys.stderr)
            
            FILENAME.close() # Close the opened file after processing
        except:
            # Handle errors that occur when trying to open the file
            print(f"ERROR: Could not open the given file path", file=sys.stderr)
            sys.exit()       

    
    elif inputted_flags[0].isdigit():     # Check if the first inputted flag is a digit (indicating a register count)
        try:
            # Open the specified file
            FILENAME = open(inputted_flags[-1])
            k = int(inputted_flags[0]) # Convert the first input flag to an integer (register count)
            
            if not (3 <= k <= 64):
                print("ERROR: Invalid number of registers supported.", file=sys.stderr)
                sys.exit() # Exit the program if an invalid number of registers is provided
            
            BUFFER = FILENAME.readline()
            
            errors_total, num_ops , max_sr = parsing_iloc() # Parse the file and check for errors
            
            if errors_total == 0: # If no errors, print the intermediate representation
                rename = Rename(num_ops, max_sr, TAIL_NODE) # Intialize process for renaming
                vrname, maxlive = rename.renaming_iloc() # Rename the SR's to VR's 

                allocate = Allocate(k, vrname, HEAD_NODE, maxlive) # Intialize process for allocation
                allocate.allocating_iloc() # Rename the VR's to PR's

                curr_node = HEAD_NODE # Start from the head of the instruction list

                while curr_node != None:
                    lexeme = REVERSE_LEXEMES[curr_node.information[1]] # Get the lexeme (operation)
                    # Print instruction based on its type (load, store, add, sub, etc.)
                    if lexeme == "load" or lexeme == "store":
                        print(f"{lexeme} r{curr_node.information[4]} => r{curr_node.information[12]}")
                    elif lexeme in ["add","sub","mult","lshift","rshift"]:
                        print(f"{lexeme} r{curr_node.information[4]}, r{curr_node.information[8]} => r{curr_node.information[12]}")
                    elif lexeme == "output":
                        print(f"{lexeme} {curr_node.information[2]}")
                    elif lexeme == "nop":
                        print(f"{lexeme}")
                    elif lexeme == "loadI" and curr_node.ignore is False:
                        print(f"loadI {curr_node.information[2]} => r{curr_node.information[12]}")
                        
                    curr_node = curr_node.next # Move to the next instruction node
                    
            else:
                print("ERROR: Cannot display internal representation because there exists an error withiin the ILOC", file=sys.stderr) 
                # Display an error if there were issues parsing the ILOC
            FILENAME.close()
        
        except:
            print(f"ERROR: Could not open the given file path", file=sys.stderr) # Handle errors that occur when trying to open the file
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


#Used to be able to run the file from command line
if __name__ == '__main__':
    main()