from random import randint, choice
from os import system
from subprocess import run, PIPE
from sys import stdin
import argparse

sets = 70
interp = "python3 pbasic.py | lua"

instrs = {"u": {"auipc", "lui"}, "i": {"addi", "ori", "andi", "xori", "sltiu", "slti"}, "r": {"add", "sub", "or", "and", "xor", "sltu", "slt", "sll", "srl", "sra"}, "l": {"lb", "lbu", "lh", "lhu", "lw"}, "sh": {"slli", "srli", "srai"}, "amo": {"amoswap.w", "amoadd.w", "amoxor.w", "amoand.w", "amoor.w", "amominu.w", "amomaxu.w", "amomin.w", "amomax.w", "sc.w"}, "lr": {"lr.w"}}

def gen_reg():
    return "x" + str(randint(0, 31))

def gen_instruction(rd):
    instr = choice([x for y in instrs.values() for x in y])
    type = next(k for k, v in instrs.items() if instr in v)
    match type:
        case "u": return [f"{instr} x{rd}, {randint(0, 1048575)}"]
        case "i": return [f"{instr} x{rd}, {gen_reg()}, {randint(-2048, 2047)}"]
        case "sh": return [f"{instr} x{rd}, {gen_reg()}, {randint(0, 31)}"]
        case "r": return [f"{instr} x{rd}, {gen_reg()}, {gen_reg()}"]
        case "amo": return [f"{instr} x{rd}, {gen_reg()}, (x1)"]
        case "lr": return [f"{instr} x{rd}, (x1)"]
        case "l":
            off = randint(-2048, 2047)
            return [f"{instr.replace('l', 's')[:2]} {gen_reg()}, {off}(x1)", f"{instr} x{rd}, {off}(x1)"]
    return []

def gen_prog():
    prog = [""]
    reg_map = {}
    for s in range(sets):
        for i in range(2, 32):
            instr = gen_instruction(i)
            reg_map[(s, i)] = instr
            prog.extend(instr)
        prog.append(".word 1")
    prog[0] = f"li x1, {0x80000000+4*len(prog)+2052}"
    return prog, reg_map

def compile(prog, filename):
    with open(filename + ".S", "w") as f:
        for p in prog: f.write(p + "\n")
    system(f"riscv32-unknown-elf-as {filename}.S -o {filename}.elf")
    system(f"riscv32-unknown-elf-objcopy -O binary {filename}.elf {filename}.bin")

def test(prog, reg_map, filename, pb):
    wrong = []
    a = run(["./mini-rv32ima", "-b", "disable", "-f", filename + ".bin", "-s", "-c", str(len(prog))], stdout=PIPE).stdout.decode().strip().split("\n")
    if pb:
        system(f"python3 main.py {filename}.bin > '{pb}'")
        print("paste output:")
        b = stdin.read().strip().split("\n")
    else:
        b = run(["sh", "-c", f"python3 main.py {filename}.bin | {interp}"], stdout=PIPE).stdout.decode().strip().split("\n")

    for i, regs in enumerate(a):
        s = regs.split()
        bs = b.index("REGS:")
        aregs = []
        bregs = []
        for reg in range(2, 32):
            areg = int(s[reg + 3].split(":")[1], 16)
            aregs.append(areg)
            breg = int(b[bs + reg + 1].split(".")[0])
            bregs.append(breg)
            if areg != breg: wrong.append((reg, areg, breg, aregs, bregs, reg_map[(i, reg)]))
        del b[bs]

    return wrong

if __name__ == "__main__":
    done = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-gen", action="store_true")
    parser.add_argument("-l", "--lua-interpreter", action="store_true")
    parser.add_argument("-p", "--pbasic-file")
    args = parser.parse_args()
    if args.lua_interpreter: interp = "lua pbasic.lua"
    while True:
        if not args.no_gen:
            prog, reg_map = gen_prog()
            compile(prog, "fuzz")
        else:
            prog = []
            reg_map = {}
            s = 0
            with open("fuzz.S") as f:
                for l in f:
                    instr = l[:-1]
                    prog.append(instr)
                    i = instr.split()
                    if i[0] == ".word":
                        s += 1
                    elif not (i[0].replace("s", "l") in instrs["l"] and i[0] not in instrs["l"]):
                        reg_map[(s, int(i[1][1:-1]))] = instr
        if not args.pbasic_file: wrong = test(prog, reg_map, "fuzz", None)
        else: wrong = test(prog, reg_map, "fuzz", args.pbasic_file)
        if wrong:
            for i, w in enumerate(wrong):
                print(f"Register {w[0]}: (OURS) {w[2]} != {w[1]} (RV32IMA)")
                print(f"Line: {w[5]}")
                print("RV32IMA Registers:")
                for x, r in enumerate(w[3]):
                    x += 2
                    if x > 9: print(f" x{x}: {r}")
                    else: print(f"  x{x}: {r}")
                print("\nOur Registers:")
                for x, r in enumerate(w[4]):
                    x += 2
                    if x > 9: print(f" x{x}: {r}")
                    else: print(f"  x{x}: {r}")
                if i != len(wrong) - 1: print("\n")
            break
        done += sets * 30
        print(f"fuzzed {done} instructions")
        if args.no_gen: break
