local prog = {}
local pc = 1
Vars = {}

local function eval(expr)
    local x = "return " .. expr:gsub("[a-zA-Z]+[a-zA-Z0-9]*", 'Vars["%1"]')
    if _VERSION == 5.1 then return loadstring(x)()
    else return load(x)() end
end

local function set(y)
    local i = 0
    local v = ""
    y = y .. "="
    for x in y:gmatch("(.-)=") do
        if i == 0 then v = x
        else Vars[v] = eval(x) end
        i = i + 1
    end
end

local function interp(l)
    local s = {}
    l = l .. " "
    for w in l:gmatch("(.-) ") do
        s[#s + 1] = w
    end
    if s[2] == "LET" then
        set(s[3])
    elseif s[2] == "PRINT" then
        local q = l:find('"')
        if s[3]:sub(1, 1) == '"' then
            print(l:sub(q + 1, -3))
        else
            print(eval(s[3]))
        end
    elseif s[2] == "GOTO" then
        pc = eval(s[3]) - 1
    elseif s[2] == "IF" then
        if eval(s[3]) then
            if s[5] == "GOTO" then pc = eval(s[6]) - 1
            else set(s[5]) end
        end
    end
    pc = pc + 1
end

for l in io.stdin:read("a"):gmatch("(.-)\n") do
    prog[#prog + 1] = l
end

while prog[pc] do
    interp(prog[pc])
end
