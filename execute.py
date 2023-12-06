import arr
from compile import c
import decode

def auipc():
    decode.u()
    c("LET REGVALUE=PC+IMM") # overflow ignored, idk
    arr.reg_store("RD", "REGVALUE")
    c("LET PC=PC+4")

def addi():
    arr.reg_load("RS1", "REGVALUE")
    c("LET REGVALUE=REGVALUE+IMM")
    decode.cut("REGVALUE", 32, "REGVALUE")
    arr.reg_store("RD", "REGVALUE")

def add():
    arr.reg_load("RS1", "REGVALUE")
    arr.reg_load("RS2", "REGVALUE2")
    c("LET REGVALUE=REGVALUE+REGVALUE2")
    decode.cut("REGVALUE", 32, "REGVALUE")
    arr.reg_store("RD", "REGVALUE")

def lb():
    arr.reg_load("RS1", "REGVALUE")
    arr.mem_load1("REGVALUE+IMM", "MEMVALUE") # overflow ignored, idk
    decode.sign_extend("MEMVALUE", 8)
    arr.reg_store("RD", "MEMVALUE")

def r():
    decode.r()
    c("IF FUNCT3==0 THEN GOTO ERLADD")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("ERLADD:")
    add()
    c("ERLEND:")
    c("LET PC=PC+4")

def l():
    decode.i()
    c("IF FUNCT3==0 THEN GOTO ELLLB")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("ELLLB:")
    lb()
    c("ELLEND:")
    c("LET PC=PC+4")

def i():
    decode.i()
    c("IF FUNCT3==0 THEN GOTO EILADDI")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("EILADDI:")
    addi()
    c("EILEND:")
    c("LET PC=PC+4")

def execute():
    arr.mem_load4("PC", "INSTRUCTION")
    decode.cut("INSTRUCTION", 7, "OPCODE")
    c("IF OPCODE==19 THEN GOTO ELI")
    c("IF OPCODE==51 THEN GOTO ELR")
    c("IF OPCODE==3 THEN GOTO ELL")
    c("IF OPCODE==23 THEN GOTO ELAUIPC")
    c('PRINT "INVALID OPCODE"')
    c("PRINT OPCODE")
    c("GOTO THEEND")
    c("ELR:")
    r()
    c("GOTO ELEND")
    c("ELL:")
    l()
    c("GOTO ELEND")
    c("ELAUIPC:")
    auipc()
    c("GOTO ELEND")
    c("ELI:")
    i()
    c("ELEND:")
