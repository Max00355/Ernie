import data
import errors as error
import lexer
import os
import re
import socket

def check_equal(stuff, code, on):
    if stuff[2] != "=":
        error.syntax(code[on], on)

def execute(code):
    length = len(code)-1
    on = 0
    allstrings = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    while on != length:
        stuff = code[on].split()
        
        if stuff[0] == "say":
            print typecheck(' '.join(stuff[1:])).replace("$n", "\n").replace("$t", "\t").replace("$r", "\r")
        
        elif stuff[0] == "socket":
            check_equal(stuff, code, on)
            stuff[3] = typecheck(stuff[3])
            if stuff[3] == "tcp":
                data.variables[stuff[1]] = socket.socket()
            else:
                data.variables[stuff[1]] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        elif stuff[0] == "bind":
            check_equal(stuff, code, on)
            var = typecheck(stuff[1])
            data_ = ''.join(stuff[3:]).split(",")
            host = typecheck(data_[0])
            port = typecheck(data_[1])
            data_ = (host, port)
            var.bind(data_)
            var.listen(5)

        elif stuff[0] == "accept":
            check_equal(stuff, code, on)
            obj, b = data.variables[stuff[3]].accept()
            data.variables[stuff[1]] = obj

        elif stuff[0] == "send":
            check_equal(stuff, code, on)
            stuff[3] = typecheck(' '.join(stuff[3:]))
            data.variables[stuff[1]].send(stuff[3].replace("$n", "\n").replace("$t", "\t").replace("$r", "\r"))
    
        elif stuff[0] == "recv":
            check_equal(stuff, code, on)
            var1 = stuff[1]
            data_ = ''.join(stuff[3:]).split(",")
            var = data_[0]
            buff = typecheck(data_[1])
            data.variables[var1] = data.variables[var].recv(buff)

        elif stuff[0] == "connect":
            check_equal(stuff, code, on)
            var = typecheck(stuff[1])
            data_ = ''.join(stuff[3:]).split(",")
            host = typecheck(data_[0])
            port = typecheck(data_[1])
            data_ = (host, port)
            var.connect(data_)

        elif stuff[0] == "open":
            if stuff[2] != "=":
                error.syntax(code[on], on)
            s = ' '.join(stuff[3:]).split(",")
            print s
            data.variables[stuff[1]] = open(typecheck(s[0]), s[1])
        
        elif stuff[0] == "read":
            if stuff[2] != "=":
                error.syntax(code[on], on)
            data.variables[stuff[1]] = data.variables[stuff[3]].read()
        
        elif stuff[0] == "write":
            if stuff[2] != "=":
                error.syntax(code[on], on)
            data.variables[stuff[1]].write(typecheck(' '.join(stuff[3:])))
        
        elif stuff[0] == "close":
            data.variables[stuff[1]].close()

        elif stuff[0] == "set":
            if stuff[2] != "=":
                error.syntax(code[on], on)
            data.variables[stuff[1]] = typecheck(' '.join(stuff[3:]))
        elif stuff[0] == "use":
            if not os.path.exists(stuff[1]):
                error.nofile(code[on], on)
            else:
                with open(stuff[1], 'rb') as file:
                    lexer.lex(file.read())
        
        elif stuff[0] == "swap":
            d = data.variables[stuff[1]]
            if isinstance(d, int):
                try:
                    data.variables[stuff[1]] = int(d)
                except ValueError:
                    error.typeerror(code[on], on)
            else:
                data.variables[data[1]] = str(d)
        elif stuff[0] == "call":
            stuff[1] = typecheck(stuff[1])
            if stuff[1] not in data.funcs:
                error.invalidcall(code[on], on)
            else:
                st = data.funcs[stuff[1]]
                lexer.lex('\n'.join(st))
        elif stuff[0] == "math":
            st = stuff[3:]
            out = []
            for x in st:
                if x[0] in allstrings:
                    d = str(typecheck(x))
                    out.append(d)
                else:
                    out.append(x)
            data.variables[stuff[1]] = eval(''.join(out))
        
        
        elif stuff[0] == "if":
            stuff[1] = typecheck(stuff[1])
            stuff[3] = typecheck(stuff[3])
            if data.ops[stuff[2]](stuff[1], stuff[3]):
                code_ = '\n'.join(data.funcs[stuff[4]])
                lexer.lex(code_)
            
        
        elif stuff[0] == "while":
            var1 = stuff[1]
            var2 = stuff[3]
            while True:
                stuff[1] = typecheck(var1)
                stuff[3] = typecheck(var2)
                if data.ops[stuff[2]](stuff[1], stuff[3]):
                    co = '\n'.join(data.funcs[stuff[4]])
                    lexer.lex(co)
                else:
                    break
        elif stuff[0] == "add":
            data.variables[stuff[2]].append(typecheck(stuff[1]))

        elif stuff[0] == "input_str":
            if stuff[2] != "=":
                error.syntax(code[on], on)
            else:
                var = stuff[1]
                string = typecheck(' '.join(stuff[3:]))
                d = raw_input(string)
                data.variables[var] = d
        
        elif stuff[0] == "input_int":
            if stuff[2] != "=":
                error.syntax(code[on], on)
            
            else:
                var = stuff[1]
                stri = typecheck(' '.join(stuff[3:]))
                dat = input(stri)
                data.variables[var] = dat

        elif stuff[0] == "find":
            if stuff[2] != "=":
                error.syntax(code[on], on)

            else:
                var = stuff[1]
                data_ = ''.join(stuff[3:]).split(",")
                stri = typecheck(data_[0])
                check = typecheck(data_[1])
                if check.find(stri) != -1:
                    out = "True"
                else:
                    out = "False"

                data.variables[var] = out
        elif stuff[0] == "remove":
            check = ''.join(stuff[3:]).split(",")
            check_equal(stuff, code, on)
            from_ = typecheck(check[0])
            remove = typecheck(check[1])
            data.variables[stuff[1]] = remove.replace(from_, '')

        elif stuff[0] == "split":
            check = typecheck(' '.join(stuff[3:]))
            if stuff[2] != "=":
                error.syntaxerror(code[on], on)
            else:
                data.variables[stuff[1]] = check.split()
        elif stuff[0] == "list":
            check = ' '.join(stuff[3:])
            if not check.startswith("[") and not check.endswith("]"):
                error.syntax(code[on], on)
            else:
                if stuff[2] != "=":
                    error.syntaxerror(code[on], on)
                else:
                    data.variables[stuff[1]] = eval(check)
        
        elif stuff[0] == "length":
            if stuff[2] != "=":
                error.syntax(code[on], on)
            else:
                var = stuff[1]
                data.variables[var] = len(typecheck(' '.join(stuff[3:])))

        on += 1
def typecheck(code):
    try:
        return int(code)
    except ValueError:
        if code.startswith('"'):
            code = code[0:].strip()
            try:
                return re.findall('"(.*?)"', code)[0]
            except IndexError:
                return re.findall('"(.*?)', code)[0]
         
        elif "[" in code:
            code = code.split("[")
            if code[0] not in data.variables:
                error.undefined(str(code))
            else:
                num = code[1].strip("]")
                try:
                    num = int(num)
                except ValueError:
                    error.typeerror(code, 0)
                else:
                    return data.variable[code[0]][num]
        else:
            if code in data.variables:
                return data.variables[code]
            else:
                error.undefined(code)

