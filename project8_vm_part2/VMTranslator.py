#! /bin/python
# Assembler of the Hack assembly language to the Hack instruction set binary code

import sys, os
import re 
import numpy as np 

class Parser:

    def __init__(self, file):
        """Initiate the parser on a VM script file"""

        # Reading it as a list of lines
        with open(file, "r") as fd_in:
            lines = fd_in.readlines()

        # Remove the ending newline character
        lines = [line.replace("\n","") for line in lines]

        # Filter out empty lines and comment lines
        lines = [
            line for line in lines
            if not re.match(r'^\s*(//|$)', line)
        ]

        # We split on spaces 
        lines_splitted = [re.split(r'\s+', line.strip()) for line in lines]

        self.lines = lines_splitted # Declare it as an object
        self.current_i = 0 # Pointer to the current instruction
        self.current = self.lines[0] # Current instruction
        self.current_type = ""

    def hasMoreLines(self):
        """Return boolean if there is more lines to go through"""
        return self.current_i < len(self.lines) - 1

    def advance(self):
        """Read the next instruction and make it the current instruction"""
        self.current_i += 1
        self.current = self.lines[self.current_i]
        return

    def commandType(self):
        """Read the current VM instruction and return its type, among : C_ARITHMETIC, C_PUSH, C-POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL"""
        match self.current[0]:
            case "push" : self.current_type = "C_PUSH"
            case "pop" : self.current_type = "C_POP"
            case "label" : self.current_type = "C_LABEL"
            case "goto" : self.current_type = "C_GOTO"
            case "if-goto" : self.current_type = "C_IF"
            case "function" : self.current_type = "C_FUNCTION"
            case "call" : self.current_type = "C_CALL"
            case "return" : self.current_type = "C_RETURN"
            case _: self.current_type = "C_ARITHMETIC"

    def arg1(self):
        """Return the first argument of the current command (note, for C_ARITHMETIC returns the command itself as a string)"""
        if self.current_type == "C_ARITHMETIC": 
            return self.current[0]
        return self.current[1]

    def arg2(self):
        """Return the second argument of the command (only for C_PUSH, C-POP, C_FUNCTION, or C_CALL)"""
        if self.current_type in ["C_PUSH","C_POP","C_FUNCTION","C_CALL"]:
            return self.current[2]
        return

class CodeWriter:

    def __init__(self, filename, fileout):
        """Initiate the list of assembly commands, take as input the name of the file (without suffix and path) and the output file name"""
        self.asm_commands = []
        self.fn = filename
        self.asm_filename = fileout
        self.logic_label_index = 0

        # variables for naming of labels
        self.current_function = None
        self.ith_function_call = 0

    def writeArithmetic(self, command):
        """Convert a VM arithmetic command into assembly code (ie apply an arithmetic/logical command on the stack)"""
        match command:
            case "add":
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@SP",
                    "A=M-1",
                    "M=D+M"
                ]
            case "sub":
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@SP",
                    "A=M-1",
                    "M=M-D"
                ]
            case "neg":
                asm_code = [
                    "@SP",
                    "A=M-1",
                    "M=-M"
                ]
            case "eq":
                self.logic_label_index += 1
                i = self.logic_label_index
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@SP",
                    "A=M-1",
                    "D=D-M",
                    f"@{self.fn}.LOGIC_YES.{i}",
                    "D;JEQ",
                    "@SP",
                    "A=M-1",
                    "M=0",
                    f"@{self.fn}.LOGIC_NO.{i}",
                    "0;JMP",
                    f"({self.fn}.LOGIC_YES.{i})",
                    "@SP",
                    "A=M-1",
                    "M=-1",
                    f"({self.fn}.LOGIC_NO.{i})"
                ]
            case "gt":
                self.logic_label_index += 1
                i = self.logic_label_index
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@SP",
                    "A=M-1",
                    "D=M-D",
                    f"@{self.fn}.LOGIC_YES.{i}",
                    "D;JGT",
                    "@SP",
                    "A=M-1",
                    "M=0",
                    f"@{self.fn}.LOGIC_NO.{i}",
                    "0;JMP",
                    f"({self.fn}.LOGIC_YES.{i})",
                    "@SP",
                    "A=M-1",
                    "M=-1",
                    f"({self.fn}.LOGIC_NO.{i})"
                ]
            case "lt":
                self.logic_label_index += 1
                i = self.logic_label_index
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@SP",
                    "A=M-1",
                    "D=M-D",
                    f"@{self.fn}.LOGIC_YES.{i}",
                    "D;JLT",
                    "@SP",
                    "A=M-1",
                    "M=0",
                    f"@{self.fn}.LOGIC_NO.{i}",
                    "0;JMP",
                    f"({self.fn}.LOGIC_YES.{i})",
                    "@SP",
                    "A=M-1",
                    "M=-1",
                    f"({self.fn}.LOGIC_NO.{i})"
                ]
            case "and":
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@SP",
                    "A=M-1",
                    "M=D&M"
                ]
            case "or":
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@SP",
                    "A=M-1",
                    "M=D|M"
                ]

            case "not":
                asm_code = [
                    "@SP",
                    "A=M-1",
                    "M=!M"
                ]

            case _:
                print(f"Unknown arithmetic/logical command : {command}")

        self.asm_commands += asm_code

    def writePushPop(self, command, segment, index):
        """Push or pop from the stack onto the segment <segment> at index <index>
        command can be either "C_PUSH" or "C_POP"
        segment must be among : local, argument, this, that, constant, static, temp, pointer
        Here are how the different segments are implemented : 
        - constant : can only be pushed to the stack
        - local : RAM block whose base address is kept in address LCL
        - argument : RAM block whose base address is kept in address ARG
        - this : RAM block whose base address is kept in address THIS
        - that : RAM block whose base address is kept in address THAT
        - static : RAM block whose base address is 16
        - temp : RAM block of length 8 and whose base address is 5
        - pointer : more on that later
        """

        # Table of the RAM block base address :
        BASE_ADDRESS_POINTER = {
            "local" : "LCL",
            "argument" : "ARG",
            "this" : "THIS",
            "that" : "THAT"
        }

        BASE_ADDRESS = {
            "static" : "16",
            "temp" : "5"
        }

        # Pushing a constant
        if segment == "constant":
            if command == "C_PUSH":
                asm_code = [
                    f"@{index}",
                    "D=A",
                    "@SP",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1",
                ]
            else : 
                print(f"Can't use command {command} on segment {segment}")
        
        # Pushing from / popping to a RAM block
        elif segment in ["local", "argument", "this", "that"]:
            base_ad = BASE_ADDRESS_POINTER[segment]
            if command == "C_PUSH":
                # D <- RAM[base_ad] + index ; RAM[SP] <- D ; SP++ ; 
                asm_code = [
                    f"@{index}",
                    "D=A",
                    f"@{base_ad}",
                    "A=D+M",
                    "D=M",
                    "@SP",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1",
                ]
            else :
                # C_POP
                # BA += i ; SP-- ; D <- RAM[SP] ; RAM[BA] <- D ; BA -= i
                asm_code = [
                    f"@{index}",
                    "D=A",
                    f"@{base_ad}",
                    "M=D+M",
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    f"@{base_ad}",
                    "A=M",
                    "M=D",
                    f"@{index}",
                    "D=A",
                    f"@{base_ad}",
                    "M=M-D",
                ]

        # Pushing from / popping to a RAM block
        elif segment in ["temp", "static"]:
            base_ad = BASE_ADDRESS[segment]
            if command == "C_PUSH":
                # D <- RAM[base_ad+index] ; RAM[SP] <- D ; SP++ ; 
                asm_code = [
                    f"@{index}",
                    "D=A",
                    f"@{base_ad}",
                    "A=D+A",
                    "D=M",
                    "@SP",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1"
                ]
            else :
                # C_POP
                # R13 <- base + index ; RAM[R13] <- RAM[SP-1] ; SP--
                asm_code = [
                    f"@{index}",
                    "D=A",
                    f"@{base_ad}",
                    "D=D+A",
                    "@R13",
                    "M=D",
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    "@R13",
                    "A=M",
                    "M=D"
                ]
        elif segment == "pointer":
            dest = {'0' : "THIS", '1' : "THAT"}[index]
            if command == "C_PUSH":
                asm_code = [
                    f"@{dest}",
                    "D=M",
                    "@SP",
                    "A=M",
                    "M=D",
                    "@SP",
                    "M=M+1",
                ]
            else : 
                asm_code = [
                    "@SP",
                    "M=M-1",
                    "A=M",
                    "D=M",
                    f"@{dest}",
                    "M=D"
                ]

        else : 
            print(f"Unknown segment : {segment}")

        self.asm_commands += asm_code

    def _getFullLabel(self, label):
        """Get the full label name : <filename>.<function>$<label>"""
        if self.current_function is None:
            label_name = f"{self.fn}${label}"
        else : 
            label_name = f"{self.fn}.{self.current_function}${label}"
        return label_name

    def writeLabel(self, label):
        """Write a label in the VM code as a label in the assembly code""" 
        full_label = self._getFullLabel(label)       
        self.asm_commands.append(f"({full_label})")

    def writeGoto(self, label):
        """Write an unconditionnal goto"""
        full_label = self._getFullLabel(label) 
        asm_code = [
            f"@{full_label}",
            "0;JMP"
        ]
        self.asm_commands += asm_code

    def writeIf(self, label):
        """Write an unconditionnal goto : pop on the stack and do conditionnal JGT jump on it"""
        full_label = self._getFullLabel(label) 
        asm_code = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{full_label}",
            "D;JGT"
        ]
        self.asm_commands += asm_code
    
    def close(self):
        """Generate the assembly script"""
        with open(self.asm_filename, "w") as fd_out:
            for line in self.asm_commands[:-1]:
                fd_out.write(line)
                fd_out.write("\n")
            fd_out.write(self.asm_commands[-1])
            
        print(f"Assembly code written in {self.asm_filename}")

if __name__ == "__main__":

    # Getting the VM script path thought CL argument
    if len(sys.argv) != 2:
        print(f"Usage : {sys.argv[0]} <prog.vm | progDirectory>")
        exit()

    # Check if the input is a vm file or a directory
    if sys.argv[1].endswith(".vm"):
        usage_mode = "standalone_source_file"

    else:
        if os.path.isdir(sys.argv[1]):
            src_dir = sys.argv[1]
            # List all the files ending with .vm
            files = os.listdir(src_dir)
            vm_files = []
            for f in files:
                if f.endswith(".vm"):
                    vm_files.append(f.split("/")[-1]) # Get the file name, without the path

            # Exit if no vm file found
            if len(vm_files) == 0:
                print("Error : no VM code file found in the supplied directory (must end with .vm)")
                exit()
            # Check if the Sys.vm file exists
            if not("Sys.vm" in vm_files):
                print("Error : no Sys.vm code file found in the supplied directory")
                exit()
            # Open the Sys.vm file and check for the presence of the Sys.init function
            with open(os.path.join(src_dir, "Sys.vm")) as fd:
                sys_code = ''.join(fd.readlines())
                if not("function Sys.init" in sys_code):
                    print("Error : the Sys.vm file does not contain a Sys.init function decalaration")
                    exit()

            # We have a Sys.vm file and it contains a Sys.init function
            usage_mode = "bootstrap_and_sources"

    print(usage_mode)
    exit()

    # Construct Parser
    parser = Parser(sys.argv[1])

    # Initiate assembly code write
    fileout = sys.argv[1].replace(".vm", ".asm")
    filename = sys.argv[1].split("/")[-1][:-3]
    code_writer = CodeWriter(filename, fileout)

    # Loop on lines
    while True:

        parser.commandType()

        print(parser.current_type)

        if parser.current_type == "C_ARITHMETIC":
            code_writer.writeArithmetic(parser.arg1())

        elif parser.current_type in ["C_PUSH", "C_POP"]:
            code_writer.writePushPop(parser.current_type, parser.arg1(), parser.arg2())

        elif parser.current_type == "C_LABEL":
            code_writer.writeLabel(parser.arg1())

        elif parser.current_type == "C_GOTO":
            code_writer.writeGoto(parser.arg1())

        elif parser.current_type == "C_IF":
            code_writer.writeIf(parser.arg1())

        if parser.hasMoreLines() :
            parser.advance()
        else : 
            break

    code_writer.close()
    
    

