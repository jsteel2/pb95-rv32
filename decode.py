from compile import c

def cut(value, bits, dest):
    c(f"LET {dest}={value}-({value}/{1 << bits}+POINT5+POW2OF52-POW2OF52-1)*{1 << bits}")

def sign_extend(v, len):
    c(f"IF {v}>{(1 << (len - 1)) - 1} THEN {v}={v}+{((1 << 32) - (1 << len))}")

def to_signed(v):
    c(f"IF {v}>{(1 << 31) - 1} THEN {v}=-{1 << 32}+{v}")

# feel like we could get rid of DLAST

def start():
    c(f"LET DLAST=(INSTRUCTION/{1 << 7}+POINT5+POW2OF52-POW2OF52-1)*{1 << 7}")
    c(f"LET OPCODE=INSTRUCTION-DLAST")

def i():
    c(f"LET DLAST2=(INSTRUCTION/{1 << 12}+POINT5+POW2OF52-POW2OF52-1)*{1 << 12}")
    c(f"LET RD=(DLAST-DLAST2)/{1 << 7}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 15}+POINT5+POW2OF52-POW2OF52-1)*{1 << 15}")
    c(f"LET FUNCT3=(DLAST2-DLAST)/{1 << 12}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET IMM=INSTRUCTION/{1 << 20}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET RS1=(DLAST-IMM*{1 << 20})/{1 << 15}+POINT5+POW2OF52-POW2OF52-1")
    sign_extend("IMM", 12)

def u():
    c(f"LET IMM=(DLAST/{1 << 12}+POINT5+POW2OF52-POW2OF52-1)*{1 << 12}")
    c(f"LET RD=(DLAST-IMM)/{1 << 7}+POINT5+POW2OF52-POW2OF52-1")

def r():
    c(f"LET DLAST2=(INSTRUCTION/{1 << 12}+POINT5+POW2OF52-POW2OF52-1)*{1 << 12}")
    c(f"LET RD=(DLAST-DLAST2)/{1 << 7}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 15}+POINT5+POW2OF52-POW2OF52-1)*{1 << 15}")
    c(f"LET FUNCT3=(DLAST2-DLAST)/{1 << 12}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST2=(INSTRUCTION/{1 << 20}+POINT5+POW2OF52-POW2OF52-1)*{1 << 20}")
    c(f"LET RS1=(DLAST-DLAST2)/{1 << 15}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET FUNCT7=INSTRUCTION/{1 << 25}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET RS2=(DLAST2-FUNCT7*{1 << 25})/{1 << 20}+POINT5+POW2OF52-POW2OF52-1")

def s():
    c(f"LET DLAST2=(INSTRUCTION/{1 << 12}+POINT5+POW2OF52-POW2OF52-1)*{1 << 12}")
    c(f"LET IMMA=(DLAST-DLAST2)/{1 << 7}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 15}+POINT5+POW2OF52-POW2OF52-1)*{1 << 15}")
    c(f"LET FUNCT3=(DLAST2-DLAST)/{1 << 12}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST2=(INSTRUCTION/{1 << 20}+POINT5+POW2OF52-POW2OF52-1)*{1 << 20}")
    c(f"LET RS1=(DLAST-DLAST2)/{1 << 15}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET IMM=IMMA+INSTRUCTION/{1 << 18}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET RS2=(DLAST2-(IMM-IMMA)*{1 << 18})/{1 << 20}+POINT5+POW2OF52-POW2OF52-1")
    sign_extend("IMM", 12)
