import os
from compile import gen_label, c
import sys

MEMSIZE=1024

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

def mem_store_fn():
    c("MEMSTORE:")

def mem_load_fn():
    def f(x):
        c(f"LET MEMVALUE1=MEMN{x}")
        if x + 1 < MEMSIZE: c(f"LET MEMVALUE2=MEMN{x + 1}")
        else: c(f"LET MEMVALUE2=0")
        if x + 2 < MEMSIZE: c(f"LET MEMVALUE3=MEMN{x + 2}")
        else: c(f"LET MEMVALUE3=0")
        if x + 3 < MEMSIZE: c(f"LET MEMVALUE4=MEMN{x + 3}")
        else: c(f"LET MEMVALUE4=0")
    c("MEMLOAD:")
    address(MEMSIZE, f, "MEMLD", "MEMADDR", "MEMRET", 0)

def reg_store_fn():
    c("REGSTORE:")
    address(32, lambda x: c(f"LET REGN{x}=REGVALUE"), "REGST", "REGADDR", "REGRET", 1)

def reg_load_fn():
    c("REGLOAD:")
    address(32, lambda x: c(f"LET REGVALUE=REGN{x}"), "REGLD", "REGADDR", "REGRET", 1)

def n_store(pre, addr, value, x=None):
    lbl = gen_label()
    if pre == "MEM": # hacky
        c(f"IF {addr}<{0x80000000} THEN GOTO {lbl}") # print an error or something
        c(f"LET {pre}ADDR={addr}-{0x80000000}")
    else:
        c(f"LET {pre}ADDR={addr}")
    c(f"LET {pre}VALUE={value}")
    c(f"LET {pre}RET={lbl}")
    c(f"GOTO {pre}STORE")
    if x: c(x)
    c(f"{lbl}:")

def n_load(pre, addr, x=None):
    lbl = gen_label()
    if pre == "MEM": # hacky
        c(f"IF {addr}<{0x80000000} THEN GOTO {lbl}") # print an error or something
        c(f"LET {pre}ADDR={addr}-{0x80000000}")
    else:
        c(f"LET {pre}ADDR={addr}")
    c(f"LET {pre}RET={lbl}")
    c(f"GOTO {pre}LOAD")
    if x: c(x)
    c(f"{lbl}:")

def mem_load4(addr, dest):
     n_load("MEM", addr)
     c(f"LET {dest}=MEMVALUE1+MEMVALUE2*{1<<8}+MEMVALUE3*{1<<16}+MEMVALUE4*{1<<24}")

def mem_load2(addr, dest):
    n_load("MEM", addr)
    c(f"LET {dest}=MEMVALUE1+MEMVALUE2*{1<<8}")

def mem_load1(addr, dest):
    n_load("MEM", addr)
    c(f"LET {dest}=MEMVALUE1")

def reg_store(num, value):
    lbl = gen_label()
    c(f"IF {num}==0 THEN GOTO {lbl}")
    n_store("REG", num, value, f"{lbl}:")

def reg_load(num, dest):
    lbl = gen_label()
    c(f"IF {num}==0 THEN GOTO {lbl}")
    n_load("REG", num, f"{lbl}: LET REGVALUE=0")
    c(f"LET {dest}=REGVALUE")

## MEMN69=MEMVALUE1
## IF W>1 THEN MEMN70=MEMVALUE2
## IF W==4 THEN MEMN71=MEMVALUE3
## IF W==4 THEN MEMN72=MEMVALUE4
