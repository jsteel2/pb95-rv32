import arr
from compile import c, compile
import execute

def main():
    c(f"LET PC={0x80000000}")
    c("MAINLOOP:")
    execute.execute()
    c("PRINT PC")
    c("GOTO MAINLOOP")

if __name__ == "__main__":
    c('PRINT "INITIALIZING REGISTERS"')
    arr.init_regs()
    c(f"LET POW2OF52={2 ** 52}")
    c("LET POINT5=0.50000000000001")
    c("LET RESERVATION=0")
    c('PRINT "INITIALIZING MEMORY"')
    arr.init_mem()
    c('PRINT "STARTING UP!"')
    main()
    arr.mem_store_fn()
    arr.mem_load_fn()
    arr.reg_store_fn()
    arr.reg_load_fn()
    c("THEEND:")
    for x in range(1, 32): c(f"PRINT REGN{x}")
    c("PRINT PC")
    c('PRINT "THATS ALL FOLKS!"')
    compile()
