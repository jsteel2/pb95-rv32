nop
nop
auipc t5, 0
addi t5, t5, 32
lb t6, 4(t5)
add t6, t6, t6
add t6, t6, t6
add t6, t6, t6
addi t2, t6, 4
addi t6, t2, 69
b: .word 0
a: .byte 2
