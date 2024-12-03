import sys

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

# Define a class to represent a node in an intermediate representation
class IR_Node:
    def __init__(self):
        # Pointer to the previous node
        self.prev = None
        # Pointer to the next node
        self.next = None
        # List to store information related to the node
        self.information = ["-" for i in range(14)]


HEAD_NODE = IR_Node() # Initialize the head 
CURRENT_NODE = None # Pointer to the current node,

# Function to print an intermediate representation
def ir_representation(labels, data): 
    maxiumum = [max(len(str(a)), len(str(b))) for a, b in zip(labels, data)]
    print(" ".join(f"{item:<{width}}" for item, width in zip(labels, maxiumum)))
    print(" ".join(f"{item:<{width}}" for item, width in zip(data, maxiumum)))
    # print(data)

def main():
    global FILENAME, BUFFER, CURRENT_NODE, HEAD_NODE  # Reference global variables to keep track of and modify
    
    #Parse command line flags
    inputted_flags = sys.argv[1:]
    
    # Check for multiple flags or incorrect flags
    number_of_flags = 0
    for flag in inputted_flags: 
        if flag.startswith("-"):
            if flag in ["-h", "-r", "-p", "-s"]:
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
        print("""-s <name>. When the -s inputted_flags is present, 412fe should read the file specified by <name> and print, to the standard
              output stream, a list of the token_stream that the scanner found.""")
        print("""-p <name>. When the -p inputted_flags is present, 412fe should read the file specified by <name>, scan it and parse it, 
              build the intermediate representation, and report either success or report all the errors that it finds in the input file.
              If the parse succeeds, the front end must report “Parse succeeded. Processed k operations.”, where k is the number of 
              operations the front end handled, printed without commas. If it finds errors, it must print “Parse found errors.”""")
        print("""-r <name>. When the -r inputted_flags is present, 412fe should read the file specified by <name>, scan it, parse it, build the 
              intermediate representation, and print out the information in the intermediate representation (in an appropriately human readable format).""")
        sys.exit()
    
    # Handle the "-r" flag
    elif "-r" in inputted_flags:
        try:
            # Open the specified file
            FILENAME = open(inputted_flags[-1])
            BUFFER = FILENAME.readline()
            
            errors_total, _ = parsing_iloc() # Parse the file and check for errors
            if errors_total == 0: # If no errors, print the intermediate representation
                CURRENT_NODE = HEAD_NODE  
                labels = ["Line", "Opcode", "SR", "VR", "PR", "NU", "SR", "VR", "PR", "NU", "SR", "VR", "PR", "NU"] 
                while CURRENT_NODE != None:
                    data = CURRENT_NODE.information
                    updated_data = REVERSE_LEXEMES[data[1]]
                    data[1] = updated_data
                    ir_representation(labels, data)
                    CURRENT_NODE = CURRENT_NODE.next
            else:
                print("ERROR: Cannot display internal representation because there exists an error withiin the ILOC")
            
            FILENAME.close()
        except:
            print(f"ERROR: Could not open the given file path", file=sys.stderr)
            sys.exit()       
        
    # Handle the "-p" flag 
    elif "-s" not in inputted_flags or "-p" in inputted_flags:
        try:
            
            # Open the specified file
            FILENAME = open(inputted_flags[-1])
            BUFFER = FILENAME.readline()
            
            errors_total, operations_total = parsing_iloc() # Parse the file and count errors and operations
            if errors_total > 0: 
                print(f"Parse failed, finding errors on {errors_total} lines")
            else: 
                print(f"Parse succeeded. Processed {operations_total} operations.")   
            
            FILENAME.close()
        except:
            print(f"ERROR: Could not open the given file path", file=sys.stderr)
            sys.exit()       
        
    # Handle the "-s" flag 
    elif "-s" in inputted_flags:
        try:
            # Open the specified file 
            FILENAME = open(inputted_flags[-1])
            BUFFER = FILENAME.readline()
            
            # Run the scanner, scanning one token at a time
            token_stream = []
            while True:
                scanned_token = scanning_iloc()
                if scanned_token[0] == CATEGS["EOF"]:
                    break
                token_stream.append(scanned_token)
                
                
            # Print the scanned token stream line by line
            print_line = 1
            for token in token_stream:
                if token[0] == CATEGS["REGISTER"] or  token[0] == CATEGS["CONSTANT"]:
                    print(f"{print_line}, {REVERSE_CATEGS[token[0]]}, {token[1]}")
                else:
                    print(f"{print_line}, {REVERSE_CATEGS[token[0]]}, {REVERSE_LEXEMES[token[1]]}")
                if token[0] == CATEGS["EOL"]:
                    print_line += 1
                
            # Close the file
            FILENAME.close()
        except:
            print(f"ERROR: Could not open the given file path", file=sys.stderr) #If the file could not be opened
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
    global LINE_NUMBER, CURRENT_NODE, HEAD_NODE  # Reference global variables to keep track of and modify


    final_token = [CATEGS["EOL"], CATEGS["EOF"]] # Define final tokens representing end of line (EOL) or end of file (EOF)
    error_word = None    # Variable to store the category of the word that caused an error
    errors_total = 0     # Counter for the total number of errors encountered
    parsing_error = False # Flag to indicate if a parsing error has occurred
    operations_total = 0 # Counter for the total number of operations parsed successfully

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
                            if CURRENT_NODE is None:
                                HEAD_NODE.information[0] = LINE_NUMBER
                                HEAD_NODE.information[1] = first_lexeme
                                HEAD_NODE.information[2] = lexeme1
                                HEAD_NODE.information[10] = lexeme2
                                CURRENT_NODE = HEAD_NODE
                            else:
                                new = IR_Node()
                                new.information[0] = LINE_NUMBER
                                new.information[1] = first_lexeme
                                new.information[2] = lexeme1
                                new.information[10] = lexeme2
                                new.prev = CURRENT_NODE
                                CURRENT_NODE.next = new
                                CURRENT_NODE = new
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
                                    if CURRENT_NODE is None:
                                        HEAD_NODE.information[0] = LINE_NUMBER
                                        HEAD_NODE.information[1] = first_lexeme
                                        HEAD_NODE.information[2] = lexeme1
                                        HEAD_NODE.information[6] = lexeme2
                                        HEAD_NODE.information[10] = lexeme3
                                        CURRENT_NODE = HEAD_NODE
                                    else:
                                        new = IR_Node()
                                        new.information[0] = LINE_NUMBER
                                        new.information[1] = first_lexeme
                                        new.information[2] = lexeme1
                                        new.information[6] = lexeme2
                                        new.information[10] = lexeme3
                                        new.prev = CURRENT_NODE
                                        CURRENT_NODE.next = new
                                        CURRENT_NODE = new
                                else:
                                    error_word = next_category
                                    parsing_error = True
                                    print(f"ERROR {LINE_NUMBER}: Expected EOL or EOF but encountered " + str(REVERSE_CATEGS[next_category]), file=sys.stderr)


        elif first_categ == CATEGS["NOP"]:  # Handle no-operation
            next_category, _ = scanning_iloc()
            if next_category in final_token: # Create the node for the intermediate representation
                parsing_error = False 
                if CURRENT_NODE is None:
                    HEAD_NODE.information[0] = LINE_NUMBER
                    HEAD_NODE.information[1] = first_lexeme
                    CURRENT_NODE = HEAD_NODE
                else:
                    new = IR_Node()
                    new.information[0] = LINE_NUMBER
                    new.information[1] = first_lexeme
                    new.prev = CURRENT_NODE
                    CURRENT_NODE.next = new
                    CURRENT_NODE = new
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
                    if CURRENT_NODE is None:
                        HEAD_NODE.information[0] = LINE_NUMBER
                        HEAD_NODE.information[1] = first_lexeme
                        HEAD_NODE.information[2] = lexeme1
                        CURRENT_NODE = HEAD_NODE
                    else:
                        new = IR_Node()
                        new.information[0] = LINE_NUMBER
                        new.information[1] = first_lexeme
                        new.information[2] = lexeme1
                        new.prev = CURRENT_NODE
                        CURRENT_NODE.next = new
                        CURRENT_NODE = new
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
                            if CURRENT_NODE is None:
                                HEAD_NODE.information[0] = LINE_NUMBER
                                HEAD_NODE.information[1] = first_lexeme
                                HEAD_NODE.information[2] = lexeme1
                                HEAD_NODE.information[10] = lexeme2
                                CURRENT_NODE = HEAD_NODE
                            else:
                                new = IR_Node()
                                new.information[0] = LINE_NUMBER
                                new.information[1] = first_lexeme
                                new.information[2] = lexeme1
                                new.information[10] = lexeme2
                                new.prev = CURRENT_NODE
                                CURRENT_NODE.next = new
                                CURRENT_NODE = new
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

    return errors_total, operations_total

#Used to be able to run the file from command line
if __name__ == '__main__':
    main()