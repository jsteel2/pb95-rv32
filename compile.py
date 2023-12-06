import re

def increment_string(s):
    if not s: return "a"
    last_char = s[-1]
    if last_char == '9':
        return increment_string(s[:-1]) + 'a'
    elif last_char == 'Z':
        if len(s) == 1:
            return increment_string(s[:-1]) + 'a'
        else:
            return s[:-1] + '0'
    elif last_char == 'z':
        return s[:-1] + 'A'
    else:
        return s[:-1] + chr(ord(last_char) + 1)

lbl = 0
def gen_label():
    global lbl
    lbl += 1
    return f"CMPLBL{lbl}"

cur_var = ""
a = []
labels = {}
variables = {}
i = 1
def c(x):
    global a, cur_var, labels, variables, i
    if m := re.match(r"^([A-Za-z]+[A-Za-z0-9]*):(.*)", x):
        if m.group(1) not in labels: labels[m.group(1)] = str(i)
        x = m.group(2).strip()

    if m := re.search(r"([A-Za-z]+[A-Za-z0-9]*)=", x):
        cur_var = increment_string(cur_var)
        if m.group(1) not in variables: variables[m.group(1)] = cur_var

    if m := re.match(r"LET ([A-Za-z]+[A-Za-z0-9]*)=(.*)", x):
        if m.group(1) == m.group(2): return

    if x:
        a.append(x)
        i += 1

def compile():
    def replace(x):
        global labels, variables
        try:
            return labels[x.group(1)]
        except KeyError:
            try: return variables[x.group(1)]
            except KeyError: return x.group(1)

    i = 1
    for x in a:
        x = re.sub(r"([A-Za-z]+[A-Za-z0-9]*)(?=[^\"]*(?:\"[^\"]*\"[^\"]*)*$)", replace, x)
        print(str(i) + " " + x)
        i += 1
