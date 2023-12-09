from compile import c
import decode

def bor(x, y, dest, ylen):
    if ylen != 32:
        c(f"LET {dest}={x}")
        decode.cut(dest, ylen, "BITCU")
        c(f"LET {x}={x}/2*2-CFLRD*{1 << ylen}")
        c(f"IF {y}>{(1 << (ylen - 1)) - 1} THEN {dest}={(1 << 32) - (1 << ylen)}+BITCU")
    else:
        c(f"LET {dest}={x}")
    for i in range(ylen, -1, -1):
        c(f"LET BITHX={x}/{1 << i}")
        decode.floor("BITHX", "BITHXF")
        c(f"LET BITHY={y}/{1 << i}")
        decode.floor("BITHY", "BITHYF")

        c("LET BITR=BITHYF/2*2-BITHXF/2*2")
        c(f"IF BITR==1 THEN {dest}={dest}+{1 << i}")

        c(f"LET {x}={x}/2*2-BITHXF*{1 << i}")
        c(f"LET {y}={y}/2*2-BITHYF*{1 << i}")

def band(x, y, dest, ylen):
    c(f"LET {dest}=0")
    if ylen != 32:
        c(f"LET BITDL={x}/{1 << ylen}")
        decode.floor("BITDL", "BITFL")
        c(f"LET {x}={x}/2*2-BITFL*{1 << ylen}")
        c(f"IF {y}>{(1 << (ylen - 1)) - 1} THEN {dest}=BITFL*{1 << ylen}")
    for i in range(ylen, -1, -1):
        c(f"LET BITHX={x}/{1 << i}")
        decode.floor("BITHX", "BITHXF")
        c(f"LET BITHY={y}/{1 << i}")
        decode.floor("BITHY", "BITHYF")

        c("LET BITR=BITHYF/2*2+BITHXF/2*2")
        c(f"IF BITR==2 THEN {dest}={dest}+{1 << i}")

        c(f"LET {x}={x}/2*2-BITHXF*{1 << i}")
        c(f"LET {y}={y}/2*2-BITHYF*{1 << i}")

def bxor(x, y, dest):
    c(f"LET {dest}=0")
    for i in range(31, -1, -1):
        c(f"LET BITHX={x}/{1 << i}")
        decode.floor("BITHX", "BITHXF")
        c(f"LET BITHY={y}/{1 << i}")
        decode.floor("BITHY", "BITHYF")

        c("LET BITR=BITHYF/2*2+BITHXF/2*2")
        c(f"IF BITR==1 THEN {dest}={dest}+{1 << i}")

        c(f"LET {x}={x}/2*2-BITHXF*{1 << i}")
        c(f"LET {y}={y}/2*2-BITHYF*{1 << i}")
