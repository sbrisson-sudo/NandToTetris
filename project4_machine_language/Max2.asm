	@R0
	D=M
	@R1
	D=D-M
	@ALT
	D;JLT
	@R0
	D=M
	@R2
	M=D
	@END
	0;JMP
(ALT)
	@R1
	D=M
	@R2
	M=D
(END)
	@END
	0;JMP