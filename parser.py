#!/usr/bin/env python3

import lexer
import sys
import re

'''
<Statement> -> <Declarative>
<Statement> -> <Assign>
...
<Declarative> -> <Type> <id>
...
<Type> -> {"int", "float", "bool"}

<Assign> -> <ID> = <Expression>
...
<Expression> -> <Expression> + <Term> | <Expression> - <Term> | <Term>
<Expression> -> <Term> | <Term> + <Expression> | <Term> - <Expression>
<Term> -> <Term> * <Factor> | <Term> / <Factor> | <Factor>

...


...
<Statement> -> if <Conditional> then <StatementList> else <Statement> endif
    |   while <Conditional> do <StatementList> whileend
    |   begin <StatementList> end
    
<Conditional> -> <Expression> <Relop> <Expression> | <Expression>
'''

types = ["int", "float", "bool"]
relop = ['<', '<=', '==', '<>', '>=', '>']

class Parser:
    def __init__(self, fIn, fOut):
        self.index = 0
        self.tokens = lexer.lexer(fIn)
        #print(self.tokens)
        self.token = None
        self.statementList()
        
    def nextToken(self):
        if self.index >= len(self.tokens):
            #No more tokens error
            exit()
        self.token = self.tokens[self.index]
        #Write token
        print("Token:\t%-16s Lexeme:\t%s" % (self.token[0], self.token[1]))
        self.index += 1
        
    def peekToken(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        else:
            return None
        
    def statementList(self, ending=None):
        if isinstance(ending, list):
            while (self.peekToken() is not None) and (self.peekToken()[1] not in ending):
                print("\n\t<StatementList> -> <Statement> <StatementList> | <empty>")
                self.statement()
                if (self.peekToken() is not None) and (self.peekToken()[1] == ';'):
                    self.nextToken()
                    continue
        elif isinstance(ending, str):
            while (self.peekToken() is not None) and (self.peekToken()[1] != ending):
                print("\n\t<StatementList> -> <Statement> <StatementList> | <empty>")
                self.statement()
                if (self.peekToken() is not None) and (self.peekToken()[1] == ';'):
                    self.nextToken()
                    continue
        else:
            while self.peekToken() is not None:
                print("\n\t<StatementList> -> <Statement> <StatementList> | <empty>")
                self.statement()
                if (self.peekToken() is not None) and (self.peekToken()[1] == ';'):
                    self.nextToken()
                    continue
            return
    
    def statement(self):
        self.nextToken()
        #Assignment and Declarations
        if self.token[1] == "begin":
            print("\t<Statement> -> begin <StatementList> end")
            self.statementList("end")
            if self.peekToken() is not None and self.peekToken()[1] == "end":
                self.nextToken()
            else:
                #ERROR: Should end with "end"
                exit()
                return
        elif self.token[0] == "IDENTIFIER":
            print("\t<Statement> -> <Assign>")
            self.assign()
        elif self.token[1] in types:
            print("\t<Statement> -> <Declarative>")
            self.declarative()
        #Control structures
        elif self.token[1] == "if":
            print("\t<Statement> -> if <Conditional> then <Statement> else <Statement> endif")
            self.conditional()
            if self.peekToken() is not None and self.peekToken()[1] == "then":
                self.nextToken()
                self.statementList(["else", "endif"])
                if self.peekToken() is not None and self.peekToken()[1] == "else":
                    self.nextToken()
                    self.statementList("endif")
                if self.peekToken()[1] == "endif":
                    self.nextToken()
                else:
                    #ERROR: Needs endif
                    exit()
                    return
            else:
                '''Does it need to have then? is this an error?'''
                return
        elif self.token[1] == "while":
            print("\t<Statement> -> while <Conditional> do <Statement> whileend")
            self.conditional()
            if self.peekToken() is not None and self.peekToken()[1] == "do":
                self.nextToken()
                self.statementList('whileend')
                if self.peekToken()[1] == 'whileend':
                    self.nextToken()
                else:
                    #ERROR: Needs "whileend"
                    exit()
                    return
                '''self.statement()
                if self.peekToken() is not None and self.peekToken()[1] == "whileend":
                    self.nextToken()
                else:
                    #ERROR should have "whileend"
                    exit()
                    return'''
            else:
                #ERROR, should have "do"
                exit()
                return
        
        else:
            #ERROR
            exit()
            return
            
    def assign(self):
        self.nextToken()
        if self.token[1] == "=":
            print("\t<Assign> -> <ID> = <Expression>;")
            self.expression()
        else:
            #ERROR
            exit()
            return

    #EXTRA: How about declarative assignments? "int x=1;"
    def declarative(self):
        self.nextToken() #ID
        print("\t<Declarative> -> <Type> <ID> <MoreIds>; | <empty>")
        while self.peekToken() is not None and self.peekToken()[1] == ',' and self.peekToken()[1] != ";":
            self.nextToken()
            if self.peekToken() is not None and (self.peekToken()[1] not in types): #or self.peekToken()[0] == "IDENTIFIER" #To allow int x, y;
                #TRUE ERROR
                exit()
                return
            print("\t<MoreIds> -> , <ID> <MoreIds> | <empty>")
            self.nextToken()
            self.nextToken()
        
    def expression(self):
        print("\t<Expression> -> <Term> | <Term> + <Expression> | <Term> - <Expression>")
        self.term()
        tmpTok = self.peekToken()
        if tmpTok is not None and tmpTok[1] in ['+', '-']:
            self.nextToken()
            self.expression()
        
    def term(self):
        print("\t<Term> -> <Term> * <Factor> | <Term> / <Factor> | <Factor>")
        self.factor()
        tmpTok = self.peekToken()
        if tmpTok is not None and tmpTok[1] in ['*', '/']:
            self.nextToken()
            self.term();
    
    def factor(self):
        self.nextToken()
        print("\t<Factor> -> ( <Expression> ) | <ID> | <num>")
        if self.token[1] == '(':
            self.expression()
            self.nextToken()
            if self.token[1] != ')':
                #ERROR
                exit()
                return
        elif self.token[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT'] or self.token[1] in ['True', 'False']:
            #valid
            #print( self.token[0] )
            return
        else:
            #ERROR
            exit()
            return
            
    #EXTRA: <Conditional> -> ( <Conditional> )
    def conditional(self):
        print("\t<Conditional> -> <Expression> <Relop> <Expression> | <Expression>")
        self.expression()
        tmpTok = self.peekToken()
        if tmpTok is not None:
            if tmpTok[1] == "<":
                self.nextToken()
                tmpTok2 = self.peekToken()
                if tmpTok2 is not None and tmpTok2[1] in ['=', '>']:
                    self.nextToken() #Eval as "<=" or "<>"
                self.expression() #Eval as "<"
            elif tmpTok[1] == ">":
                self.nextToken()
                tmpTok2 = self.peekToken()
                if tmpTok2 is not None and tmpTok2[1] == "=":
                    self.nextToken() # Eval as >=
                self.expression() #Eval as >
            elif tmpTok[1] == "=":
                self.nextToken()
                tmpTok2 = self.peekToken()
                if tmpTok2 is not None and tmpTok2[1] == '=':
                    self.nextToken()
                    self.expression() #Eval as ==
            #Potential error here ? ? ?
        
            
        

def main():
    #Accept filename input from command line or prompt
    filename = ""
    if len(sys.argv) <= 1:  #Prompt user for file name
        filename = input("Input filename: ")
    else:   #Accept argument from command line
        filename = sys.argv[1]
    
    #Run lexical analysis function "lexer()"
    parseTree = Parser(filename, None)
    '''
    #Print tokens
    print("%-16s\t%s\n" % ("TOKENS", "Lexemes"))
    for token, lexeme in tokens:
        print("%-16s=\t%s" % (token, lexeme))'''
    
    #Return tokens
    #return

#Execute main function only when directly executing script
if __name__ == "__main__":
    main()
