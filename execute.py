import arr
from compile import c
import decode
import bit

def auipc():
    decode.u()
    c("LET REGVALUE=PC+IMM")
    decode.cut("REGVALUE", 32, "REGVALUE")
    arr.reg_store("RD", "REGVALUE")
    c("LET PC=PC+4")

def lui():
    decode.u()
    arr.reg_store("RD", "IMM")
    c("LET PC=PC+4")

def addi():
    arr.reg_load("RS1", "REGVALUE")
    c("LET REGVALUE=REGVALUE+IMM")
    decode.cut("REGVALUE", 32, "REGVALUE")
    arr.reg_store("RD", "REGVALUE")

def ori():
    arr.reg_load("RS1", "REGVALUE1")
    bit.bor("REGVALUE1", "IMM", "REGVALUE", 12)
    arr.reg_store("RD", "REGVALUE")

def andi():
    arr.reg_load("RS1", "REGVALUE1")
    bit.band("REGVALUE1", "IMM", "REGVALUE", 12)
    arr.reg_store("RD", "REGVALUE")

def xori():
    arr.reg_load("RS1", "REGVALUE1")
    bit.bxor("REGVALUE1", "IMM", "REGVALUE")
    arr.reg_store("RD", "REGVALUE")

def sltiu():
    arr.reg_load("RS1", "REGVALUE1")
    c("LET REGVALUE=0")
    c("IF REGVALUE1<IMM THEN REGVALUE=1")
    arr.reg_store("RD", "REGVALUE")

def add():
    c(f"LET DOSUB=INSTRUCTION/{1<<30}")
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE")
    c(f"IF DOSUB>1 THEN REGVALUE={1 << 32}/2*2-REGVALUE/2*2")
    c("LET REGVALUE=REGVALUE1+REGVALUE")
    decode.cut("REGVALUE", 32, "REGVALUE")
    arr.reg_store("RD", "REGVALUE")

def bor():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    bit.bor("REGVALUE1", "REGVALUE2", "REGVALUE", 32)
    arr.reg_store("RD", "REGVALUE")

def band():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    bit.band("REGVALUE1", "REGVALUE2", "REGVALUE", 32)
    arr.reg_store("RD", "REGVALUE")

def bxor():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    bit.bxor("REGVALUE1", "REGVALUE2", "REGVALUE")
    arr.reg_store("RD", "REGVALUE")

def sltu():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    c("LET REGVALUE=0")
    c("IF REGVALUE1<REGVALUE2 THEN REGVALUE=1")
    arr.reg_store("RD", "REGVALUE")

def lb():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load1("REGVALUE+IMM", "MEMVALUE1") # overflow ignored, idk
    decode.sign_extend("MEMVALUE1", 8)
    arr.reg_store("RD", "MEMVALUE1")

def lh():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load2("REGVALUE+IMM", "MEMVALUE") # overflow ignored, idk
    decode.sign_extend("MEMVALUE", 16)
    arr.reg_store("RD", "MEMVALUE")

def lw():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load4("REGVALUE+IMM", "MEMVALUE") # overflow ignored, idk
    arr.reg_store("RD", "MEMVALUE")

def lbu():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load1("REGVALUE+IMM", "MEMVALUE1") # overflow ignored, idk
    arr.reg_store("RD", "MEMVALUE1")

def lhu():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load2("REGVALUE+IMM", "MEMVALUE") # overflow ignored, idk
    arr.reg_store("RD", "MEMVALUE")

def print_regs():
    c('PRINT "REGS:"')
    for i in range(32): c(f"PRINT REGN{i}")
    c("LET PC=PC+4")

def r():
    decode.r()
    c("IF FUNCT3==0 THEN GOTO ERLADD")
    c("IF FUNCT3==3 THEN GOTO ERLSLTU")
    c("IF FUNCT3==4 THEN GOTO ERLXOR")
    c("IF FUNCT3==6 THEN GOTO ERLOR")
    c("IF FUNCT3==7 THEN GOTO ERLAND")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("ERLSLTU:")
    sltu()
    c("GOTO ERLEND")
    c("ERLXOR:")
    bxor()
    c("GOTO ERLEND")
    c("ERLAND:")
    band()
    c("GOTO ERLEND")
    c("ERLOR:")
    bor()
    c("GOTO ERLEND")
    c("ERLADD:")
    add()
    c("ERLEND:")
    c("LET PC=PC+4")

def l():
    decode.i()
    c("IF FUNCT3==0 THEN GOTO ELLLB")
    c("IF FUNCT3==1 THEN GOTO ELLLH")
    c("IF FUNCT3==2 THEN GOTO ELLLW")
    c("IF FUNCT3==4 THEN GOTO ELLLBU")
    c("IF FUNCT3==5 THEN GOTO ELLLHU")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("ELLLH:")
    lh()
    c("GOTO ELLEND")
    c("ELLLW:")
    lw()
    c("GOTO ELLEND")
    c("ELLLBU:")
    lbu()
    c("GOTO ELLEND")
    c("ELLLHU:")
    lhu()
    c("GOTO ELLEND")
    c("ELLLB:")
    lb()
    c("ELLEND:")
    c("LET PC=PC+4")

def i():
    decode.i()
    c("IF FUNCT3==0 THEN GOTO EILADDI")
    c("IF FUNCT3==3 THEN GOTO EILSLTIU")
    c("IF FUNCT3==4 THEN GOTO EILXORI")
    c("IF FUNCT3==6 THEN GOTO EILORI")
    c("IF FUNCT3==7 THEN GOTO EILANDI")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("EILSLTIU:")
    sltiu()
    c("GOTO EILEND")
    c("EILXORI:")
    xori()
    c("GOTO EILEND")
    c("EILANDI:")
    andi()
    c("GOTO EILEND")
    c("EILORI:")
    ori()
    c("GOTO EILEND")
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
    c("IF OPCODE==55 THEN GOTO ELLUI")
    c("IF OPCODE==1 THEN GOTO ELPRINTREGS")
    c('PRINT "INVALID OPCODE"')
    c("PRINT OPCODE")
    c("GOTO THEEND")
    c("ELPRINTREGS:")
    print_regs()
    c("GOTO ELEND")
    c("ELR:")
    r()
    c("GOTO ELEND")
    c("ELL:")
    l()
    c("GOTO ELEND")
    c("ELAUIPC:")
    auipc()
    c("GOTO ELEND")
    c("ELLUI:")
    lui()
    c("GOTO ELEND")
    c("ELI:")
    i()
    c("ELEND:")
