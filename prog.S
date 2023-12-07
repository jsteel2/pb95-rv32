nop
nop
auipc t5, 0
addi t5, t5, 56
lh x25, 5(t5)
lw x26, 7(t5)
lhu x27, 5(t5)
lbu t6, 4(t5)
add t6, t6, t6
add t6, t6, t6
add t6, t6, t6
addi t2, t6, 4
addi t6, t2, 69
addi t2, x0, 8
sub t6, t6, t2
ori t4, t6, 69
.word 0
.byte 2
.half 42069
.word 999999
