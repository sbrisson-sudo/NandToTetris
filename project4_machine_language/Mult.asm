    @i
    M=0
    @res
    M=0
(LOOP)
    @R1
    D=M
    @i
    D=D-M
    @END
    D;JEQ
    @i
    M=M+1
    @R0
    D=M
    @res
    M=D+M
    @LOOP
    0;JMP
(END)
    @END
    0;JMP
    