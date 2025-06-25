import sys
# ast구조를 담을 노드
class node:
    def __init__(self, nodetype, step, name="", childnode=None, parent=None):
        self.nodetype = nodetype
        self.level = step 
        self.name = name
        self.childnode = childnode or []
        self.parent = parent
        
    #step을 부모노드의 step+1이 되도록 설정
    @property
    def step(self):
        if self.parent:
            return self.parent.step + 1
        return self.level
    #그 외의 step을 설정할 일이 있을때
    @step.setter
    def step(self, value):
        self.level = value
    #실제 ast 구조를 보여주는 부분
    def show(self):
        str = "{}{}:".format(("  " * self.step), self.nodetype)
        if self.nodetype == "Decl":
            str += " {}, [], [], [], []\n".format(self.name)
        elif self.nodetype == "TypeDecl":
            str += " {}, [], None\n".format(self.name)
        elif self.nodetype == "IdentifierType":
            str += " [\'{}\']\n".format(self.name)
        elif self.nodetype == "Constant" or "ID" or "BinaryOp":
            str += " {}\n".format(self.name)
        else:
            str += "\n"
        for node in self.childnode:
            str += node.show()
        return str
#정수인지 실수인지 판단하는 함수
def is_digit(data):
    try:
        int(data)
        return "int"
    except ValueError:
        try:
            float(data)
            return "double"
        except ValueError:
            return "string"
#int a = ? -> ?(등호 우변의 식)에 해당하는 부분을 읽어 operate하는 함수
def operation(data, arglevel, start, endsymbol,recursion):
    priority = { "*": 1, "/": 1, "%": 1, "+": 2, "-": 2, "<<": 3, ">>": 3, "&": 4, "^": 5, "|": 6} # 값이 낮을 수록 우선순위가 높다.
    opsymbol = ["+","-","*","/","%","^","|","&","<<",">>"]
    i = start
    nodelist = []
    oplist = [] # 앞에서부터 하나씩 읽으며 연산자, 인덱스, 그에 따른 우선순위를 전부 저장하는 딕셔너리 리스트
    ops = [] # 등호 우변의 식에 존재하는 연산자, 인덱스, 그에 따른 우선순위를 전부 저장한 딕셔너리 리스트 단, 괄호로 둘러싸인 부분 제외
    rec = recursion
    opcount = 0 # 연산자의 갯수
    bracket = 0 # 괄호의 갯수
    # 여는 괄호와 닫는 괄호의 갯수가 맞을때만 ops저장
    for k in range(start,len(data)):
        if rec>=1:
            if data[k]==")":
                break
        if data[k]=="(":
            bracket+=1
            continue
        if data[k]==")":
            bracket-=1
            continue
        if bracket==0:
            if data[k] in opsymbol:
                ops.append({"op": data[k], "index": k, "priority": priority.get(data[k])})
                opcount+=1
        if data[k]==";":
            break
        
    level=arglevel
    
    # ";" 를 만나기전까지 돌며 연산자, 변수, 상수, 함수일 때의 연산처리
    while i < len(data):
        if data[i] in endsymbol:
            break
        if data[i] == "(":
            recur_op = operation(data, level+1, i+1, [")"], rec+1)
            i = recur_op["index"]+1
            nodelist.append(recur_op["node"])
        elif data[i] in opsymbol:
            # 연산자가 하나라도 존재하고 현재 연산자가 직전에 추가한 연산자보다 우선순위가 낮거나 같을때만 반복 
            # 직전에 추가한 연산자 pop을 하여 계산하는과정
            while len(oplist) > 0 and priority.get(oplist[-1]['op']) <= priority.get(data[i]):
                # 직전에 추가한 연산자보다 우선순위가 높은 연산자가 뒤에 있는지 체크 -> 없다면 연산
                if not any(v["priority"] < priority.get(oplist[-1]['op']) for v in ops): 
                    op = oplist.pop()['op']
                    opcount-=1
                    level=arglevel+opcount
                    binaryop = node("BinaryOp", step=level, name=op)
                    binaryop.step = level
                    right = nodelist.pop()
                    left = nodelist.pop()
                    if right.nodetype == "FuncCall":
                        right.childnode[0].parent = right
                        if len(right.childnode) > 1:
                            right.childnode[1].parent= right
                            for j in range(len(right.childnode[1].childnode)):
                                right.childnode[1].childnode[j].parent = right.childnode[1]
                    if left.nodetype == "FuncCall":
                        left.childnode[0].parent = left
                        if len(left.childnode) > 1:
                            left.childnode[1].parent = left
                            for j in range(len(left.childnode[1].childnode)):
                                left.childnode[1].childnode[j].parent = left.childnode[1]
                    right.parent = binaryop
                    left.parent = binaryop
                    binaryop.childnode.append(left)
                    binaryop.childnode.append(right)
                    nodelist.append(binaryop)
                else:
                    break
            # oplist에 아무것도 없거나 우선순위가 높다면 그냥 추가
            oplist.append({"op": data[i], "index": i, "priority": priority.get(data[i])})
            i += 1
        elif i+1 < len(data) and data[i+1] == "(": # 함수에 대한 처리
            funcname = data[i]
            temp = i
            if i+6 < len(data):
                if data[temp+2] ==")":
                    if data[temp+1] in opsymbol or len(opsymbol) > 0:
                        level = level+1
                elif data[temp+3]==")":
                    if data[temp+1] in opsymbol or len(opsymbol) > 0:
                        level = level+1
                elif data[temp+5]==")":
                    if data[temp+1] in opsymbol or len(opsymbol) > 0:
                        level = level+1
            funccall = node("FuncCall", step=level)
            funcid = node("ID", step=level+1, name=funcname)
            funcid.parent = funccall
            funccall.childnode.append(funcid)
            i += 2
            check = 0
            if data[i] != ")":
                exprlist = node("ExprList", step=level+1)
                exprlist.parent = funccall
                check = 1
            while data[i] != ")":
                if data[i] == ",":
                    i += 1
                    continue
                if is_digit(data[i])=="int":
                    consta = node("Constant", step=level+2, name="int, "+data[i])
                    exprlist.childnode.append(consta)
                    consta.parent = exprlist
                elif is_digit(data[i])=="double":
                    consta = node("Constant", step=level+2, name="double, "+data[i])
                    exprlist.childnode.append(consta)
                    consta.parent = exprlist
                else:
                    Idv = node("ID", step=level+2, name=data[i])
                    exprlist.childnode.append(Idv)
                    Idv.parent = exprlist
                i += 1
            if check:
                funccall.childnode.append(exprlist)
            nodelist.append(funccall)
            level-=1
            i += 1
        else: # 일반 변수나 상수에 대한 처리
            if i+1 < len(data):
                if data[i] == ",":
                    i += 1
                    continue
                if data[i+1] in opsymbol or len(oplist)>0:
                    if data[i] == ",":
                        i += 1
                        continue
                    if is_digit(data[i])=="int":
                        nodelist.append(node("Constant", step=level+1, name="int, "+data[i]))
                    elif is_digit(data[i])=="double":
                        nodelist.append(node("Constant", step=level+1, name="double, "+data[i]))
                    else:
                        nodelist.append(node("ID", step=level+1, name=data[i]))
                else:
                    if is_digit(data[i])=="int":
                        nodelist.append(node("Constant", step=level, name="int, "+data[i]))
                    elif is_digit(data[i])=="double":
                        nodelist.append(node("Constant", step=level, name="double, "+data[i]))
                    else:
                        nodelist.append(node("ID", step=level, name=data[i]))
                i += 1
    while len(oplist) > 0: # 남은 연산자가 존재할때 처리
        op = oplist.pop()['op']
        opcount-=1
        level=arglevel+opcount
        binaryop = node("BinaryOp", step=level, name=op)
        binaryop.step = level
        right = nodelist.pop()
        left = nodelist.pop()
        if right.nodetype == "FuncCall":
            right.childnode[0].parent = right
            if len(right.childnode) > 1:
                right.childnode[1].parent= right
                for j in range(len(right.childnode[1].childnode)):
                    right.childnode[1].childnode[j].parent = right.childnode[1]
        if left.nodetype == "FuncCall":
            left.childnode[0].parent = left
            if len(left.childnode) > 1:
                left.childnode[1].parent = left
                for j in range(len(left.childnode[1].childnode)):
                    left.childnode[1].childnode[j].parent = left.childnode[1]
        right.parent = binaryop
        left.parent = binaryop
        binaryop.childnode.append(left)
        binaryop.childnode.append(right)
        nodelist.append(binaryop)
        
    return {"node": nodelist[0], "index": i} # 최종 1개의 노드에 모두 담아서 리턴
    
def parse(code): # c-code를 읽어와 문자열을 리스트에 담는 과정 
    data = []
    textsymbol = ["=","+","-","*","/","&","(",")","{","}",";",",","\"","\'","<",">","%"]
    temp = ""
    skip = False
    # code에 있는 문자열 하나씩 가져와 특수문자 혹은 공백을 분리하여 담는 과정
    # <와 >는 <<, >>로 담아야해서 조건문으로 처리
    for text in code:
        if text in ["<",">"] and skip:
            skip = False
            continue
        if text in textsymbol or text.isspace():
            if text == "<":
                if not temp == "":
                    data.append(temp)
                    temp=""
                data.append("<<")
                skip = True
                continue
            if text == ">":
                if not temp == "":
                    data.append(temp)
                    temp=""
                data.append(">>")
                skip = True
                continue
            if not temp == "":
                data.append(temp)
                temp = ""
            if text in textsymbol:
                data.append(text)
        else:
            temp = temp + text
    if not temp == "":
        data.append(temp)
    l = 0
    fileast = node("FileAST", step = l)
    i = 0
    # i를 data의 끝까지 인덱스로 돌면서 code의 라인 하나하나를 처리하는 과정
    while i < len(data):
        l=0
        funcdef = node("FuncDef", step = l+1)
        funcdef.parent = fileast
        # 함수의 리턴 타입에 따른 조건문
        if data[i] == "int" or data[i] == "float" or data[i] == "double" or data[i] == "void":
            datatype = data[i]
            i+=1
            dataname = data[i]
            decl = node("Decl", step = l+2, name = dataname)
            funcdecl = node("FuncDecl", step = l+3)
            i+=1
            # parameter의 존재에 대한 처리
            if data[i]=="(":
                i+=1
                checkpar = 0
                if data[i]!=")":
                    checkpar = 1
                    paramlist = node("ParamList", step = l+4)
                while data[i]!=")":
                    pardatatype = data[i]
                    pardataname = data[i+1]
                    pardecl = node("Decl", step = l+5, name = pardataname)
                    partypedecl = node("TypeDecl", step = l+6, name = pardataname)
                    paridentifiertype = node("IdentifierType", step = l+7, name = pardatatype)
                    i+=2
                    if data[i]==",":
                        i+=1
                    paridentifiertype.parent = partypedecl
                    partypedecl.childnode.append(paridentifiertype)
                    partypedecl.parent = pardecl
                    pardecl.childnode.append(partypedecl)
                    pardecl.parent = paramlist
                    paramlist.childnode.append(pardecl)
                if checkpar == 1:
                    paramlist.parent = funcdecl
                    funcdecl.childnode.append(paramlist)
                typedecl = node("TypeDecl", step = l+4, name = dataname)
                identifiertype = node("IdentifierType", step = l+5, name = datatype)
                identifiertype.parent = typedecl
                typedecl.childnode.append(identifiertype)
                typedecl.parent = funcdecl
                funcdecl.childnode.append(typedecl)
            funcdecl.parent = decl
            decl.childnode.append(funcdecl)
            decl.parent = funcdef
            funcdef.childnode.append(decl)
            i+=1
            # 함수의 body 시작 { ~ } 사이를 읽어서 하나하나 ast구조로 처리
            if data[i]=="{":
                fixl = l+2
                compound = node("Compound", step = l+2)
                i+=1
                while data[i]!="}":
                    l=fixl
                    if data[i] == "int" or data[i] == "float" or data[i] == "double": # 처음 선언되는 변수 저장
                        bodydatatype = data[i]
                        bodydataname = data[i+1]
                        bodydecl = node("Decl", step = l+1, name = bodydataname)
                        bodytypedecl = node("TypeDecl", step = l+2, name = bodydataname)
                        bodyidentifiertype = node("IdentifierType", step = l+3, name = bodydatatype)
                        bodyidentifiertype.parent = bodytypedecl
                        bodytypedecl.childnode.append(bodyidentifiertype)
                        bodytypedecl.parent = bodydecl
                        bodydecl.childnode.append(bodytypedecl)
                        i+=2
                        if data[i]==";":
                            i+=1
                            bodydecl.parent = compound
                            compound.childnode.append(bodydecl)
                            continue
                        i+=1
                        opexp = operation(data, l+2, i, [";"],0)
                        i=opexp["index"]+1
                        opexpnode = opexp["node"]
                        opexpnode.parent = bodydecl
                        bodydecl.childnode.append(opexpnode)
                        bodydecl.parent = compound
                        compound.childnode.append(bodydecl)
                    elif i+1 < len(data) and data[i+1] == "=": # 이미 선언된 변수에 할당하는 경우
                        bodydataname = data[i]
                        bodydecl = node("Assingment", step = l+1, name ="=")
                        i+=2
                        opexp = operation(data, l+2, i, [";"],0)
                        i=opexp["index"]+1
                        opexpnode = opexp["node"]
                        opexpnode.parent = bodydecl
                        assignid = node("ID", step = l+2, name = bodydataname)
                        assignid.parent = bodydecl
                        bodydecl.childnode.append(assignid)
                        opexpnode.parent = bodydecl
                        bodydecl.childnode.append(opexpnode)
                        bodydecl.parent = compound
                        compound.childnode.append(bodydecl)
                    else: # 그 외의 문자열 처리(return, 함수호출, printf)
                        if data[i] == "printf": # 출력문
                            funcname = data[i]
                            funccall = node("FuncCall", step=l+1)
                            funcid = node("ID", step=l+2, name=funcname)   
                            funcid.parent = funccall                        
                            funccall.childnode.append(funcid)
                            i+=4
                            exprlist = node("ExprList", step=l+2)
                            if data[i]=="d": # 정수
                                constantprint = node("Constant", step=l+3, name="string, \"%"+"d\"")
                                constantprint.parent = exprlist
                                exprlist.childnode.append(constantprint)
                                i+=3
                                if is_digit(data[i])=="int":
                                    constantd = node("Constant", step=l+3, name="int, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                elif is_digit(data[i])=="double":
                                    constantd = node("Constant", step=l+3, name="double, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                else:
                                    constantd = node("ID", step=l+3, name=data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                            elif data[i]=="f": # 실수
                                constantprint = node("Constant", step=l+3, name="string, \"%"+"f\"")
                                constantprint.parent = exprlist
                                exprlist.childnode.append(constantprint)
                                i+=3
                                if is_digit(data[i])=="int":
                                    constantd = node("Constant", step=l+3, name="int, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                elif is_digit(data[i])=="double":
                                    constantd = node("Constant", step=l+3, name="double, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                else:
                                    constantd = node("ID", step=l+3, name=data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                            elif data[i]=="lf": # 실수 Double
                                constantprint = node("Constant", step=l+3, name="string, \"%"+"lf\"")
                                constantprint.parent = exprlist
                                exprlist.childnode.append(constantprint)
                                i+=3
                                if is_digit(data[i])=="int":
                                    constantd = node("Constant", step=l+3, name="int, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                elif is_digit(data[i])=="double":
                                    constantd = node("Constant", step=l+3, name="double, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                else:
                                    constantd = node("ID", step=l+3, name=data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                            exprlist.parent = funccall
                            funccall.childnode.append(exprlist)
                            funccall.parent = compound
                            compound.childnode.append(funccall)
                            i += 3
                        elif data[i]=="return": # 리턴
                            i+=1
                            returnnode = node("Return", step=l+1)
                            opexp = operation(data, l+2, i, [";"],0)
                            i=opexp["index"]+1
                            opexpnode = opexp["node"]
                            opexpnode.parent = returnnode
                            returnnode.childnode.append(opexpnode)
                            returnnode.parent = compound
                            compound.childnode.append(returnnode)
                            if data[i]==";":
                                i+=1
                                continue
                        else: # 그 외의 user-defined 함수 호출
                            funcname = data[i]
                            funccall = node("FuncCall", step=l)
                            funcid = node("ID", step=l+1, name=funcname)      
                            funcid.parent = funccall                     
                            funccall.childnode.append(funcid)
                            i += 2
                            check = 0
                            if data[i] != ")":
                                exprlist = node("ExprList", step=l+1)
                                check = 1
                            while data[i] != ")":
                                if data[i] == ",":
                                    i += 1
                                    continue
                                if is_digit(data[i])=="int":
                                    constantd = node("Constant", step=l+2, name="int, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                elif is_digit(data[i])=="double":
                                    constantd = node("Constant", step=l+2, name="double, "+data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                else:
                                    constantd = node("ID", step=l+2, name=data[i])
                                    constantd.parent = exprlist
                                    exprlist.childnode.append(constantd)
                                i += 1
                            if check:
                                exprlist.parent = funccall
                                funccall.childnode.append(exprlist)
                            funccall.parent = compound
                            compound.childnode.append(funccall)
                            i+=2        
                i+=1
                compound.parent = funcdef
                funcdef.childnode.append(compound)
        funcdef.parent = fileast
        fileast.childnode.append(funcdef)
    # 전부 계층 구조로 부모노드에 포함시켜 최종적으로 FileAst가 루트노드가 되도록 설정
    return fileast

# 실제 expr로 ast의 노드를 가져와 식을 계산하는 과정
def calculator(expr, varname, value, type, functions, printv):
    if expr.nodetype == "Constant": # 값이 상수일때
        vartype, varvalue = expr.name.split(", ")
        if vartype == "int":
            return int(varvalue)
        elif vartype == "double":
            return float(varvalue)
    elif expr.nodetype == "ID": # 값이 변수일 때 
        return value[expr.name]
    elif expr.nodetype == "BinaryOp": # 연산되어 있는 값인 경우
        if len(expr.childnode) != 2:
            return 0
        op = expr.name
        left = calculator(expr.childnode[0], varname, value, type, functions, printv)
        right = calculator(expr.childnode[1], varname, value, type, functions, printv)
        if left is None:
            print("left None!", expr.childnode[0].name, " ", varname)
        if right is None:
            print("right None!", expr.childnode[1].name, " ", varname)
        if op in ["^", "|", "&", "<<", ">>"]:
            left = left&0xFFFFFFFF
            lmsb = left&0x80000000
            if lmsb:
                left = -(0x100000000 - left)
            right = right&0xFFFFFFFF
            rmsb = right&0x80000000
            if rmsb:
                right = -(0x100000000 - right)
        if op == "+":
            return left+right
        elif op == "-":
            return left-right
        elif op == "*":
            return left*right
        elif op == "/":
            return left//right
        elif op == "%":
            return left%right
        # bitwise연산은 32bit 정수일 경우만 고려
        elif op == "^":
            if isinstance(left, int) and isinstance(right, int):
                v = left^right
                v = v&0xFFFFFFFF
                msb = v&0x80000000
                if msb:
                    v = -(0x100000000 - v)
                return v
        elif op == "|":
            if isinstance(left, int) and isinstance(right, int):
                v = left|right
                v = v&0xFFFFFFFF
                msb = v&0x80000000
                if msb:
                    v = -(0x100000000 - v)
                return v
        elif op == "&":
            if isinstance(left, int) and isinstance(right, int):
                v = left&right
                v = v&0xFFFFFFFF
                msb = v&0x80000000
                if msb:
                    v = -(0x100000000 - v)
                return v
        elif op == "<<":
            if isinstance(left, int) and isinstance(right, int):
                if right >= 0 and right < 32:
                    v = left<<right
                    v = v&0xFFFFFFFF
                    msb = v&0x80000000
                    if msb:
                        v = -(0x100000000 - v)
                    return v
        elif op == ">>":
            if isinstance(left, int) and isinstance(right, int):
                if right >= 0 and right < 32:
                    v = left>>right
                    v = v&0xFFFFFFFF
                    msb = v&0x80000000
                    if msb:
                        v = -(0x100000000 - v)
                    return v
        else:
            return 0
    elif expr.nodetype == "Assignment": # 선언되어 있는 변수를 재할당하는 경우 
        Idv = expr.childnode[0].name
        a = calculator(expr.childnode[1], Idv, value, type, functions, printv)
        return a
    elif expr.nodetype == "Decl": # 변수 선언
        if len(expr.childnode) == 1:
            if expr.childnode[0].nodetype == "TypeDecl":
                typeexpr = expr.childnode[0]
                vartype = typeexpr.childnode[0].name
                type[varname] = vartype
            else:
                return calculator(expr.childnode[0], varname, value, type, functions, printv)
        elif len(expr.childnode) > 1:
            typeexpr = expr.childnode[0]
            vartype = typeexpr.childnode[0].name
            type[varname] = vartype
            return calculator(expr.childnode[1], varname, value, type, functions, printv)
    elif expr.nodetype == "FuncCall": # 함수 호출
        funcname = expr.childnode[0].name
        if funcname == "printf":
            printfexprnode = expr.childnode[1]
            printfconstant = printfexprnode.childnode[0].name
            printfsymbol = printfconstant[printfconstant.find("%")+1]
            if printfsymbol == "d":
                printv.append(calculator(printfexprnode.childnode[1], varname, value, type, functions, printv))
            elif printfsymbol == "f" or "l":
                printv.append(round(calculator(printfexprnode.childnode[1], varname, value, type, functions, printv), 6)) 
            return None
        else:
            targetfun = functions.get(funcname)
            declare = targetfun.childnode[0]
            fundeclare = declare.childnode[0]
            if len(fundeclare.childnode) > 1:
                argument = expr.childnode[1].childnode
                argvalue = []
                for argnode in argument:
                    argvalue.append(calculator(argnode, varname, value, type, functions, printv))
                parameterlist = fundeclare.childnode[0]
                paras = []
                for p in parameterlist.childnode:
                    paras.append(p.name)
                for p, a in zip(paras, argvalue):
                    value[p] = a
                funcompound = targetfun.childnode[1]
            for funline in funcompound.childnode:
                if funline.nodetype == "Return":
                    return calculator(funline, funline.childnode[0].name, value, type, functions, printv)
                elif funline.nodetype == "Decl" or funline.nodetype == "FuncCall" or funline.nodetype == "Assignment":
                    value[varname] = calculator(funline, funline.childnode[0].name, value, type, functions, printv)
            return 0
    elif expr.nodetype == "Return": # 리턴을 만나는 경우
        return calculator(expr.childnode[0], varname, value, type, functions, printv)
# ast tree를 받아와 calculator함수를 통해 실제 값을 계산하여 출력하는 함수
def eval(tree):
    value = {}
    type = {}
    functions = {} # 함수명을 담아둘 리스트
    printv = [] # printf문을 담아둘 리스트
    maincheck = 0
    for find_fdef in tree.childnode:
        if find_fdef.nodetype == "FuncDef":
            for find_dec in find_fdef.childnode:
                if find_dec.nodetype == "Decl":
                    functions[find_dec.name] = find_fdef
    for fdef in tree.childnode:
        if maincheck == 0:
            if fdef.childnode[0].name != "main": # main함수 먼저 읽어야 하므로 maincheck를 통해 체크
                continue
            else:
                if fdef.childnode[1].nodetype == "Compound": # 함수의 body 부분
                    comp = fdef.childnode[1]
                    for line in comp.childnode:
                        if line.nodetype == "Decl" or line.nodetype == "Assignment":
                            varname = line.childnode[0].name
                            value[varname] = calculator(line, varname, value, type, functions, printv)
                        else:
                            varname = line.childnode[0].name
                            value[varname] = calculator(line, varname, value, type, functions, printv)
                maincheck = 1        
        else:
            if fdef.childnode[1].nodetype == "Compound": # 함수의 body 부분
                    comp = fdef.childnode[1]
                    for line in comp.childnode:
                        if line.nodetype == "Decl" or line.nodetype == "Assignment":
                            varname = line.childnode[0].name
                            value[varname] = calculator(line, varname, value, type, functions, printv)
                        else:
                            varname = line.childnode[0].name    
                            value[varname] = calculator(line, varname, value, type, functions, printv) 
    # printf 순서대로 출력
    for result in printv:
        print("Computation Result:", result)

def main():
    with open(sys.argv[1], "r") as file:
        ccode = file.read()
    

    ast = parse(ccode)
    print(ast.show())
    eval(ast)
    
if __name__ == "__main__":
    main()
