from compile import c

def cut(value, bits, dest):
    c(f"LET {dest}={value}-({value}/{1 << bits}+POINT5+POW2OF52-POW2OF52-1)*{1 << bits}")

def sign_extend(v, len):
    c(f"IF {v}>{(1 << (len - 1)) - 1} THEN {v}={v}+{((1 << 32) - (1 << len))}")

def to_signed(v):
    c(f"IF {v}>{(1 << 31) - 1} THEN {v}=-{1 << 32}+{v}")

# feel like we could get rid of DLAST
# also figure out why this doesnt work elsewhere like in bit.py or now arr.py, or in b() here now
# also if i figure that out u could do branchless bitwise in a single line, which would be way fastr
# after we get shit running we should mash things up into one line where ever possible for that sweet speed

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
    c(f"LET IMMB=INSTRUCTION/{1 << 25}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET RS2=(DLAST2-IMMB*{1 << 25})/{1 << 20}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET IMM=IMMA+IMMB*{1 << 5}")
    sign_extend("IMM", 12)

def b():
    c(f"LET DLAST2=(INSTRUCTION/{1 << 8}+POINT5+POW2OF52-POW2OF52-1)*{1 << 8}")
    c(f"LET IMMA=(DLAST-DLAST2)*{1 << 4}")
    c(f"LET DLAST=(INSTRUCTION/{1 << 12}+POINT5+POW2OF52-POW2OF52-1)*{1 << 12}")
    c(f"LET IMMB=(DLAST2-DLAST)/{1 << 7}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST2=(INSTRUCTION/{1 << 15}+POINT5+POW2OF52-POW2OF52-1)*{1 << 15}")
    c(f"LET FUNCT3=(DLAST-DLAST2)/{1 << 12}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 20}+POINT5+POW2OF52-POW2OF52-1)*{1 << 20}")
    c(f"LET RS1=(DLAST2-DLAST)/{1 << 15}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST2=(INSTRUCTION/{1 << 25}+POINT5+POW2OF52-POW2OF52-1)*{1 << 25}")
    c(f"LET RS2=(DLAST-DLAST2)/{1 << 20}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 31}+POINT5+POW2OF52-POW2OF52-1)*{1 << 31}")
    c(f"LET IMMC=(DLAST2-DLAST)/{1 << 20}+POW2OF52-POW2OF52")
    c(f"IF IMMC>(DLAST2-DLAST)/{1 << 20} THEN IMMC=IMMC-1")
    c(f"LET IMMD=DLAST/{1 << 19}+POW2OF52-POW2OF52")
    c(f"IF IMMD>DLAST/{1 << 19} THEN IMMD=IMMD-1")
    c(f"LET IMM=IMMA+IMMB+IMMC+IMMD")
    sign_extend("IMM", 13)

def j():
    c(f"LET DLAST2=(INSTRUCTION/{1 << 12}+POINT5+POW2OF52-POW2OF52-1)*{1 << 12}")
    c(f"LET RD=(DLAST-DLAST2)/{1 << 7}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 20}+POINT5+POW2OF52-POW2OF52-1)*{1 << 20}")
    c(f"LET IMMA=DLAST2-DLAST")
    c(f"LET DLAST2=(INSTRUCTION/{1 << 21}+POINT5+POW2OF52-POW2OF52-1)*{1 << 21}")
    c(f"LET IMMB=(DLAST-DLAST2)/{1 << 9}+POW2OF52-POW2OF52")
    c(f"IF IMMB>(DLAST-DLAST2)/{1 << 9} THEN IMMB=IMMB-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 31}+POINT5+POW2OF52-POW2OF52-1)*{1 << 31}")
    c(f"LET IMMC=(DLAST2-DLAST)/{1 << 20}+POW2OF52-POW2OF52")
    c(f"IF IMMC>(DLAST2-DLAST)/{1 << 20} THEN IMMC=IMMC-1")
    c(f"LET IMMD=DLAST/{1 << 11}+POW2OF52-POW2OF52")
    c(f"IF IMMD>DLAST/{1 << 11} THEN IMMD=IMMD-1")
    c(f"LET IMM=IMMA+IMMB+IMMC+IMMD")
    sign_extend("IMM", 21)

def z():
    c(f"LET DLAST2=(INSTRUCTION/{1 << 12}+POINT5+POW2OF52-POW2OF52-1)*{1 << 12}")
    c(f"LET RD=(DLAST-DLAST2)/{1 << 7}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET DLAST=(INSTRUCTION/{1 << 15}+POINT5+POW2OF52-POW2OF52-1)*{1 << 15}")
    c(f"LET FUNCT3=(DLAST2-DLAST)/{1 << 12}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET IMM=INSTRUCTION/{1 << 20}+POINT5+POW2OF52-POW2OF52-1")
    c(f"LET RS1=(DLAST-IMM*{1 << 20})/{1 << 15}+POINT5+POW2OF52-POW2OF52-1")
