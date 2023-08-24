# Konstantinos Kikidis, 4387, cse84387
# Konstantinos Tsampiras, 4508, cse84508
# To run, type on terminal (on lab computers): python3 CimpleCompiler.py <filename.ci>

import sys

# Token Class, responsible for holding token data
class Token:
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number
    def __str__(self):
        return (str(self.recognized_string) + "\t\tfamily:" + str(self.family) + ",  line: " + str(self.line_number))


# Classes for Symbol Table Implementation
class Scope:
    global depth
    entityList = []
    nestingLevel = 0
    offset = 0
    def __init__(self):
        self.nestingLevel = depth + 1
        self.entityList = []
        self.offset =12

class Entity:
    name = ""
    type = ""
    startingQuad = 0
    args = []
    offset = 0
    parameterMode = ""
    def __init__(self, name, type, startingQuad):
        self.name = name
        self.type = type
        self.startingQuad = startingQuad
        self.args = []

class Argument:
    parmode = ""
    nextArg = None
    def __init__(self, parmode):
        self.parmode = parmode


# Final Code

def gnlvcode(variable):
    global depth
    global table
    global final
    tempScope, tempEntity = searchEntity(variable)
    x = ""
    x += "      lw t0,-4(sp) \n" 
    lvl = depth-tempScope.nestingLevel-1
    for i in range(lvl):
        x += "    lw t0,-4(sp) \n" 
    x += "      addi t0,t0,-" + str(tempEntity.offset) + " \n"
    final.append(x)

def loadvr(v, reg):
    global depth
    global final
    if (str(v).isdigit()):
        final.append("      li " + reg + "," + v + " \n") # "li reg, integer"
    else:
        tempScope, tempEntity = searchEntity(v)
        lvl = tempScope.nestingLevel
        if (lvl == depth and (tempEntity.type == "temporary" or tempEntity.type == "in" or tempEntity.type == "id")):
            final.append("      lw " + reg + ",-" + str(tempEntity.offset)+ "(sp) \n")
        elif (lvl == depth and tempEntity.type == "inout"):
            final.append("      lw t0,-" + str(tempEntity.offset) + "(sp) \n")
            final.append("      lw " + reg + ",(t0) \n")
        elif (lvl == 0 and tempEntity.type == "id"):
            final.append("      lw " + reg + ",-" + str(tempEntity.offset) + "(gp) \n")
        elif (lvl < depth and (tempEntity.type == "in" or tempEntity.type == "id")):
            gnlvcode(v)
            final.append("      lw " + reg + ",(t0) \n")
        elif (lvl < depth and tempEntity.type == "inout"):
            gnlvcode(v)
            final.append("      lw t0,(t0) \n")
            final.append("      lw " + reg + ",(t0) \n")
        
def storerv(reg, v):
    global depth
    global final
    if ( str(v).isdigit()):
        final.append("      li " + v + "," + reg + " \n")
    else:  
        tempScope, tempEntity = searchEntity(v)
        lvl = tempScope.nestingLevel
        if (lvl == depth and (tempEntity.type == "temporary" or tempEntity.type == "in" or tempEntity.type == "id")):
            final.append("      sw " + reg + ",-" + str(tempEntity.offset)+ "(sp) \n")
        elif (lvl == depth and tempEntity.type == "inout"):
            final.append("      lw t0,-" + str(tempEntity.offset) + "(sp) \n")
            final.append("      sw " + reg + ",(t0) \n")
        elif (lvl == 0 and tempEntity.type == "id"):
            final.append("      sw " + reg + ",-" + str(tempEntity.offset) + "(gp) \n")
        elif (lvl < depth and (tempEntity.type == "in" or tempEntity.type == "id")):
            gnlvcode(v)
            final.append("      sw " + reg + ",(t0) \n")
        elif (lvl < depth and tempEntity.type == "inout"):
            gnlvcode(v)
            final.append("      lw t0,(t0) \n")
            final.append("      sw " + reg + ",(t0) \n")
        
def riscVBlock(blockName, sQuad):
    global quadList
    global final
    global label
    for q in quadList[sQuad-1::]:
        final.append("L" + q[0] + ":        \n")
        riscVAssemblyGen(q, blockName)

def riscVAssemblyGen(quad, blockName):
    global final
    global quadList
    global main_name
    global table
    global paramFlag
    global paramList
    operator = quad[1]
    if (operator == "jump"):
        final.append("      b L"+str(quad[4])+" \n")
    elif (operator == "+"):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      add t1,t1,t2 \n")
        storerv("t1", quad[4])
    elif (operator == "-"):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      sub t1,t1,t2 \n")
        storerv("t1", quad[4])
    elif (operator == "*"):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      mul t1,t1,t2 \n")
        storerv("t1", quad[4])
    elif (operator == "/"):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      div t1,t1,t2 \n")
        storerv("t1", quad[4])
    elif (operator == "="):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      beq t1,t2,L" + quad[4] + " \n")
    elif (operator == "<>"):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      bne t1,t2,L" + quad[4] + " \n")
    elif (operator == ">"):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      bgt t1,t2,L" + quad[4] + " \n")
    elif (operator == "<"):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      blt t1,t2,L" + quad[4] + " \n")
    elif (operator == ">="):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      bge t1,t2,L" + quad[4] + " \n")
    elif (operator == "<="):
        loadvr(quad[2], "t1")
        loadvr(quad[3], "t2")
        final.append("      ble t1,t2,L" + quad[4] + " \n")
    elif (operator == ":="):
        loadvr(quad[2], "t1")
        storerv("t1", quad[4])
    elif (operator == "out"):
        loadvr(quad[2], "a0")
        final.append("      li a7,1 \n")
        final.append("      ecall \n")
    elif (operator == "inp"):
        final.append("      li a7,5 \n")
        final.append("      ecall \n")
        storerv("a0", quad[2])
    elif (operator == "retv"):
        loadvr(quad[2], "t1")
        final.append("      lw t0,-8(sp) \n")
        final.append("      sw t1,(t0) \n")
    elif (operator == "halt"):
        final.append("      li a0,0 \n")
        final.append("      li a7,93 \n")
        final.append("      ecall \n")
    elif (operator == "begin_block"):
        if (main_name == blockName):
            final.append("      addi sp,sp," + str(table[0].offset) + " \n")
            final.append("      mv gp,sp \n")
        else:
            final.append("      sw ra,-0(sp) \n")
    elif (operator == "end_block"):
        if (main_name != blockName):
            final.append("      lw ra,-0(sp) \n")
            final.append("      jr ra \n")
    elif (operator == "par"):
        if (paramFlag == False):
            zz = int(quad[0])
            paramCounter = 0
            while (quadList[zz-1][1] != "call"):
                paramCounter+=1
                paramList.append(paramCounter)
                zz+=1
            calleeName = quadList[zz-1][2]
            calleeScope, calleeEntity = searchEntity(calleeName)
            final.append("      addi fp,sp," + str(calleeEntity.offset) + " \n")
            paramFlag = True
        if (blockName != main_name):
            callerScope, callerEntity = searchEntity(blockName)
            callerOffset = callerEntity.offset
            callerScope = callerScope.nestingLevel
        else:
            callerScope = 0
            callerOffset = table[0].offset
        if (quad[3] == "cv"):
            loadvr(quad[2], "t0")
            index = paramList.pop(0)
            d = 12+4*(index-1)
            final.append("      sw t0,-" + str(d) + "(fp) \n")
        elif (quad[3] == "ref"):
            entityScope, entity = searchEntity(quad[2])
            if (entityScope.nestingLevel == callerScope):
                if (entity.type == "id" or entity.type == "in"):
                    index = paramList.pop(0)
                    d = 12+4*(index-1)
                    final.append("      addi t0,sp,-" + str(entity.offset) + " \n")
                    final.append("      sw t0,-" + str(d) + "(fp) \n")
                elif (entity.type == "inout"):
                    index = paramList.pop(0)
                    d = 12+4*(index-1)
                    final.append("      lw t0,-" + str(entity.offset) + "(sp) \n")
                    final.append("      sw t0,-" + str(d) + "(fp) \n")
            else:
                if (entity.type == "id" or entity.type == "in"):
                    index = paramList.pop(0)
                    d = 12+4*(index-1)
                    gnlvcode(quad[2])
                    final.append("      sw t0,-" + str(d) + "(fp) \n")
                elif (entity.type == "inout"):
                    index = paramList.pop(0)
                    d = 12+4*(index-1)
                    gnlvcode(quad[2])
                    final.append("      lw t0,(t0) \n")
                    final.append("      sw t0,-" + str(d) + "(fp) \n")
        elif (quad[3] == "ret"):
            entityScope, entity = searchEntity(quad[2])
            final.append("      addi t0,sp,-" + str(entity.offset) + " \n" )
            final.append("      sw t0,-8(fp) \n")
    elif (operator == "call"):
        calleeName = quad[2]
        calleeScope, calleeEntity = searchEntity(calleeName)
        calleeLevel = calleeEntity.scope
        if (blockName == main_name):
            callerLevel = 0
            callerFrame = table[0].offset
        else:
            callerScope, callerEntity = searchEntity(blockName)
            callerLevel = callerScope.nestingLevel
            callerFrame = callerEntity.offset
        if (paramFlag == False):
            final.append("      addi fp,sp, " + str(calleeEntity.offset) + " \n")
        if (calleeLevel == callerLevel):
            final.append("      lw t0,-4(sp) \n")
            final.append("      sw t0,-4(fp) \n")
        else:
            final.append("      sw sp,-4(fp) \n")
        final.append("      addi sp,sp," + str(calleeEntity.offset) + " \n")
        final.append("      jal L" + str(calleeEntity.startingQuad) + " \n") 
        final.append("      addi sp,sp,-" + str(calleeEntity.offset) + " \n")
        paramFlag = False

def writeRiscVAsm(file):
    global final
    asm = file[:len(file)-2] + "asm"
    output = open(asm, "w")
    for i in final:
        output.write(i)
    output.close()


# Symbol Table
def addEntity(name, type, quad):
    global table
    global depth
    anEntity = Entity(name, type, quad)
    for x in table[depth].entityList:
        if (x.name == anEntity.name and x.type == anEntity.type):
            print("Name " + x.name + " is already defined")
    if (type == "id"):
        anEntity.offset = table[depth].offset
        table[depth].offset += 4
        table[depth].entityList.append(anEntity)
    elif (type == "temporary"):
        anEntity.offset = table[depth].offset
        table[depth].offset += 4
        table[depth].entityList.append(anEntity)
    elif (type == "in"):
        anEntity.offset = table[depth].offset
        anEntity.parameterMode = "cv"
        table[depth].offset += 4
        table[depth].entityList.append(anEntity)
    elif (type == "inout"):
        anEntity.offset = table[depth].offset
        anEntity.parameterMode = "ref"
        table[depth].offset += 4
        table[depth].entityList.append(anEntity)
    elif (type == "function"):
        anEntity.offset = 12
        anEntity.scope = depth + 1
        table[depth].entityList.append(anEntity)
        addScope()
    elif (type == "procedure"):
        anEntity.offset = 12
        anEntity.scope = depth + 1
        table[depth].entityList.append(anEntity)
        addScope()

def addScope():
    global table
    global depth
    aScope = Scope()
    depth += 1
    table.append(aScope)

def deleteScope():
    global table
    global depth
    table.pop()
    depth -= 1

def addArgument(arg):
    global table
    global depth
    nextArg = Argument(arg)
    idx = len(table[depth-1].entityList)-1 # index of last entity
    table[depth-1].entityList[idx].args.append(nextArg) # in entity list of specified scope, add the in and inout at the last entity.

def searchEntity(name):
    global table
    global token
    for scope in table[::-1]:
        for entity in scope.entityList:
            if (entity.name == name):
                return (scope, entity)
    print("Variable " + name + " isn't declared")
    sys.exit()

def existEntity(entityName, entityType):
    global table
    global depth
    depthCounter = depth
    level = table[depthCounter]
    while (len(table) != 0):
        for anEntity in level.entityList:
            if (anEntity.name == entityName and anEntity.type == entityType):
                return
        depthCounter -= 1
        if (depthCounter < 0):
            break
        level = table[depthCounter]
    print("The " + entityName + " " + entityType + " wasn't found")
    sys.exit(0)

def symbolTableGen():
    global table
    global symTable
    out = ""
    for x in table:
        if (len(table) > 1):
            out += "Nesting Level: " + str(x.nestingLevel) + "  "
        else:
            out += "Nesting Level: " + str(x.nestingLevel) + "  " + main_name + ":" + str(x.offset) + " "
        for y in x.entityList:
            if (y.type == "function" or y.type == "procedure"):
                out += str(y.name) + "/" + str(y.offset) + " "
                for z in y.args:
                    out +=  "->" + str(z.parmode) + " "
            elif (y.type == "in" or y.type == "inout"):
                out += str(y.name) + "/" + str(y.offset) + "/" + str(y.parameterMode) + " "
            else:
                out += str(y.name) + "/" + str(y.offset) + " " 
        out += "\n"
    out += "========================================\n"
    symTable.append(out)

def writeSymTable(Filename):
    global symTable
    a = Filename[:len(Filename)-2] + "symb"
    output= open(a,"w")
    for i in symTable:
        output.write(i) 
    output.close()


# Intercode Generation
def genQuad(operator, operand1, operand2, operand3):
    global label
    global quadList
    label += 1
    quad = [str(label), str(operator), str(operand1), str(operand2), str(operand3)]
    quadList.append(quad)

def nextQuad():
    global label
    return (label+1)

def newTemp():
    global tempCounter
    global variables
    temp = "T_"+str(tempCounter)
    tempCounter+=1
    variables.append(temp)
    addEntity(temp, "temporary", None) 
    return (temp)

def emptyList():
    return ([])  

def makeList(x):
    aList = []
    xStr = str(x)
    aList.append(xStr)
    return (aList)

def mergeList(list1, list2):
    mergedList = list1 + list2
    return (mergedList)

def backpatch(listX, labelY):
    global quadList
    y = str(labelY)
    for i in range(len(listX)):
        label = listX[i]
        for j in range(len(quadList)):
            z = quadList[j]
            if (z[0] == label):
                z[4] = y
                break

def intercodeGen(file):
    global quadList
    quads = ""
    intFile = file[:len(file)-2] + "int"
    output = open(intFile, "w")
    for i in range(len(quadList)):
        x = quadList[i]
        quads = x[0] + ":"
        for j in range(1,5):
            quads = quads + " " + str(x[j])
        quads += "\n"
        output.write(quads)
    output.close()

def cCodeGen(file):
    global quadList
    cFile = file[:len(file)-2] + "c"
    f = open(cFile, "w")
    x = "#include <stdio.h>" + "\n" + "int main(){ \n " + "int " + ",".join(variables)+ ";\n"
    f.write(x)
    for i in range(len(quadList)):
        y = quadList[i]
        quads = y[0] + " : "
        if (y[1] == ":="):
            quads += y[4] + "=" + y[2] + ";"
        elif (y[1] == "+" or y[1] == "-" or y[1] == "*" or y[1] == "/"):
            quads += y[4] + "=" + y[2] + y[1] + y[3] + ";"
        elif (y[1] == "<" or y[1] == ">" or y[1] == "<=" or y[1] == ">="):
            quads += "if(" + y[2] + y[1] + y[3] + ") goto " + y[4] + ";"
        elif (y[1] == "<>"):
            quads += "if(" + y[2] + "!=" + y[3] + ") goto " + y[4] + ";"
        elif (y[1] == "="):
            quads += "if(" + y[2] + "==" + y[3] + ") goto " + y[4] + ";"
        elif (y[1] == "inp"):
            quads += "scanf(\"%d\",&" + y[2] + ");"
        elif (y[1] == "out"):
            quads += "printf(\"%d\",&" + y[2] + ");"
        elif (y[1] == "retv"):
            quads += "return " + y[2] + ";"
        elif (y[1] == "jump"):
            quads += "goto "+ str(y[4]) + ";"
        else:
            quads += ";"
        quads += "\n"
        f.write(quads)
    f.write("}")
    f.close()


# Syntax Analyzer
def syntax_analyzer():
    global token
    token = get_token()
    program()
    print("Compilation successfully completed")  

def get_token():
    global index
    global all_tokens
    index += 1
    if (index == len(all_tokens)):
    #    print("DEBUG: End Token ")                                  # For Debugging Purposes
        return (Token("",0,0))
    #print("DEBUG: Examining Token : " + str(all_tokens[index]))     # For Debugging Purposes
    return (all_tokens[index])

def error(typeOfError):
    global line 
    global token
    errors = {
        "validId": "A valid id was expected at line ",
        "plusOrMinus": "A \"+\" or \"-\" was expected at line ",
        "mulOrDiv": "A \"*\" or \"/\" was expected at line ",
        "asgnSym": "The \":=\" was expected at line ",
        "closeCurBracket": "Curly bracket hasn't closed at line ",
        "openCurBracket": "Curly bracket expected at line ",
        "closeSqBracket": "Square bracket hasn't closed at line ",
        "openSqBracket": "Square bracket expected at line ",
        "closeParentheses": "Parentheses hasn't closed at line ",
        "openParentheses": "Parentheses expected at line ",
        "numExprId": "Number/(Expression)/ID expected at line ",
        "defaultNotFound": "Default case not found around line ",
        "programKeywordNF": "\"program\" keyword not found at line ",
        "dotExpected": "A \".\" was expected at line ",
        "eofExpected": "Characters found after \".\", line ",
        "relOpExpected": "One of the =, <=, >=, >, <, <> symbols are expected at line ",
        "semicolonExpected": "A \";\" was expected at line ",
        "invalidFuncName": "Invalid function name at line ",
        "invalidProcName": "Invalid procedure name at line "
    }
    print(errors[typeOfError] + str(token.line_number))
    sys.exit()

def actualparitem():
    global token
    id = ""
    exp = ""
    if (token.recognized_string == "in"):
        token = get_token()
        exp = expression()
        return (exp, "cv")
    elif (token.recognized_string == "inout"):
        token = get_token()
        if (token.family == "id"):
            id = token.recognized_string
            token = get_token()
            return (id, "ref")
        else:
            error("validId") # valid id expected

def actualparlist():
    global token
    tmpList = []
    if (token.recognized_string == "in" or token.recognized_string == "inout"):    
        (name, vartype) = actualparitem()
        tmpList.append((name, vartype))
        while (token.recognized_string == ","):
            token = get_token()
            (name, vartype) = actualparitem()
            tmpList.append((name, vartype))
        for i in tmpList:
            genQuad("par", i[0], i[1], "_")

def addoperator():
    global token
    if (token.recognized_string == "+"):
        token = get_token()
    elif (token.recognized_string == "-"):
        token = get_token()
    else:
        error("plusOrMinus") # +, -
        
def assignStat():
    global token
    if (token.family == "id"):
        eplace = ""
        x = token.recognized_string
        token = get_token()
        if (token.recognized_string == ":="):
            token = get_token()   
            eplace = expression()
            genQuad(":=", eplace, "_", x)
        else:
            error("asgnSym") # assignment symbol expected
    else: 
        error("validId") # not an id, is (another family)

def block():
    global token
    global label
    global main_name
    global final
    if (token.recognized_string == "{"):
        token = get_token()
        declarations()
        final.append("L0:   b L" + main_name + " \n")
        subprograms()
        genQuad("begin_block", main_name, "_", "_")
        startingQuadLabel = label
        blockstatements()
        final.append("L" + main_name + ": \n")
        genQuad("halt", "_", "_", "_")
        genQuad("end_block", main_name, "_", "_")
        symbolTableGen()
        riscVBlock(main_name, startingQuadLabel)
        deleteScope()
        if (token.recognized_string == "}"):
            token = get_token()
        else:
            error("closeCurBracket") # } expected
    else:
        error("openCurBracket") # start of block with { expected

def blockfuncproc(id):
    global table
    global label
    global token
    global ret
    if (token.recognized_string == "{"):
        token = get_token()
        declarations()
        subprograms()           
        genQuad("begin_block",id,"_", "_")
        idx = len(table[depth-1].entityList)-1
        ent = table[depth-1].entityList[idx]
        ent.startingQuad = label
        ret = False
        blockstatements()
        ent.offset = table[depth].offset
        genQuad("end_block",id,"_", "_")
        symbolTableGen()
        riscVBlock(ent.name, ent.startingQuad)
        deleteScope()
        if (token.recognized_string == "}"):
            token = get_token()
        #elif (token.recognized_string == "function" or token.recognized_string == "procedure"):
        #    token = get_token()
        #    subprogram()               # incase we have a function/procedure inside a function/procedure (doesn't work as intended)
        else:
            error("closeCurBracket") # } expected
    else:
        error("openCurBracket") # start of block with { expected

def blockstatements():
    global token
    statement()
    while (token.recognized_string == ";"):
        token = get_token()
        statement()

def boolfactor():
    global token
    global label
    relop = ""
    e1place = ""
    e2place = ""
    eCondTrue = emptyList()
    eCondFalse = emptyList()
    if (token.recognized_string == "not"):
        token = get_token()
        if (token.recognized_string == "["):
            token = get_token()
            eCondTrue,eCondFalse = condition()
            if (token.recognized_string == "]"):
                token = get_token()
            else:
                error("closeSqBracket") # ] expected
        else: 
            error("openSqBracket") # [ expected
    elif (token.recognized_string == "["):
        token = get_token()
        eCondTrue,eCondFalse = condition()
        if (token.recognized_string == "]"):
            token = get_token()
        else:
            error("closeSqBracket") # ] expected
    else: 
        e1place = expression()
        relop = reloperator()
        e2place = expression()
        x = nextQuad()
        eCondTrue = makeList(x)
        genQuad(relop,e1place,e2place,"_")
        x = nextQuad()
        eCondFalse = makeList(x)
        genQuad("jump","_","_","_")
    return (eCondTrue, eCondFalse)

def boolterm():
    global token
    conditionTrue = emptyList()
    conditionFalse = emptyList()
    q1CondTrue = emptyList()
    q1CondFalse = emptyList()
    q2CondTrue = emptyList()
    q2CondFalse = emptyList()
    q1CondTrue, q1CondFalse = boolfactor()
    conditionTrue = q1CondTrue
    conditionFalse = q1CondFalse
    while (token.recognized_string == "and"):
        backpatch(conditionTrue, nextQuad())
        token = get_token()
        q2CondTrue, q2CondFalse = boolfactor()
        conditionFalse = mergeList(conditionFalse, q2CondFalse)
        conditionTrue = q2CondTrue
    return (conditionTrue, conditionFalse)

def callStat():
    global token
    global flag
    global fname
    flag = True
    idplace = ""
    token = get_token() # consume call
    if (token.family == "id"):
        idplace = token.recognized_string
        token = get_token()
        if (token.recognized_string == "("):
            token = get_token()
            actualparlist()
            if (token.recognized_string == ")"):
                if (flag == False):
                    x = newTemp()
                    genQuad("par",x,"ret","_")
                    existEntity(idplace, "procedure")
                token = get_token()
                if (flag == False):
                    return (x)
            else:
                error("closeParentheses") # ) expected
            genQuad("call", idplace, "_", "_")
        else:
            error("openParentheses") # ( 
    else:
        error("validId") # a valid id expected
    flag = False
                        
def condition():
    global token
    conditionTrue = emptyList()
    conditionFalse = emptyList()
    q1CondTrue = emptyList()
    q1CondFalse = emptyList()
    q2CondTrue = emptyList()
    q2CondFalse = emptyList()
    q1CondTrue, q1CondFalse = boolterm()
    conditionTrue = q1CondTrue
    conditionFalse = q1CondFalse
    while (token.recognized_string == "or"):
        backpatch(conditionFalse, nextQuad())
        token = get_token()
        q2CondTrue, q2CondFalse = boolterm()
        conditionTrue = mergeList(conditionTrue, q2CondTrue)
        conditionFalse = q2CondFalse
    return (conditionTrue, conditionFalse)

def declarations():
    global token
    while (token.recognized_string == "declare"):
        token = get_token()
        varlist()
        if (token.recognized_string == ";"):
            token = get_token()
        else:
            error("semicolonExpected") # ";" expected but something else came

def elsepart():
    global token
    if (token.recognized_string == "else"):
        token = get_token()
        statements()

def expression():
    global token
    global index
    t1place = ""
    t2place = ""
    eplace = ""
    optionalSign()
    if (token.family != "id" and token.family != "number"):
        token = get_token()
    t1place = term()
    while (token.recognized_string == "+" or token.recognized_string == "-"):
        operator = token.recognized_string
        addoperator()
        t2place = term()
        x = newTemp()
        genQuad(operator, t1place, t2place, x)
        t1place = x
        if (token.recognized_string == ")"):
            token = get_token()
            if (token.recognized_string == ";"):
                index -= 2
                token = get_token()
    eplace = t1place
    return (eplace)

def factor():
    global token
    global fname
    t1place = ""
    t2place = ""
    if (token.family == "number"):
        t1place = token.recognized_string
        token = get_token()
        return (t1place)
    elif (token.recognized_string == "("):
        token = get_token()
        t1place = expression()
        if (token.recognized_string == ")"):
            token = get_token()
            return (t1place)
        else:
            error("closeParentheses") # ) expected
    elif (token.family == "id"):
        t1place = token.recognized_string
        token = get_token()
        if (token.recognized_string == "("):
            fname = t1place
        t2place = idtail()
        if (t2place != ""):
            return (t2place)
        return (t1place)
    else:
        error("numExprId") # number or (expression) or id expected

def forcaseStat():
    global token
    conditionTrue = emptyList()
    conditionFalse = emptyList()
    token = get_token() # consume forcase
    firstCondQuad = nextQuad()
    while (token.recognized_string == "case"):
        token = get_token()
        if (token.recognized_string == "("):
            conditionTrue, conditionFalse = condition()
            backpatch(conditionTrue,nextQuad())
            if (token.recognized_string == ")"):
                token = get_token()
                statements()
                genQuad("jump","_","_",firstCondQuad)
                backpatch(conditionFalse,nextQuad())
            else: 
                error("closeParentheses") # ) expected
        else:
            error("openParentheses") # ( expected
    if (token.recognized_string == "default"):
        statements()
    else:
        error("defaultNotFound") # you have to enter a default case
        
def formalparitem():
    global token
    if (token.recognized_string == "in"):
        token = get_token()
        if (token.family == "id"):
            addEntity(token.recognized_string, "in", None) 
            addArgument("in")
            token = get_token()
        else:
            error("validId") # valid id expected
    elif (token.recognized_string == "inout"):
        token = get_token()
        if (token.family == "id"):
            addEntity(token.recognized_string, "inout", None) 
            addArgument("inout")
            token = get_token()
        else:
            error("validId") # valid id expected

def formalparlist():
    global token
    if (token.recognized_string == "in" or token.recognized_string == "inout"):    
        formalparitem()
        while (token.recognized_string == ","):
            token = get_token()
            formalparitem()
    
def idtail():
    global token
    global flag
    global fname
    eplace = ""
    if (token.recognized_string == "("):
        token = get_token()
        actualparlist()
        if (token.recognized_string == ")"):
            if (flag == False):
                x = newTemp()
                genQuad("par",x,"ret","_")
                genQuad("call",fname,"_","_")
                existEntity(fname, "function")
            token = get_token()
            if (flag == False):
                eplace = x
        else:
            error("closeParentheses") # ) expected
    return (eplace)

def ifStat():
    global token
    conditionTrue = emptyList()
    conditionFalse = emptyList()
    ifList = emptyList()
    token = get_token() # consume if
    if (token.recognized_string == "("):
        token = get_token()
        conditionTrue, conditionFalse = condition()
        if (token.recognized_string == ")"):
            backpatch(conditionTrue, nextQuad())
            token = get_token()
            statements()
            ifList = makeList(nextQuad())
            genQuad("jump", "_", "_", "_")
            backpatch(conditionFalse, nextQuad())
            elsepart()
            backpatch(ifList, nextQuad())
        else:
            error("closeParentheses")
    else:
        error("openParentheses")

def incaseStat():
    global token
    conditionTrue = emptyList()
    conditionFalse = emptyList()
    token = get_token() # consume incase
    flag = newTemp()
    firstCondQuad = nextQuad()
    genQuad(":=","0","_",flag)
    while (token.recognized_string == "case"):
        token = get_token()
        if (token.recognized_string == "("):
            conditionTrue,conditionFalse = condition() 
            backpatch(conditionTrue, nextQuad())
            if (token.recognized_string == ")"):
                token = get_token()
                statements()
                genQuad(":=","1","_",flag)
                backpatch(conditionFalse, nextQuad())
                genQuad("=",1,flag,firstCondQuad)
            else: 
                error("closeParentheses") # ) expected
        else:
            error("openParentheses") # ( expected
    
def inputStat():
    global token
    idplace = ""
    token = get_token() # consume input
    if (token.recognized_string == "("):
        token = get_token()
        if (token.family == "id"):
            idplace = token.recognized_string
            token = get_token()
            if (token.recognized_string == ")"):
                genQuad("inp",idplace,"_","_")
                token = get_token()
            else:
                error("closeParentheses") # ) expected
        else:
            error("validId") # a valid id expected
    else:
        error("openParentheses") # ( expected

def muloperator():
    global token
    if (token.recognized_string == "*"):
        token = get_token()
    elif (token.recognized_string == "/"):
        token = get_token()
    else:
        error("mulOrDiv") # *, /

def optionalSign():
    global token
    global index
    if (token.recognized_string == "+" or token.recognized_string == "-"):
        addoperator()

def printStat():
    global token
    eplace = ""
    token = get_token() # consume print
    if (token.recognized_string == "("):
        token = get_token()
        eplace = expression()
        if (token.recognized_string == ")"):
            genQuad("out", eplace, "_", "_")
            token = get_token()
        else:
            error("closeParentheses") # ) expected
    else:
        error("openParentheses") # ( expected

def program():
    global token
    global main_name
    if (token.recognized_string == "program"):
        token = get_token()
        if (token.family == "id"):
            main_name = token.recognized_string
            addScope()
            token = get_token()
            block()
            if (token.recognized_string == "."):
                token = get_token()
                if (token.recognized_string == ""):
                    pass
                else:
                    error("eofExpected")
            else:
                error("dotExpected")
        else:
            error("validId")
    else:
        error("programKeywordNF")

def reloperator():
    global token
    relop = ""
    if (token.recognized_string == "="):
        relop = token.recognized_string
        token = get_token()
    elif (token.recognized_string == "<="):
        relop = token.recognized_string
        token = get_token()
    elif (token.recognized_string == ">="):
        relop = token.recognized_string
        token = get_token()
    elif (token.recognized_string == ">"):
        relop = token.recognized_string
        token = get_token()
    elif (token.recognized_string == "<"):
        relop = token.recognized_string
        token = get_token()
    elif (token.recognized_string == "<>"):
        relop = token.recognized_string
        token = get_token()
    else:
        error("relOpExpected") # =, <=, >=, >, <, <> expected
    return (relop)

def returnStat():
    global token
    global ret
    eplace = ""
    token = get_token() # consume return
    if (token.recognized_string == "("):
        token = get_token()
        eplace = expression()
        if (token.recognized_string == ")"):
            token = get_token()
            genQuad("retv", eplace, "_", "_")
            ret = True
        else:
            error("closeParentheses") # ) expected
    else:
        error("openParentheses") # ( expected

def statement():
    global token
    global index
    token = get_token()
    if (token.recognized_string == ":="):
        index -= 2
        token = get_token()
        assignStat()
    else:
        index -= 2
        token = get_token()
    if (token.recognized_string == "if"):
        ifStat()
    elif (token.recognized_string == "while"):
        whileStat()
    elif (token.recognized_string == "switchcase"):
        switchcaseStat()
    elif (token.recognized_string == "forcase"):
        forcaseStat()
    elif (token.recognized_string == "incase"):
        incaseStat()
    elif (token.recognized_string == "call"):
        callStat()
    elif (token.recognized_string == "return"):
        returnStat()
    elif (token.recognized_string == "input"):
        inputStat()
    elif (token.recognized_string == "print"):
        printStat()
    elif (token.recognized_string == "default"):
        token = get_token()
        statement()

def statements():
    global token
    if (token.recognized_string == "{"):
        token = get_token()
        statement()
        while (token.recognized_string == ";"):
            token = get_token()
            statement()
        if (token.recognized_string == "}"):
            token = get_token()
        else: 
            error("closeCurBracket") # } expected
    else:
        statement()
        if (token.recognized_string == ";"):
            token = get_token()
        else: 
            error("semicolonExpected") # ; expected

def subprogram():
    global token
    global label
    global ret
    id = ""
    if (token.recognized_string == "function"):
        token = get_token()
        if (token.family == "id"):
            id = token.recognized_string
            addEntity(id, "function", None)             
            token = get_token()
            if (token.recognized_string == "("):
                token = get_token()
                if (token.recognized_string == ")"):
                    token = get_token()
                    blockfuncproc(id)
                    if (ret == False):
                        print("Function has not return statement")
                        sys.exit(0)
                else:
                    error("closeParentheses") # ")" not found
            else:
                error("openParentheses") # "(" not found
        else: 
            error("invalidFuncName") # a valid function name is expected

    elif (token.recognized_string == "procedure"):
        token = get_token()
        if (token.family == "id"):
            id = token.recognized_string
            addEntity(id, "procedure", None)                
            token = get_token()
            if (token.recognized_string == "("):
                token = get_token()
                formalparlist()
                if (token.recognized_string == ")"):
                    token = get_token()
                    blockfuncproc(id)
                else:
                    error("closeParentheses") # ")" not found
            else:
                error("openParentheses") # "(" not found
        else: 
            error("invalidProcName") # a valid procedure name is expected

def subprograms():
    global token
    while (token.recognized_string == "function" or token.recognized_string == "procedure"):
        subprogram()

def switchcaseStat():
    global token
    conditionTrue = emptyList()
    conditionFalse = emptyList()
    exitList = emptyList()
    token = get_token() # consume switchcase
    while (token.recognized_string == "case"):
        token = get_token()
        if (token.recognized_string == "("):
            conditionTrue,conditionFalse = condition()       #here
            if (token.recognized_string == ")"):
                backpatch(conditionTrue, nextQuad())
                token = get_token()
                statements()
                t = makeList(nextQuad())
                genQuad("jump","_","_","_")
                exitList = mergeList(exitList, t)
                backpatch(conditionFalse, nextQuad())
            else: 
                error("closeParentheses") # ) expected
        else:
            error("openParentheses") # ( expected
    if (token.recognized_string == "default"):
        statements()
        backpatch(exitList, nextQuad())
    else:
        error("defaultNotFound") # you have to enter a default case

def term():
    global token
    global index
    f1place = ""
    f2place = ""
    eplace = ""
    f1place = factor()
    while (token.recognized_string == "*" or token.recognized_string == "/"):
        operator = token.recognized_string
        muloperator()
        f2place = factor()
        x = newTemp()
        genQuad(operator, f1place, f2place, x)
        f1place = x
        if (token.recognized_string == ")"):
            token = get_token()
            if (token.recognized_string == ";"):
                index -= 2
                token = get_token()
    eplace = f1place
    if (token.family == "keyword"):  # catch a case where after ")" we get a keyword, so we don"t skip token
        if (token.recognized_string != "and" and token.recognized_string != "or"):
            index -= 2
            token = get_token()
    return (eplace)

def varlist():
    global token
    global variables
    if (token.family == "id"):
        variables.append(token.recognized_string)
        addEntity(token.recognized_string, token.family, None)              
        token = get_token()
        while (token.recognized_string == ","):
            token = get_token()
            variables.append(token.recognized_string)
            addEntity(token.recognized_string, token.family, None)              
            if (token.family == "id"):
                token = get_token()
            else:
                error("validId") # id expected, something else came

def whileStat():
    global token
    conditionTrue = emptyList()
    conditionFalse = emptyList()
    condQuad = nextQuad()
    token = get_token() # consume while
    if (token.recognized_string == "("):
        conditionTrue, conditionFalse = condition()
        if (token.recognized_string == ")"):
            backpatch(conditionTrue, nextQuad())
            token = get_token()
            statements()
            genQuad("jump", "_", "_", condQuad)
            backpatch(conditionFalse, nextQuad())
        else:
            error("closeParentheses") # ) expected
    else:
        error("openParentheses") # ( expected


# Lexical Analyzer        
def lex():
    global line 
    global eof_flag
    char1 = "" 
    char2 = input_file.read(1)  
    if (char2 == ""):  
        eof_flag = True
        return (0, 0, 0)
    while (char2 == " " or char2 == "\n" or char2 == "\t"):       
        if (char2 == "\n"): 
            line = line + 1
        char2 = input_file.read(1)   
        if (char2 == ""):  
            eof_flag = True
            return (0, 0, 0)
    while (char2 == "#"):
        char1, char2, line = comment(char1,char2,line)
        while (char2 == " " or char2 == "\n" or char2 == "\t"): 
            if (char2 == "\n"):
                line = line + 1
            char2 = input_file.read(1) 
        if (char2 == ""): 
            eof_flag = True
    if (char2.isdigit()):  
        char1 = char2
        char2 = input_file.read(1) 
        while (char2.isdigit()): 
            char1 = char1 + char2
            char2 = input_file.read(1)  
        if (char2.isalpha()):  
            print ("Letter \"" + char2 + "\" directly after number \"" + str(char1) + "\" at line " + str(line))
            sys.exit(0)
        input_file.seek(input_file.tell() - 1)  
        if (int(char1) <= -4294967295 or int(char1) >= 4294967295):
            print ("Number is out of range at line " + str(line))
            sys.exit(0)
        return (char1, "number", line) 
    elif (char2.isalpha()): 
        letter_counter = 1
        char1 = char2
        char2 = input_file.read(1) 
        while (char2.isalpha() or char2.isdigit()):  
            letter_counter += 1  
            if (letter_counter <= 30): 
                char1 = char1 + char2
            else:                      
                print ("Identifier over characher limit at " + str(line) + ", use <= 30 characters ")
                sys.exit(0)
            char2 = input_file.read(1)  
        input_file.seek(input_file.tell() - 1) 
        if (char1 in keywords):  
            return (char1, "keyword", line) 
        else:
            return (char1, "id", line)    
    elif (char2 == "+" or char2 == "-"):
        char1 = char2
        return (char1, "addOperator", line)   
    elif (char2 == "*" or char2 == "/"):
        char1 = char2
        return (char1, "mulOperator", line)  
    elif (char2 == "{" or char2 == "}" or char2 == "[" or char2 == "]" or char2 == "(" or char2 == ")"):
        char1 = char2
        return (char1, "groupSymbol", line)  
    elif (char2 == "," or char2 == ";" or char2 == "."):
        char1 = char2
        return (char1, "delimiter", line) 
    elif (char2 == ":"):
        char1 = char2
        char2 = input_file.read(1)  
        if (char2 == "="):
            char1 = char1 + char2
            return (char1, "assignment", line) 
        else:  
            print ("= not found after :, for assignment use ':=', at line " + str(line)) 
            sys.exit(0)
    elif (char2 == "<"):
        char1 = char2
        char2 = input_file.read(1)   
        if (char2 == "=" or char2 == ">"):
            char1 = char1 + char2
            return (char1, "relOperator", line)   
        else:
            input_file.seek(input_file.tell() - 1)    
            return (char1, "relOperator", line)    
    elif (char2 == ">"):
        char1 = char2
        char2 = input_file.read(1) 
        if (char2 == "="):
            char1 = char1 + char2
            return (char1, "relOperator", line)  
        else:
            input_file.seek(input_file.tell() - 1)     
            return (char1, "relOperator", line)   
    elif (char2 == "="):
        char1 = char2
        return (char1, "relOperator", line)     
    else:
        print ("Invalid Character \"" + char2 + "\" at line " + str(line))
        sys.exit(0)

def comment(char1,char2,line):            
    char1 = char2
    char2 = input_file.read(1)  
    comment_line_start = line
    while (char2 != "#"):
        if (char2 == "\n"): 
            line = line + 1
        if (char2 == ""): 
            print ("Comment section not closed, comment starts at line " + str(comment_line_start))
            sys.exit(0)
        char2 = input_file.read(1)   
    if (char2 == "#"):
        char2 = input_file.read(1)  
    return (char1,char2,line)   


# Main Function
def main():
    while (not eof_flag):
        token = lex()                                                       
        new_token = Token(token[0],token[1],token[2]) 
        all_tokens.append(new_token) 
    all_tokens.pop() 
    syntax_analyzer()
    intercodeGen(sys.argv[1])
    cCodeGen(sys.argv[1])
    writeSymTable(sys.argv[1])
    writeRiscVAsm(sys.argv[1])


# Defining some global variables
if (__name__ == "__main__"):

    final = []
    paramFlag = False
    paramList = []

    depth = -1
    table = []
    symTable = []
    ret = False

    label = 0
    quadList = []
    tempCounter = 0
    variables = []
    main_name = ""
    fname = ""
    flag = False

    line = 1  
    all_tokens = []
    token = 0
    index = -1
    eof_flag = False
    keywords = {"program","declare","if","else","while","switchcase",       # keywords of Cimple language
                "forcase","incase","case","default","not","and","or",
                "function","procedure","call","return","in","inout",
                "input","print"}

    input_file = open(sys.argv[1],"r") 

    main() 
