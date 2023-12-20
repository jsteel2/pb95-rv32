import arr
from compile import c
import decode
import bit

def auipc():
    decode.u()
    decode.cut("(PC+IMM)", 32, "REGVALUE")
    arr.reg_store("RD", "REGVALUE")
    c("LET PC=PC+4")

def lui():
    decode.u()
    arr.reg_store("RD", "IMM")
    c("LET PC=PC+4")

def addi():
    arr.reg_load("RS1", "REGVALUE")
    decode.cut("(REGVALUE+IMM)", 32, "REGVALUE")
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
    bit.bxor("REGVALUE1", "IMM", "REGVALUE", 12)
    arr.reg_store("RD", "REGVALUE")

def sltiu():
    arr.reg_load("RS1", "REGVALUE1")
    c("LET REGVALUE=0")
    c("IF REGVALUE1<IMM THEN REGVALUE=1")
    arr.reg_store("RD", "REGVALUE")

def slti():
    arr.reg_load("RS1", "REGVALUE1")
    c("LET REGVALUE=0")
    decode.to_signed("REGVALUE1")
    decode.to_signed("IMM")
    c("IF REGVALUE1<IMM THEN REGVALUE=1")
    arr.reg_store("RD", "REGVALUE")

def slli():
    arr.reg_load("RS1", "REGVALUE")
    c("IF IMM==0 THEN GOTO LBSSLID")
    c("LBSSLIL:")
    c("IF REGVALUE==0 THEN GOTO LBSSLID")
    decode.cut("(REGVALUE*2)", 32, "REGVALUE")
    c("LET IMM=IMM-1")
    c("IF IMM>0 THEN GOTO LBSSLIL")
    c("LBSSLID:")
    arr.reg_store("RD", "REGVALUE")

def srli():
    arr.reg_load("RS1", "REGVALUE")
    c("IF IMM==0 THEN GOTO LBSRLID")
    c("LBSRLIL:")
    c("IF REGVALUE==0 THEN GOTO LBSRLID")
    c("LET REGVALUE=(REGVALUE+0.5)/2-0.5+POW2OF52-POW2OF52")
    c("LET IMM=IMM-1")
    c("IF IMM>0 THEN GOTO LBSRLIL")
    c("LBSRLID:")
    arr.reg_store("RD", "REGVALUE")

def srai():
    arr.reg_load("RS1", "REGVALUE")
    c("IF IMM==0 THEN GOTO LBSRAID")
    c("LET MSB=0")
    c(f"IF REGVALUE>{(1 << 31) - 1} THEN MSB={1 << 31}")
    c("LBSRAIL:")
    c("IF REGVALUE==0 THEN GOTO LBSRAID")
    c("LET REGVALUE=(REGVALUE+0.5)/2-0.5+POW2OF52-POW2OF52+MSB")
    c("LET IMM=IMM-1")
    c("IF IMM>0 THEN GOTO LBSRAIL")
    c("LBSRAID:")
    arr.reg_store("RD", "REGVALUE")

def jalr():
    decode.i()
    arr.reg_load("RS1", "REGVALUE")
    arr.reg_store("RD", "PC+4")
    decode.to_signed("IMM")
    c("LET PC=((IMM+REGVALUE+0.5)/2-0.5+POW2OF52-POW2OF52)*2")

def jal():
    decode.j()
    arr.reg_store("RD", "PC+4")
    decode.to_signed("IMM")
    c("LET PC=PC+IMM")

def add():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE")
    c(f"IF FUNCT7>0 THEN REGVALUE={1 << 32}-REGVALUE")
    decode.cut("(REGVALUE1+REGVALUE)", 32, "REGVALUE")
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
    bit.bxor("REGVALUE1", "REGVALUE2", "REGVALUE", 32)
    arr.reg_store("RD", "REGVALUE")

def sltu():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    c("LET REGVALUE=0")
    c("IF REGVALUE1<REGVALUE2 THEN REGVALUE=1")
    arr.reg_store("RD", "REGVALUE")

def slt():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    c("LET REGVALUE=0")
    decode.to_signed("REGVALUE1")
    decode.to_signed("REGVALUE2")
    c("IF REGVALUE1<REGVALUE2 THEN REGVALUE=1")
    arr.reg_store("RD", "REGVALUE")

def sll():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    c(f"LET DAMNYOU=REGVALUE2/{1 << 5}+POW2OF52-POW2OF52")
    c(f"IF DAMNYOU>REGVALUE2/{1 << 5} THEN DAMNYOU=DAMNYOU-1")
    c(f"LET REGVALUE2=REGVALUE2-DAMNYOU*{1 << 5}")
    c("IF REGVALUE2==0 THEN GOTO LBSSLD")
    c("LBSSLL:")
    c("IF REGVALUE==0 THEN GOTO LBSSLD")
    decode.cut("(REGVALUE*2)", 32, "REGVALUE")
    c("LET REGVALUE2=REGVALUE2-1")
    c("IF REGVALUE2>0 THEN GOTO LBSSLL")
    c("LBSSLD:")
    arr.reg_store("RD", "REGVALUE")

def srl():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    c(f"LET DAMNYOU=REGVALUE2/{1 << 5}+POW2OF52-POW2OF52")
    c(f"IF DAMNYOU>REGVALUE2/{1 << 5} THEN DAMNYOU=DAMNYOU-1")
    c(f"LET REGVALUE2=REGVALUE2-DAMNYOU*{1 << 5}")
    c("IF REGVALUE2==0 THEN GOTO LBSRLD")
    c("LBSRLL:")
    c("IF REGVALUE==0 THEN GOTO LBSRLD")
    c("LET REGVALUE=(REGVALUE+0.5)/2-0.5+POW2OF52-POW2OF52")
    c("LET REGVALUE2=REGVALUE2-1")
    c("IF REGVALUE2>0 THEN GOTO LBSRLL")
    c("LBSRLD:")
    arr.reg_store("RD", "REGVALUE")

def sra():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    c(f"LET DAMNYOU=REGVALUE2/{1 << 5}+POW2OF52-POW2OF52")
    c(f"IF DAMNYOU>REGVALUE2/{1 << 5} THEN DAMNYOU=DAMNYOU-1")
    c(f"LET REGVALUE2=REGVALUE2-DAMNYOU*{1 << 5}")
    c("IF REGVALUE2==0 THEN GOTO LBSRAD")
    c("LET MSB=0")
    c(f"IF REGVALUE>{(1 << 31) - 1} THEN MSB={1 << 31}")
    c("LBSRAL:")
    c("IF REGVALUE==0 THEN GOTO LBSRAD")
    c("LET REGVALUE=(REGVALUE+0.5)/2-0.5+POW2OF52-POW2OF52+MSB")
    c("LET REGVALUE2=REGVALUE2-1")
    c("IF REGVALUE2>0 THEN GOTO LBSRAL")
    c("LBSRAD:")
    arr.reg_store("RD", "REGVALUE")

def lb():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load1("REGVALUE+IMM", "REGVALUE") # overflow ignored, idk
    decode.sign_extend("REGVALUE", 8)
    arr.reg_store("RD", "REGVALUE")

def lh():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load2("REGVALUE+IMM", "REGVALUE") # overflow ignored, idk
    decode.sign_extend("REGVALUE", 16)
    arr.reg_store("RD", "REGVALUE")

def lw():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load4("REGVALUE+IMM", "REGVALUE") # overflow ignored, idk
    arr.reg_store("RD", "REGVALUE")

def lbu():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load1("REGVALUE+IMM", "REGVALUE") # overflow ignored, idk
    arr.reg_store("RD", "REGVALUE")

def lhu():
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_load2("REGVALUE+IMM", "REGVALUE") # overflow ignored, idk
    arr.reg_store("RD", "REGVALUE")

def sb():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_store1("REGVALUE+IMM", "REGVALUE2")

def sh():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_store2("REGVALUE+IMM", "REGVALUE2")

def sw():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    arr.mem_store4("REGVALUE+IMM", "REGVALUE2")

def bltu():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    c(f"LET PC=PC+4")
    c(f"IF REGVALUE<REGVALUE2 THEN PC=PC+IMM-4")

def beq():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    c(f"LET PC=PC+4")
    c(f"IF REGVALUE==REGVALUE2 THEN PC=PC+IMM-4")

def bne():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    c(f"LET PC=PC+IMM")
    c(f"IF REGVALUE==REGVALUE2 THEN PC=PC-IMM+4")

def blt():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    decode.to_signed("REGVALUE2")
    decode.to_signed("REGVALUE")
    c(f"LET PC=PC+4")
    c(f"IF REGVALUE<REGVALUE2 THEN PC=PC+IMM-4")

def bge():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    decode.to_signed("REGVALUE2")
    decode.to_signed("REGVALUE")
    c(f"LET PC=PC+4")
    c(f"IF REGVALUE+1>REGVALUE2 THEN PC=PC+IMM-4")

def bgeu():
    arr.reg_load("RS2", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE")
    decode.to_signed("IMM")
    c(f"LET PC=PC+4")
    c(f"IF REGVALUE+1>REGVALUE2 THEN PC=PC+IMM-4")

def amoswap():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    arr.mem_store4("REGVALUE1", "REGVALUE2")
    arr.reg_store("RD", "REGVALUE3")

def amoadd():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    decode.cut("(REGVALUE2+REGVALUE3)", 32, "REGVALUE4")
    arr.mem_store4("REGVALUE1", "REGVALUE4")
    arr.reg_store("RD", "REGVALUE3")

def amoxor():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    c("LET REGVALUE5=REGVALUE3")
    bit.bxor("REGVALUE2", "REGVALUE5", "REGVALUE4", 32)
    arr.mem_store4("REGVALUE1", "REGVALUE4")
    arr.reg_store("RD", "REGVALUE3")

def amoand():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    c("LET REGVALUE5=REGVALUE3")
    bit.band("REGVALUE2", "REGVALUE5", "REGVALUE4", 32)
    arr.mem_store4("REGVALUE1", "REGVALUE4")
    arr.reg_store("RD", "REGVALUE3")

def amoor():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    c("LET REGVALUE5=REGVALUE3")
    bit.bor("REGVALUE2", "REGVALUE5", "REGVALUE4", 32)
    arr.mem_store4("REGVALUE1", "REGVALUE4")
    arr.reg_store("RD", "REGVALUE3")

def amominu():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    c("IF REGVALUE3<REGVALUE2 THEN REGVALUE2=REGVALUE3")
    arr.mem_store4("REGVALUE1", "REGVALUE2")
    arr.reg_store("RD", "REGVALUE3")

def amomaxu():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    c("IF REGVALUE3>REGVALUE2 THEN REGVALUE2=REGVALUE3")
    arr.mem_store4("REGVALUE1", "REGVALUE2")
    arr.reg_store("RD", "REGVALUE3")

def amomin():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    c("LET REGVALUE4=REGVALUE3")
    c("LET REGVALUE5=REGVALUE2")
    decode.to_signed("REGVALUE4")
    decode.to_signed("REGVALUE5")
    c("IF REGVALUE4<REGVALUE5 THEN REGVALUE2=REGVALUE3")
    arr.mem_store4("REGVALUE1", "REGVALUE2")
    arr.reg_store("RD", "REGVALUE3")

def amomax():
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_load4("REGVALUE1", "REGVALUE3")
    c("LET REGVALUE4=REGVALUE3")
    c("LET REGVALUE5=REGVALUE2")
    decode.to_signed("REGVALUE4")
    decode.to_signed("REGVALUE5")
    c("IF REGVALUE4>REGVALUE5 THEN REGVALUE2=REGVALUE3")
    arr.mem_store4("REGVALUE1", "REGVALUE2")
    arr.reg_store("RD", "REGVALUE3")

def lr():
    arr.reg_load("RS1", "REGVALUE1")
    c("LET RESERVATION=REGVALUE1")
    arr.mem_load4("REGVALUE1", "REGVALUE")
    arr.reg_store("RD", "REGVALUE")

def sc():
    arr.reg_load("RS1", "REGVALUE1")
    c("IF REGVALUE1==RESERVATION THEN GOTO LBSCRT")
    arr.reg_store("RD", "1")
    c("GOTO LBSCRE")
    c("LBSCRT:")
    arr.reg_load("RS2", "REGVALUE2")
    arr.mem_store4("REGVALUE1", "REGVALUE2")
    arr.reg_store("RD", "0")
    c("LBSCRE:")

def csrrw():
    arr.csr_load("IMM", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_store("RD", "REGVALUE2")
    arr.csr_store("IMM", "REGVALUE1")

def csrrwi():
    arr.csr_load("IMM", "REGVALUE")
    arr.reg_store("RD", "REGVALUE")
    arr.csr_store("IMM", "RS1")

def csrrs():
    arr.csr_load("IMM", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_store("RD", "REGVALUE2")
    bit.bor("REGVALUE2", "REGVALUE1", "REGVALUE3", 32)
    arr.csr_store("IMM", "REGVALUE3")

def csrrsi():
    arr.csr_load("IMM", "REGVALUE2")
    arr.reg_store("RD", "REGVALUE2")
    bit.bor("REGVALUE2", "RS1", "REGVALUE3", 5, False)
    arr.csr_store("IMM", "REGVALUE3")

def csrrc():
    arr.csr_load("IMM", "REGVALUE2")
    arr.reg_load("RS1", "REGVALUE1")
    arr.reg_store("RD", "REGVALUE2")
    c(f"LET REGVALUE1={(1 << 32) - 1}-REGVALUE1")
    bit.band("REGVALUE2", "REGVALUE1", "REGVALUE3", 32)
    arr.csr_store("IMM", "REGVALUE3")

def csrrci():
    arr.csr_load("IMM", "REGVALUE2")
    arr.reg_store("RD", "REGVALUE2")
    c(f"LET RS1={(1 << 32) - 1}-RS1")
    bit.band("REGVALUE2", "RS1", "REGVALUE3", 32)
    arr.csr_store("IMM", "REGVALUE3")

def print_regs():
    c('PRINT "REGS:"')
    for i in range(32): c(f"PRINT REGN{i}")
    c("LET PC=PC+4")

def r():
    decode.r()
    c("IF FUNCT3==0 THEN GOTO ERLADD")
    c("IF FUNCT3==1 THEN GOTO ERLSLL")
    c("IF FUNCT3==2 THEN GOTO ERLSLT")
    c("IF FUNCT3==3 THEN GOTO ERLSLTU")
    c("IF FUNCT3==4 THEN GOTO ERLXOR")
    c("IF FUNCT3==5 THEN GOTO ERLSRX")
    c("IF FUNCT3==6 THEN GOTO ERLOR")
    c("IF FUNCT3==7 THEN GOTO ERLAND")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("ERLSRX:")
    c("IF FUNCT7>0 THEN GOTO ERLSRA")
    srl()
    c("GOTO ERLEND")
    c("ERLSRA:")
    sra()
    c("GOTO ERLEND")
    c("ERLSLL:")
    sll()
    c("GOTO ERLEND")
    c("ERLSLT:")
    slt()
    c("GOTO ERLEND")
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
    c("IF FUNCT3==1 THEN GOTO EILSLLI")
    c("IF FUNCT3==2 THEN GOTO EILSLTI")
    c("IF FUNCT3==3 THEN GOTO EILSLTIU")
    c("IF FUNCT3==4 THEN GOTO EILXORI")
    c("IF FUNCT3==5 THEN GOTO EILSRXI")
    c("IF FUNCT3==6 THEN GOTO EILORI")
    c("IF FUNCT3==7 THEN GOTO EILANDI")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("EILSRXI:")
    c("IF IMM>31 THEN GOTO EILSRAI")
    srli()
    c("GOTO EILEND")
    c("EILSRAI:")
    c(f"LET IMM=IMM-{1 << 10}")
    srai()
    c("GOTO EILEND")
    c("EILSLLI:")
    slli()
    c("GOTO EILEND")
    c("EILSLTI:")
    slti()
    c("GOTO EILEND")
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

def s():
    decode.s()
    c("IF FUNCT3==0 THEN GOTO ESLSB")
    c("IF FUNCT3==1 THEN GOTO ESLSH")
    c("IF FUNCT3==2 THEN GOTO ESLSW")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("ESLSB:")
    sb()
    c("GOTO ESLEND")
    c("ESLSH:")
    sh()
    c("GOTO ESLEND")
    c("ESLSW:")
    sw()
    c("ESLEND:")
    c("LET PC=PC+4")

def b():
    decode.b()
    c("IF FUNCT3==0 THEN GOTO EBLBEQ")
    c("IF FUNCT3==1 THEN GOTO EBLBNE")
    c("IF FUNCT3==4 THEN GOTO EBLBLT")
    c("IF FUNCT3==5 THEN GOTO EBLBGE")
    c("IF FUNCT3==6 THEN GOTO EBLBLTU")
    c("IF FUNCT3==7 THEN GOTO EBLBGEU")
    c('PRINT "INVALID FUNCT3"')
    c("PRINT FUNCT3")
    c("GOTO THEEND")
    c("EBLBEQ:")
    beq()
    c("GOTO EBLEND")
    c("EBLBNE:")
    bne()
    c("GOTO EBLEND")
    c("EBLBLT:")
    blt()
    c("GOTO EBLEND")
    c("EBLBGE:")
    bge()
    c("GOTO EBLEND")
    c("EBLBGEU:")
    bgeu()
    c("GOTO EBLEND")
    c("EBLBLTU:")
    bltu()
    c("EBLEND:")

def amo():
    decode.r()
    c(f"LET FUNCT5=FUNCT7/4+POINT5+POW2OF52-POW2OF52-1")
    c("IF FUNCT5==0 THEN GOTO EAMOLADD")
    c("IF FUNCT5==2 THEN GOTO EAMOLLR")
    c("IF FUNCT5==3 THEN GOTO EAMOLSC")
    c("IF FUNCT5==1 THEN GOTO EAMOLSWAP")
    c("IF FUNCT5==4 THEN GOTO EAMOLXOR")
    c("IF FUNCT5==8 THEN GOTO EAMOLOR")
    c("IF FUNCT5==12 THEN GOTO EAMOLAND")
    c("IF FUNCT5==16 THEN GOTO EAMOLMIN")
    c("IF FUNCT5==20 THEN GOTO EAMOLMAX")
    c("IF FUNCT5==24 THEN GOTO EAMOLMINU")
    c("IF FUNCT5==28 THEN GOTO EAMOLMAXU")
    c('PRINT "INVALID FUNCT5"')
    c("PRINT FUNCT5")
    c("GOTO THEEND")
    c("EAMOLLR:")
    lr()
    c("GOTO EAMOLEND")
    c("EAMOLSC:")
    sc()
    c("GOTO EAMOLEND")
    c("EAMOLMIN:")
    amomin()
    c("GOTO EAMOLEND")
    c("EAMOLMAX:")
    amomax()
    c("GOTO EAMOLEND")
    c("EAMOLMAXU:")
    amomaxu()
    c("GOTO EAMOLEND")
    c("EAMOLMINU:")
    amominu()
    c("GOTO EAMOLEND")
    c("EAMOLOR:")
    amoor()
    c("GOTO EAMOLEND")
    c("EAMOLAND:")
    amoand()
    c("GOTO EAMOLEND")
    c("EAMOLXOR:")
    amoxor()
    c("GOTO EAMOLEND")
    c("EAMOLADD:")
    amoadd()
    c("GOTO EAMOLEND")
    c("EAMOLSWAP:")
    amoswap()
    c("EAMOLEND:")
    c("LET PC=PC+4")

def z():
    decode.z()
    c("IF FUNCT3==1 THEN GOTO EZLCSRRW")
    c("IF FUNCT3==2 THEN GOTO EZLCSRRS")
    c("IF FUNCT3==3 THEN GOTO EZLCSRRC")
    c("IF FUNCT3==5 THEN GOTO EZLCSRRWI")
    c("IF FUNCT3==6 THEN GOTO EZLCSRRSI")
    c("IF FUNCT3==7 THEN GOTO EZLCSRRCI")
    c('PRINT "INVALID FUNCT3"')
    c("GOTO THEEND")
    c("EZLCSRRCI:")
    csrrci()
    c("GOTO EZLEND")
    c("EZLCSRRC:")
    csrrc()
    c("GOTO EZLEND")
    c("EZLCSRRSI:")
    csrrsi()
    c("GOTO EZLEND")
    c("EZLCSRRS:")
    csrrs()
    c("GOTO EZLEND")
    c("EZLCSRRWI:")
    csrrwi()
    c("GOTO EZLEND")
    c("EZLCSRRW:")
    csrrw()
    c("EZLEND:")
    c("LET PC=PC+4")

def execute():
    arr.mem_load4("PC", "INSTRUCTION")
    decode.start()
    c("IF OPCODE==1 THEN GOTO ELPRINTREGS")
    c("IF OPCODE==3 THEN GOTO ELL")
    c("IF OPCODE==19 THEN GOTO ELI")
    c("IF OPCODE==23 THEN GOTO ELAUIPC")
    c("IF OPCODE==35 THEN GOTO ELS")
    c("IF OPCODE==47 THEN GOTO ELAMO")
    c("IF OPCODE==51 THEN GOTO ELR")
    c("IF OPCODE==55 THEN GOTO ELLUI")
    c("IF OPCODE==99 THEN GOTO ELB")
    c("IF OPCODE==103 THEN GOTO ELJALR")
    c("IF OPCODE==111 THEN GOTO ELJAL")
    c("IF OPCODE==115 THEN GOTO ELZ")
    c('PRINT "INVALID OPCODE"')
    c("PRINT OPCODE")
    c("GOTO THEEND")
    c("ELZ:")
    z()
    c("GOTO ELEND")
    c("ELAMO:")
    amo()
    c("GOTO ELEND")
    c("ELJAL:")
    jal()
    c("GOTO ELEND")
    c("ELJALR:")
    jalr()
    c("GOTO ELEND")
    c("ELB:")
    b()
    c("GOTO ELEND")
    c("ELS:")
    s()
    c("GOTO ELEND")
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
