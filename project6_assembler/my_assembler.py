#! /bin/python3
# Assembler of the Hack assembly language to the Hack instruction set binary code

import sys, os
import re 
import numpy as np 

pattern_c_inst = r"^(?:(?P<dest>[A-Z]+)=)?(?P<comp>[^;=]+)(?:;(?P<jump>[A-Z]+))?$"

JUMP_CODE = {
    "JGT" : "001",
    "JEQ" : "010",
    "JGE" : "011",
    "JLT" : "100",
    "JNE" : "101",
    "JLE" : "110",
    "JMP" : "111",
    ""    : "000"
}

DEST_CODE = {
    "M"     : "001",
    "D"     : "010",
    "DM"    : "011",
    "MD"    : "011",
    "A"     : "100",
    "AM"    : "101",
    "MA"    : "101",
    "AD"    : "110",
    "DA"    : "110",
    "ADM"   : "111",
    "AMD"   : "111",
    "DMA"   : "111",
    "DAM"   : "111",
    "MAD"   : "111",
    "MDA"   : "111",
    ""      : "000"
}

COMP_CODE = {
    "0"   : "0101010",
    "1"   : "0111111",
    "-1"  : "0111010",
    "D"   : "0001100",
    "A"   : "0110000",
    "!D"  : "0001101",
    "!A"  : "0110011",
    "D+1" : "0011111",
    "1+D" : "0011111",
    "A+1" : "0110111",
    "1+A" : "0110111",
    "D-1" : "0001110",
    "A-1" : "0110010",
    "D+A" : "0000010",
    "A+D" : "0000010",
    "D-A" : "0010011",
    "A-D" : "0000111",
    "D&A" : "0000000",
    "A&D" : "0000000",
    "D|A" : "0010101",
    "A|D" : "0010101",
    "M"   : "1110000",
    "!M"  : "1110001",
    "-M"  : "1110011",
    "M+1" : "1110111",
    "1+M" : "1110111",
    "M-1" : "1110010",
    "D+M" : "1000010",
    "M+D" : "1000010",
    "D-M" : "1010011",
    "M-D" : "1000111",
    "D&M" : "1000000",
    "M&D" : "1000000",
    "D|M" : "1010101",
    "M|D" : "1010101"
}

def get_free_address(address_list):
    """Get the smallest integer not in the list <address_list>"""
    addresses = np.array(address_list)
    addresses.sort()
    first_gap = np.argmax( (addresses[1:] - addresses[:-1]) > 1)
    addr = addresses[first_gap] + 1
    return addr


if __name__ == "__main__":

    # Initializing the data structures
    variables_address_table = dict(zip([f"R{i}" for i in range(16)], list(range(16))))
    variables_address_table["SCREEN"] = 16384
    variables_address_table["KBD"] = 24576
    labels_table = {}

    # Load the .asm file provided in the command line
    if len(sys.argv) != 2:
        print("Usage : python assembler.py <prog.asm>")
        exit()

    with open(sys.argv[1], "r") as infile:
        lines = infile.readlines()

    # We store our binary file as a list of strings
    binary = []

    # Remove the ending newline character
    lines = [line.replace("\n","") for line in lines]

    # Filter out empty lines and comment lines
    lines = [
        line for line in lines
        if not re.match(r'^\s*(//|$)', line)
    ]

    # Step 2: Remove all tabs and whitespaces from remaining lines
    lines = [re.sub(r'\s+', '', line) for line in lines]

    # First iteration to get all the labels
    n_labels = 0
    for i,l in  enumerate(lines):
        if l[0] == "(":
            label_line_number = i - n_labels
            labels_table[l[1:-1]] = label_line_number
            n_labels += 1

    # Iterating over the lines
    for l in  lines:
        if l[0] == "(":
            # Label -> pass
            pass

        else :
            # -> instruction
            # Getting isf it starts with @
            if l[0] == "@":
                # A-instruction
                address = l[1:]
                try:
                    # We try to convert it to int
                    address_int = int(address)
                except ValueError:
                    # It is not an int -> it is a variable
                    var_name = address

                    if var_name in variables_address_table.keys():
                        address_int = variables_address_table[var_name]

                    elif var_name in labels_table.keys():
                        address_int = labels_table[var_name]

                    else:
                        address_int = get_free_address(list(variables_address_table.values()))
                        variables_address_table[var_name] = address_int

                # Appending the instruction bin code
                binary.append("0" + f"{address_int:015b}")  

            else:
                # C-instruction
                # Among  dest=comp comp;jump dest=comp;jump
                match = re.match(pattern_c_inst, l)
                if match:
                    dest = match.group("dest") or ""
                    comp = match.group("comp") or ""
                    jump = match.group("jump") or ""
                    
                    # Appending the instruction bin code
                    binary.append("111" + COMP_CODE[comp] + DEST_CODE[dest] + JUMP_CODE[jump])  

                else: 
                    raise Exeption("C instruction not matched : " + l)

    print(variables_address_table)

    # Save the produced file in a .hack file (text file)
    with open(sys.argv[1].replace(".asm",".hack"), "w") as f_out:
        for line in binary[:-1]:
            f_out.write(line)
            f_out.write("\n")
        f_out.write(binary[-1])

    # Save the produced file in a .binhack file (binary file)
    # Convert the string to bytes
    binary_string = "".join(binary)
    binary_data = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder="big")

    # Write the binary data to a file
    with open(sys.argv[1].replace(".asm",".binhack"), "wb") as binary_file:
        binary_file.write(binary_data)


        


