#! /bin/python3
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

    def __init__(self, fileout):
        """Initiate the list of assembly commands and store the output file name"""
        self.asm_commands = []
        self.asm_filename = fileout
        self.logic_label_index = 0

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
                    f"@LOGIC_YES.{i}",
                    "D;JEQ",
                    "@SP",
                    "A=M-1",
                    "M=0",
                    f"@LOGIC_NO.{i}",
                    "0;JMP",
                    f"(LOGIC_YES.{i})",
                    "@SP",
                    "A=M-1",
                    "M=-1",
                    f"(LOGIC_NO.{i})"
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
                    f"@LOGIC_YES.{i}",
                    "D;JGT",
                    "@SP",
                    "A=M-1",
                    "M=0",
                    f"@LOGIC_NO.{i}",
                    "0;JMP",
                    f"(LOGIC_YES.{i})",
                    "@SP",
                    "A=M-1",
                    "M=-1",
                    f"(LOGIC_NO.{i})"
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
                    f"@LOGIC_YES.{i}",
                    "D;JLT",
                    "@SP",
                    "A=M-1",
                    "M=0",
                    f"@LOGIC_NO.{i}",
                    "0;JMP",
                    f"(LOGIC_YES.{i})",
                    "@SP",
                    "A=M-1",
                    "M=-1",
                    f"(LOGIC_NO.{i})"
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
                print(f"Can't use command {command} on segment {constant}")
        
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
        print(f"Usage : {sys.argv[0]} <prog.vm>")
        exit()

    # Construct Parser
    parser = Parser(sys.argv[1])

    # Initiate assembly code write
    code_writer = CodeWriter(sys.argv[1].replace(".vm", ".asm"))

    # Loop on lines
    while True:

        parser.commandType()

        print(parser.current_type)

        if parser.current_type == "C_ARITHMETIC":
            code_writer.writeArithmetic(parser.arg1())

        elif parser.current_type in ["C_PUSH", "C_POP"]:
            code_writer.writePushPop(parser.current_type, parser.arg1(), parser.arg2())

        if parser.hasMoreLines() :
            parser.advance()
        else : 
            break

    code_writer.close()
    
    

