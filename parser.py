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
            while (self.peekToken() is not None) or (self.peekToken() not in ending):
                print("\t<StatementList> -> <Statement> <StatementList> | <empty>")
                self.statement()
        elif isinstance(ending, str):
            while (self.peekToken() is not None) or (self.peekToken() != ending):
                print("\t<StatementList> -> <Statement> <StatementList> | <empty>")
                self.statement()
        else:
            while self.peekToken() is not None:
                print("\t<StatementList> -> <Statement> <StatementList> | <empty>")
                self.statement()
            return
    
    def statement(self):
        self.nextToken()
        if self.token[0] == "IDENTIFIER":
            print("\t<Statement> -> <Assign>")
            self.assign()
        elif self.token[1] in types:
            print("\t<Statement> -> <Declarative>")
            self.declarative()
        elif self.token[1] == "if":
            print("\t if <Conditional> then <Statement> else <Statement> endif")
            self.conditional()
            if self.peekToken() is not None and self.peekToken()[1] == "then":
                self.nextToken()
                self.statement()
                if self.peekToken() is not None and self.peekToken()[1] == "else":
                    self.nextToken()
                    self.statement()
                if self.peekToken() is not None and self.peekToken()[1] == "endif":
                    self.nextToken
                else:
                    #ERROR: should have endif
                    return
            else:
                '''Does it need to have then? is this an error?'''
                return
        elif self.token[1] == "while":
            print("\t while <Conditional> do <Statement> whileend")
            self.conditional()
            if self.peekToken() is not None and self.peekToken()[1] == "do":
                self.nextToken()
                self.statement()
                if self.peekToken() is not None and self.peekToken()[1] == "whileend":
                    self.nextToken()
                else:
                    #ERROR should have "whileend"
                    return
            else:
                #ERROR, should have "do"
                return
        elif self.token[1] == "begin":
            print("\t <Statement> -> begin <StatementList> end")
            self.statementList("end")
            if self.peekToken() is not None and self.peekToken()[1] == "end":
                self.nextToken()
            else:
                #ERROR: Should end with "end"
                return
        else:
            #ERROR
            return
            
    def assign(self):
        self.nextToken()
        if self.token[1] == "=":
            print("\t<Assign> -> <ID> = <Expression>;")
            self.expression()
        else:
            #ERROR
            return
        
        
    #EXTRA: How about declarative assignments? "int x=1;"
    def declarative(self):
        self.nextToken() #ID
        print("\t<Declarative> -> <Type> <ID> <MoreIds>; | <empty>")
        while self.peekToken() is not None and self.peekToken()[1] == ',' and self.peekToken()[1] != ";":
            self.nextToken()
            if self.peekToken() is not None and self.peekToken()[0] != "IDENTIFIER":
                #ERROR
                return
            self.nextToken()
            print("\t<MoreIds> -> , <ID> <MoreIds> | <empty>")
        
    def expression(self):
        self.nextToken()
        print("\t<Expression> -> <Term> | <Term> + <Expression> | <Term> - <Expression>")
        self.term()
        if self.token is not None and self.token[1] in ['+', '-']:
            self.expression()
        
    def term(self):
        self.nextToken()
        print("\t<Term> -> <Term> * <Factor> | <Term> / <Factor> | <Factor>")
        self.factor()
        if self.token is not None and self.token[1] in ['*', '/']:
            self.term();
    
    def factor(self):
        self.nextToken()
        print("\t<Factor> -> ( <Expression> ) | <ID> | <num>")
        if self.token[1] == '(':
            self.expression()
            self.nextToken()
            if self.token[1] != ')':
                #ERROR
                return
        elif self.token[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT']:
            #valid
            return
        else:
            #ERROR
            return
            
    #EXTRA: <Conditional> -> ( <Conditional> )
    def conditional(self):
        self.expression()
        print("\t<Conditional> -> <Expression> <Relop> <Expression> | <Expression>")
        tmpTok = self.peekToken()
        if tmpTok is not None:
            tmpTok2 = self.peekToken()
            if tmpTok[0] == "<":
                self.nextToken()
                if tmpTok2 is not None and tmpTok2 in ['=', '>']:
                    self.nextToken() #Eval as "<=" or "<>"
                self.expression() #Eval as "<"
            elif tmpTok[0] == ">":
                self.nextToken()
                if tmpTok2 is not None and tmpTok2 == "=":
                    self.nextToken() # Eval as >=
                self.expression #Eval as >
            elif tmpTok[0] == "=":
                self.nextToken()
                if tmpTok2 is not None and tmpTok2 == '=':
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
