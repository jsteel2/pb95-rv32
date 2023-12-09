from random import randint, choice
from os import system
from subprocess import run, PIPE
from sys import stdin
import argparse

sets = 33
prog = []

def gen_reg():
    return "x" + str(randint(0, 31))

def gen_instruction(rd):
    instrs = {"u": ["auipc", "lui"], "i": ["addi", "ori", "andi", "xori", "sltiu"], "r": ["add", "sub", "or", "and", "xor", "sltu"], "l": ["lb", "lh", "lw", "lbu", "lhu"]}
    type, c = choice(list(instrs.items()))
    instr = choice(c)
    match type:
        case "u": return f"{instr} x{rd}, {randint(0, 1048575)}"
        case "i": return f"{instr} x{rd}, {gen_reg()}, {randint(-2048, 2047)}"
        case "r": return f"{instr} x{rd}, {gen_reg()}, {gen_reg()}"
        case "l": return f"{instr} x{rd}, {randint(-2048, 2047)}(x1)"
    return ""

def gen_prog(filename):
    global prog
    prog = []
    with open(filename + ".S", "w") as f:
        prog.append("")
        f.write("li x1, 0x80000800\n")
        for _ in range(sets):
            for i in range(2, 32):
                instr = gen_instruction(i)
                prog.append(instr)
                f.write(instr + "\n")
            f.write(".word 1\n")
            prog.append("")

def compile(filename):
    system(f"riscv32-unknown-elf-as {filename}.S -o {filename}.elf")
    system(f"riscv32-unknown-elf-objcopy -O binary {filename}.elf {filename}.bin")

def test(filename, pb):
    wrong = []
    a = run(["./mini-rv32ima", "-f", filename + ".bin", "-s", "-c", str(31 * sets)], stdout=PIPE).stdout.decode().strip().split("\n")
    if pb:
        system(f"python3 main.py {filename}.bin > '{pb}'")
        print("paste output:")
        b = stdin.read().strip().split("\n")
    else:
        b = run(["sh", "-c", f"python3 main.py {filename}.bin | python3 pbasic.py | lua"], stdout=PIPE).stdout.decode().strip().split("\n")

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
            if areg != breg: wrong.append((reg, areg, breg, aregs, bregs, prog[i * 31 + reg - 1]))
        del b[bs]

    return wrong

if __name__ == "__main__":
    done = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-gen", action="store_true")
    parser.add_argument("-p", "--pbasic-file")
    args = parser.parse_args()
    while True:
        if not args.no_gen:
            gen_prog("fuzz")
            compile("fuzz")
        else:
            with open("fuzz.S") as f:
                for l in f: prog.append(l[:-1])
        if not args.pbasic_file: wrong = test("fuzz", None)
        else: wrong = test("fuzz", args.pbasic_file)
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
