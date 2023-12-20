from compile import gen_label, c
import sys

MEMSIZE=20480
#MEMSIZE=8 * 1024 * 1024

def init_regs():
    for x in range(1, 32): c(f"LET REGN{x}=0")

def init_csrs():
    c("LET CSRMSCRATCH=0")
    c("LET CSRMTVEC=0")
    c("LET CSRMIE=0")
    c("LET CSRCYCLE=0")
    c("LET CSRMIP=0")
    c("LET CSRMEPC=0")
    c("LET CSRMSTATUS=0")
    c("LET CSRMCAUSE=0")
    c("LET CSRMTVAL=0")

def init_mem():
    if len(sys.argv) == 1: f = "vmlinuz"
    else: f = sys.argv[1]
    if len(sys.argv) <= 2: d = "dtb.bin"
    else: d = sys.argv[2]

    dt = []
    with open(d, "rb") as j:
        for x in j.read(): dt.append(x)

    if len(sys.argv) <= 2 and dt[0x13c // 4] == 0x00c0ff03:
        v = 0x80000000 + MEMSIZE - len(dt)
        dt[0x13c // 4] = v & 0xff
        dt[0x13c // 4 + 1] = (v >> 8) & 0xff
        dt[0x13c // 4 + 2] = (v >> 16) & 0xff
        dt[0x13c // 4 + 3] = (v >> 24) & 0xff

    i = 0
    with open(f, "rb") as f:
        for x in f.read():
            c(f"LET MEMN{i}={x}")
            i += 1
    while i < MEMSIZE - len(dt):
        c(f"LET MEMN{i}=0")
        i += 1
    n = i
    if dt: c(f"LET REGN11={i + 0x80000000}")
    while i < MEMSIZE:
        c(f"LET MEMN{i}={dt[i - n]}")
        i += 1

def address(size, fn, pre, at, ret, s):
    def generate_code(low, high):
        if low == high:
            l1 = gen_label()
            l2 = gen_label()
            c(f"IF {at}=={low} THEN GOTO {l1}")
            c(f"GOTO {l2}")
            c(f"{l1}:")
            fn(low)
            c(f"GOTO {ret}")
            c(f"{l2}:")
        else:
            mid = (low + high) // 2
            c(f"IF {at}<{mid + 1} THEN GOTO {pre}MSL{mid + 1}")
            generate_code(mid + 1, high)
            c(f"{pre}MSL{mid + 1}:")
            generate_code(low, mid)
    generate_code(s, size - 1)

def reg_load_fn():
    c("REGLOAD:")
    address(32, lambda x: c(f"LET REGVALUE=REGN{x}"), "REGLD", "REGADDR", "REGRET", 1)

def reg_store_fn():
    c("REGSTORE:")
    address(32, lambda x: c(f"LET REGN{x}=REGVALUE"), "REGST", "REGADDR", "REGRET", 1)

def mem_load_fn():
    def f(x):
        if x + 3 < MEMSIZE: c(f"LET MEMVALUE=MEMN{x}+MEMN{x + 1}*{1 << 8}+MEMN{x + 2}*{1 << 16}+MEMN{x + 3}*{1 << 24}")
        elif x + 2 < MEMSIZE: c(f"LET MEMVALUE=MEMN{x}+MEMN{x + 1}*{1 << 8}+MEMN{x + 2}*{1 << 16}")
        elif x + 1 < MEMSIZE: c(f"LET MEMVALUE=MEMN{x}+MEMN{x + 1}*{1 << 8}")
        else: c(f"LET MEMVALUE=MEMN{x}")
    c("MEMLOAD:")
    address(MEMSIZE, f, "MEMLD", "MEMADDR", "MEMRET", 0)

def mem_store_fn():
    def f(x):
        c(f"LET MEMN{x}=MEMVALUE1")
        if x + 1 < MEMSIZE: c(f"IF MEMW>1 THEN MEMN{x + 1}=MEMVALUE2")
        if x + 2 < MEMSIZE: c(f"IF MEMW==4 THEN MEMN{x + 2}=MEMVALUE3")
        if x + 3 < MEMSIZE: c(f"IF MEMW==4 THEN MEMN{x + 3}=MEMVALUE4")
    c("MEMSTORE:")
    address(MEMSIZE, f, "MEMST", "MEMADDR", "MEMRET", 0)

def reg_load(num, dest):
    lbl = gen_label()
    c(f"IF {num}==0 THEN GOTO {lbl}")
    lblret = gen_label()
    c(f"LET REGADDR={num}")
    c(f"LET REGRET={lblret}")
    c("GOTO REGLOAD")
    c(f"{lbl}: LET REGVALUE=0")
    c(f"{lblret}: LET {dest}=REGVALUE")

def reg_store(num, value):
    lblret = gen_label()
    c(f"IF {num}==0 THEN GOTO {lblret}")
    c(f"LET REGADDR={num}")
    c(f"LET REGVALUE={value}")
    c(f"LET REGRET={lblret}")
    c("GOTO REGSTORE")
    c(f"{lblret}:")

def mem_load(addr, *x):
    lblret = gen_label()
    c(f"IF {addr}<{0x80000000} THEN GOTO {lblret}")
    c(f"LET MEMADDR={addr}-{0x80000000}")
    c(f"LET MEMRET={lblret}")
    c("GOTO MEMLOAD")
    c(f"{lblret}:")
    for y in x: c(y)

def mem_load4(addr, dest):
    mem_load(addr, f"LET {dest}=MEMVALUE")

def mem_load2(addr, dest):
    mem_load(addr,
             f"LET MEML2T=MEMVALUE/{1 << 16}+POW2OF52-POW2OF52",
             f"IF MEML2T>MEMVALUE/{1 << 16} THEN MEML2T=MEML2T-1",
             f"LET {dest}=MEMVALUE-MEML2T*{1 << 16}")

def mem_load1(addr, dest):
    mem_load(addr,
             f"LET MEML2T=MEMVALUE/{1 << 8}+POW2OF52-POW2OF52",
             f"IF MEML2T>MEMVALUE/{1 << 8} THEN MEML2T=MEML2T-1",
             f"LET {dest}=MEMVALUE-MEML2T*{1 << 8}")

def mem_store(addr, w, *x):
    lblret = gen_label()
    lbl = gen_label()
    c(f"IF {addr}=={0x10000000} THEN GOTO {lbl}")
    c(f"IF {addr}<{0x80000000} THEN GOTO {lblret}")
    c(f"LET MEMADDR={addr}-{0x80000000}")
    c(f"LET MEMRET={lblret}")
    c(f"LET MEMW={w}")
    for y in x: c(y)
    c("GOTO MEMSTORE")
    c(f"{lbl}:")
    c('PRINT "UART"')
    c("PRINT MEMVALUE1")
    c(f"{lblret}:")

# see comment in decode.py

def mem_store1(addr, value):
    mem_store(addr,
              1,
              f"LET MEMS1T={value}/{1 << 8}+POW2OF52-POW2OF52",
              f"IF MEMS1T>{value}/{1 << 8} THEN MEMS1T=MEMS1T-1",
              f"LET MEMVALUE1={value}-MEMS1T*{1 << 8}")

def mem_store2(addr, value):
    mem_store(addr,
              2,
              f"LET MEMS2T={value}/{1 << 8}+POW2OF52-POW2OF52",
              f"IF MEMS2T>{value}/{1 << 8} THEN MEMS2T=MEMS2T-1",
              f"LET MEMVALUE1={value}-MEMS2T*{1 << 8}",
              f"LET MEMS2T2=MEMS2T/{1 << 8}+POW2OF52-POW2OF52",
              f"IF MEMS2T2>MEMS2T/{1 << 8} THEN MEMS2T2=MEMS2T2-1",
              f"LET MEMVALUE2=MEMS2T-MEMS2T2*{1 << 8}")

def mem_store4(addr, value):
    mem_store(addr,
              4,
              f"LET MEMS2T={value}/{1 << 8}+POW2OF52-POW2OF52",
              f"IF MEMS2T>{value}/{1 << 8} THEN MEMS2T=MEMS2T-1",
              f"LET MEMVALUE1={value}-MEMS2T*{1 << 8}",
              f"LET MEMS2T2=MEMS2T/{1 << 8}+POW2OF52-POW2OF52",
              f"IF MEMS2T2>MEMS2T/{1 << 8} THEN MEMS2T2=MEMS2T2-1",
              f"LET MEMVALUE2=MEMS2T-MEMS2T2*{1 << 8}",
              f"LET MEMS2T3=MEMS2T2/{1 << 8}+POW2OF52-POW2OF52",
              f"IF MEMS2T3>MEMS2T2/{1 << 8} THEN MEMS2T3=MEMS2T3-1",
              f"LET MEMVALUE3=MEMS2T2-MEMS2T3*{1 << 8}",
              f"LET MEMS2T4=MEMS2T3/{1 << 8}+POW2OF52-POW2OF52",
              f"IF MEMS2T4>MEMS2T3/{1 << 8} THEN MEMS2T4=MEMS2T4-1",
              f"LET MEMVALUE4=MEMS2T3-MEMS2T4*{1 << 8}")

def csr_load(csr, dest):
    l = gen_label()
    c(f"IF {csr}=={0x340} THEN GOTO {l}CSL340")
    c(f"IF {csr}=={0x305} THEN GOTO {l}CSL305")
    c(f"IF {csr}=={0x304} THEN GOTO {l}CSL304")
    c(f"IF {csr}=={0xc00} THEN GOTO {l}CSLC00")
    c(f"IF {csr}=={0x344} THEN GOTO {l}CSL344")
    c(f"IF {csr}=={0x341} THEN GOTO {l}CSL341")
    c(f"IF {csr}=={0x300} THEN GOTO {l}CSL300")
    c(f"IF {csr}=={0x342} THEN GOTO {l}CSL342")
    c(f"IF {csr}=={0x343} THEN GOTO {l}CSL343")
    c(f"IF {csr}=={0xf11} THEN GOTO {l}CSLF11")
    c(f"IF {csr}=={0x301} THEN GOTO {l}CSL301")
    c(f"LET {dest}=0")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL305: LET {dest}=CSRMTVEC")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL304: LET {dest}=CSRMIE")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSLC00: LET {dest}=CSRCYCLE")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL344: LET {dest}=CSRMIP")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL341: LET {dest}=CSRMEPC")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL300: LET {dest}=CSRMSTATUS")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL342: LET {dest}=CSRMCAUSE")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL343: LET {dest}=CSRMTVAL")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSLF11: LET {dest}={0xff0ff0ff}")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL301: LET {dest}={0x40401101}")
    c(f"GOTO {l}CSLEND")
    c(f"{l}CSL340: LET {dest}=CSRMSCRATCH")
    c(f"{l}CSLEND:")

def csr_store(csr, value):
    l = gen_label()
    c(f"IF {csr}=={0x340} THEN GOTO {l}CSS340")
    c(f"IF {csr}=={0x305} THEN GOTO {l}CSS305")
    c(f"IF {csr}=={0x304} THEN GOTO {l}CSS304")
    c(f"IF {csr}=={0x344} THEN GOTO {l}CSS344")
    c(f"IF {csr}=={0x341} THEN GOTO {l}CSS341")
    c(f"IF {csr}=={0x300} THEN GOTO {l}CSS300")
    c(f"IF {csr}=={0x342} THEN GOTO {l}CSS342")
    c(f"IF {csr}=={0x343} THEN GOTO {l}CSS343")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS305: LET CSRMTVEC={value}")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS304: LET CSRMIE={value}")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS344: LET CSRMIP={value}")
    c(f"LET DAMNYOU=CSRMIP/{1 << 8}+POW2OF52-POW2OF52")
    c(f"IF DAMNYOU>CSRMIP/{1 << 8} THEN DAMNYOU=DAMNYOU-1")
    c(f"IF CSRMIP-DAMNYOU*{1 << 8}>{1 << 7} THEN CSRMIP=CSRMIP-{1 << 7}")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS341: LET CSRMEPC={value}")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS300: LET CSRMSTATUS={value}")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS342: LET CSRMCAUSE={value}")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS343: LET CSRMTVAL={value}")
    c(f"GOTO {l}CSSEND")
    c(f"{l}CSS340: LET CSRMSCRATCH={value}")
    c(f"{l}CSSEND:")
