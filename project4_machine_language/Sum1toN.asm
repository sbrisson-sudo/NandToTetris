    @R1
    M=0
    @R2
    M=0
(LOOP)
    @1
    D=A
    @R1 
    M=D+M
    D=M
    @R2
    M=D+M
    @R1
    D=M
    @R0
    D=D-M
    @END
    D;JEQ
    @LOOP
    0;JMP
(END)
    @END
    0;JMP

