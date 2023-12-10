from compile import c

def bor(x, y, dest, ylen):
    if ylen != 32:
        c(f"LET {dest}={x}")
        c(f"LET DAMNYOU={x}/{1 << ylen}+POW2OF52-POW2OF52")
        c(f"IF DAMNYOU>{x}/{1 << ylen} THEN DAMNYOU=DAMNYOU-1")
        c(f"IF {y}>{(1 << (ylen - 1)) - 1} THEN {dest}={(1 << 32) - (1 << ylen)}+{x}-DAMNYOU*{1 << ylen}")
    else:
        c(f"LET {dest}={x}")
    for i in range(ylen):
        c(f"IF {y}>(({y}+0.5)/2-0.5+POW2OF52-POW2OF52)*2 THEN {dest}={dest}+{1 << i}-({x}-(({x}+0.5)/2-0.5+POW2OF52-POW2OF52)*2)*{1 << i}")
        c(f"LET {y}=({y}+0.5)/2-0.5+POW2OF52-POW2OF52")
        c(f"LET {x}=({x}+0.5)/2-0.5+POW2OF52-POW2OF52")

def band(x, y, dest, ylen):
    c(f"LET {dest}=0")
    if ylen != 32:
        c(f"LET DAMNYOU={x}/{1 << ylen}+POW2OF52-POW2OF52")
        c(f"IF DAMNYOU>{x}/{1 << ylen} THEN DAMNYOU=DAMNYOU-1")
        c(f"IF {y}>{(1 << (ylen - 1)) - 1} THEN {dest}=DAMNYOU*{1 << ylen}")
    for i in range(ylen):
        c(f"IF ({y}-(({y}+0.5)/2-0.5+POW2OF52-POW2OF52)*2)+({x}-(({x}+0.5)/2-0.5+POW2OF52-POW2OF52)*2)==2 THEN {dest}={dest}+{1 << i}")
        c(f"LET {y}=({y}+0.5)/2-0.5+POW2OF52-POW2OF52")
        c(f"LET {x}=({x}+0.5)/2-0.5+POW2OF52-POW2OF52")

def bxor(x, y, dest, ylen):
    if ylen != 32:
        c(f"LET DAMNYOU={x}/{1 << ylen}+POW2OF52-POW2OF52")
        c(f"IF DAMNYOU>{x}/{1 << ylen} THEN DAMNYOU=DAMNYOU-1")
        c(f"LET {dest}=DAMNYOU*{1 << ylen}")
        c(f"IF {y}>{(1 << (ylen - 1)) - 1} THEN {dest}={(1 << 32) - (1 << ylen)}-DAMNYOU*{1 << ylen}")
    else:
        c(f"LET {dest}=0")
    for i in range(ylen):
        c(f"IF ({y}-(({y}+0.5)/2-0.5+POW2OF52-POW2OF52)*2)+({x}-(({x}+0.5)/2-0.5+POW2OF52-POW2OF52)*2)==1 THEN {dest}={dest}+{1 << i}")
        c(f"LET {y}=({y}+0.5)/2-0.5+POW2OF52-POW2OF52")
        c(f"LET {x}=({x}+0.5)/2-0.5+POW2OF52-POW2OF52")
