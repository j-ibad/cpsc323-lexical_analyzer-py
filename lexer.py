#!/usr/bin/env python3

#Built-in libs
import sys
import re

SYMBOL_TABLE = {
    #Keywords
    "int": 1, "float":1, "bool":1, "True":1, "False":1,
    "if":1, "else":1, "then":1, "endif":1, "endelse":1,
    "while":1, "whileend":1, "do":1, "enddo":1, "for":1,
    "endfor":1, "STDinput":1, "STDoutput":1, "and":1, "or":1,
    "not":1,
    
    #Separators
    "(":3, ")":3, "{":3, "}":3, "[":3, "]":3, 
    ",":3, ".":3, ":":3, ";":3,
    
    #Operators
    "*":4, "+":4, "-":4, "=":4, 
    "/":4, ">":4, "<":4, "%":4
}
TOKEN_TABLE = {
    1: "KEYWORD",
    2: "IDENTIFIER",
    3: "SEPARATOR",
    4: "OPERATOR"
}


def numToToken(tokenPairs):
    for i in range(0, len(tokenPairs)):
        tokenPairs[i][0] = TOKEN_TABLE.get(tokenPairs[i][0])

def lexer(filename):
    #Open file
    try:
        file = open(filename, "r")
    except:
        print("%s cannot be opened" % filename)
        return [[-1,""]]

    #Init variables
    tokenPairs = []
    wordRegex = "^[a-zA-Z][a-zA-Z0-9_\$]+"

    #Traverse file line by line, char by char
    for line in file:
        print(line)
        ind = 0
        while ind < len(line):
            match = re.search(wordRegex, line[ind:])
            print(match)
            if match is None:
                if line[ind] == "!":    #Comment for rest of line
                    break
                elif line[ind] == " ":  #Ignore space
                    ind += 1
                    continue
                else:
                    token = SYMBOL_TABLE.get(line[ind])
                    if token is None:
                        print("Not exp: %s" % line[ind])
                    else:
                        tokenPairs.append( [token, line[ind]] )
                ind += 1
                #No matches found
            else:
                while ind < match.span()[0] + ind:
                    print("Not exp: %s" % line[ind])
                    ind += 1
                    #Detect operators and separators
                
                #Detect indentifiers
                token = SYMBOL_TABLE.get(match.group())
                print("%s is %s" % (match.group(), token))
                if token is None:
                    tokenPairs.append( [2, match.group()] )
                else:
                    tokenPairs.append( [token, match.group()] )
                
                ind = match.span()[1] + ind;
            
    #Convert nums tokens to string tokens
    #REMOVE IN FUTURE PROJECTS
    numToToken(tokenPairs)
    
    #Return
    return tokenPairs



def main():
    #Accept filename input from command line or prompt
    filename = ""
    if len(sys.argv) <= 1:
        filename = input("Input filename: ")
    else:
        filename = sys.argv[1]
    
    #Run lexical analysis function "lexer()"
    tokens = lexer(filename)
    
    #Print tokens
    print("%-16s\t%s\n" % ("TOKENS", "Lexemes"))
    for token, lexeme in tokens:
        print("%-16s=\t%s" % (token, lexeme))
    
    return tokens


if __name__ == "__main__":
    main()
