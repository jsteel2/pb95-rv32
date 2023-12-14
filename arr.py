import os
from compile import gen_label, c
import sys

MEMSIZE=20480

def init_regs():
    for x in range(1, 32): c(f"LET REGN{x}=0")

def init_mem():
    if len(sys.argv) == 1:
        os.system("riscv32-unknown-elf-as prog.S")
        os.system("riscv32-unknown-elf-objcopy -O binary a.out a.bin")
        f = "a.bin"
    else:
        f = sys.argv[1]
    i = 0
    with open(f, "rb") as f:
        for x in f.read():
            c(f"LET MEMN{i}={x}")
            i += 1
    while i < MEMSIZE:
        c(f"LET MEMN{i}=0")
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
    c(f"IF {addr}<{0x80000000} THEN GOTO {lblret}")
    c(f"LET MEMADDR={addr}-{0x80000000}")
    c(f"LET MEMRET={lblret}")
    c(f"LET MEMW={w}")
    for y in x: c(y)
    c("GOTO MEMSTORE")
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
