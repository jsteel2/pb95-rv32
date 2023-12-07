import random
import os
from subprocess import run, PIPE

ballz = [""]*32

def gen_reg():
    return "x" + str(random.randint(0, 31))

def gen_instruction(rd):
    instrs = {"u": ["auipc", "lui"], "i": ["addi", "ori", "andi", "xori", "sltiu"], "r": ["add", "sub", "or", "and", "xor", "sltu"]}
    type, c = random.choice(list(instrs.items()))
    instr = random.choice(c)
    match type:
        case "u": return f"{instr} {rd}, {random.randint(0, 1048575)}"
        case "i": return f"{instr} {rd}, {gen_reg()}, {random.randint(-2048, 2047)}"
        case "r": return f"{instr} {rd}, {gen_reg()}, {gen_reg()}"
    return ""

def gen_prog(filename):
    with open(filename + ".S", "w") as f:
        for _i in range(1, 32):
            r = "x" + str(_i)
            i = gen_instruction(r) + "\n"
            ballz[_i] = i[:-1]
            f.write(i)
        f.write("ebreak\n")

def compile(i):
    os.system(f"riscv32-unknown-elf-as {i}.S -o {i}.elf")
    os.system(f"riscv32-unknown-elf-objcopy -O binary {i}.elf {i}.bin")

if __name__ == "__main__":
    arrhar = 0
    while True:
        gen_prog("fuzz")
        compile("fuzz")
        a = run(["./mini-rv32ima", "-f", "fuzz.bin", "-c", "30"], stdout=PIPE).stdout.decode().split()
        b = run(["sh", "-c", "python3 main.py fuzz.bin | python3 pbasic.py | lua"], stdout=PIPE).stdout.decode().split("\n")
        die = False
        for i in range(0, 31 * 4, 4):
            ab = "a"
            ab = int(a[int(i / 4) + 4].split(":")[1], 16)
            bb = int(b[-33 + int((i / 4)-1)].split(".", 1)[0])
            if ab != bb:
                print(f"Register {int(i/4)+1} ({ballz[int(i/4)+1]}):\n  RV32IMA: {ab}\n     OURS: {bb}")
                die = True
        if die:
            print("Program:")
            for i in range(1, 32): print("  " + ballz[i])
            print("Registers (RV32IMA):")
            for i in range(1, 32): print(f"  x{i}: " + str(int(a[i + 3].split(":")[1], 16)))
            print("Registers (OURS):")
            for i in range(1, 32): print(f"  x{i}: " + b[-35 + i].split(".", 1)[0])
            break
        arrhar += 30
        print(f"fuzzed {arrhar} instructions")
