from compile import c

def round(value, dest):
    c(f"LET {dest}={value}+POW2OF52-POW2OF52")

def floor(value, dest):
    round(value, dest)
    c(f"IF {dest}>{value} THEN {dest}={dest}/2*2-1")

def snip(value, bits, dest):
    c(f"LET CTMPF={value}/{1 << bits}")
    floor(f"CTMPF", "CFLRD")
    c(f"LET {dest}=CFLRD*{1 << bits}")

def cut(value, bits, dest):
    snip(value, bits, "CTMP")
    c(f"LET {dest}={value}/2*2-CTMP/2*2")

def sign_extend(v, len):
    c(f"IF {v}>{(1 << (len - 1)) - 1} THEN {v}={v}+{((1 << 32) - (1 << len))}")

def bv(x, y, z):
    c(f"LET {x}=INSTRUCTION/{1 << y}")
    floor(x, "bv" + x)
    cut("bv" + x, z, x)

def i():
    bv("RD", 7, 5)
    bv("FUNCT3", 12, 3)
    bv("RS1", 15, 5)
    c(f"LET IMMA=INSTRUCTION/{1 << 20}")
    floor("IMMA", "IMM")
    sign_extend("IMM", 12)

def u():
    bv("RD", 7, 5)
    snip("INSTRUCTION", 12, "IMM")

def r():
    bv("RD", 7, 5)
    bv("FUNCT3", 12, 3)
    bv("RS1", 15, 5)
    bv("RS2", 20, 5)
