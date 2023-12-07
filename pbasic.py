import sys
import re

i = 1

print("_table={}")
print("_pc=1")

while line := sys.stdin.readline()[:-1]:
    print(f"_table[{i}]=function()")
    l = re.sub(r"([a-z]+[a-zA-Z0-9]*)", lambda x: "VAR_" + x.group(1), line).split()
    match l[1]:
        case "LET": print(l[2])
        case "PRINT": print(f"print({' '.join(l[2:])})")
        case "GOTO": print(f"_pc = {l[2]}")
        case "IF":
            print(f"if {l[2]} then")
            if l[4] == "GOTO": print(f"_pc = {l[5]}")
            else: print(l[4])
            print("end")
    print("end")
    i += 1

print("while _table[_pc] do")
print("_opc = _pc")
print("_table[_pc]()")
print("if _opc == _pc then _pc = _pc + 1")
print("end")
print("end")
