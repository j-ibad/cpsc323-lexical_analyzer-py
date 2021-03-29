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


class TreeNode:
    def __init__(self, val):
        self.val = val
        self.children = []
        
        
    def addChild(self, child, index=None):
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
        
        
    def printSubtree(self, level, spacer=""):
        print(spacer + '["%s"\theight: %d, ' % (self.val, level) + "Children: {")
        for child in self.children:
            if isinstance(child, TreeNode):
                child.printSubtree(level+1, spacer + " ")
            else:
                print(spacer, end=" ")
                print(child)
        print(spacer + "} End of (%s, %d)]" % (self.val, level))


class Parser:
    def __init__(self, fIn, fOut):
        self.index = 0
        self.filename = fIn
        self.tokens = lexer.lexer(fIn)
        #print(self.tokens)
        self.token = None
        #PARSE TREE VARIABLES
        self.parseTreeRoot = self.statementList()
        
        print("\nPrinting Parse Tree:\n")
        self.parseTreeRoot.printSubtree(0)
        
        
    def nextToken(self):
        if self.index >= len(self.tokens):
            #No more tokens error
            self.printError("Unexpected end of file. Expected more tokens.")
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
            
            
    def printError(self, errorMsg):
        print("%s:%d:%d: Error: %s" % (self.filename, self.token[2][0], self.token[2][1], errorMsg))
        exit()
        
        
    def printUnexpectedError(self, errorMsg, errorType="Error"):
        print('%s:%d:%d: %s: Unexpected %s token "%s". %s' % (self.filename, self.token[2][0], self.token[2][1], errorType, self.token[0], self.token[1], errorMsg))
        exit()
        
        
    def statementList(self, ending=None):
        subRoot = None
        currNode = None
    
        if isinstance(ending, list):
            while (self.peekToken() is not None) and (self.peekToken()[1] not in ending):
                #Create new Tree Node for SL
                nxtNode = TreeNode('SL')
                if subRoot is None:
                    currNode = nxtNode
                    subRoot = currNode
                else:
                    currNode.addChild(nxtNode)  #Adds SL as child of parent
                    currNode = nxtNode
                    
                print("\n\t<StatementList> -> <Statement> <StatementList> | <empty>")
                currNode.addChild( self.statement() )
                if (self.peekToken() is not None) and (self.peekToken()[1] == ';'):
                    self.nextToken()
                    currNode.addChild( self.token )
        elif isinstance(ending, str):
            while (self.peekToken() is not None) and (self.peekToken()[1] != ending):
                #Create new Tree Node for SL
                nxtNode = TreeNode('SL')
                if subRoot is None:
                    currNode = nxtNode
                    subRoot = currNode
                else:
                    currNode.addChild(nxtNode)  #Adds SL as child of parent
                    currNode = nxtNode
                
                print("\n\t<StatementList> -> <Statement> <StatementList> | <empty>")
                currNode.addChild( self.statement() )
                if (self.peekToken() is not None) and (self.peekToken()[1] == ';'):
                    self.nextToken()
                    currNode.addChild( self.token )
        else:
            while self.peekToken() is not None:
                #Create new Tree Node for SL
                nxtNode = TreeNode('SL')
                if subRoot is None:
                    currNode = nxtNode
                    subRoot = currNode
                else:
                    currNode.addChild(nxtNode)  #Adds SL as child of parent
                    currNode = nxtNode
                
                print("\n\t<StatementList> -> <Statement> <StatementList> | <empty>")
                currNode.addChild( self.statement() )
                if (self.peekToken() is not None) and (self.peekToken()[1] == ';'):
                    self.nextToken()
                    currNode.addChild( self.token )
        return subRoot
    
    
    def statement(self):
        currNode = TreeNode("S")
        self.nextToken()
        #Assignment and Declarations
        if self.token[1] == "begin":
            print("\t<Statement> -> begin <StatementList> end")
            currNode.addChild( self.token )
            currNode.addChild( self.statementList("end") )
            if self.peekToken() is not None and self.peekToken()[1] == "end":
                self.nextToken()
                currNode.addChild( self.token )
            else: #ERROR:   Needs "end"
                self.printError('Expected keyword "end" after statement-list')
        elif self.token[0] == "IDENTIFIER":
            print("\t<Statement> -> <Assign>")
            tmpToken = self.token
            tmpNode = self.assign()
            tmpNode.addChild( tmpToken, 0 )
            currNode.addChild(tmpNode)
        elif self.token[1] in types:
            print("\t<Statement> -> <Declarative>")
            tmpToken = self.token
            tmpNode = self.declarative()
            tmpNode.addChild( tmpToken, 0 )
            currNode.addChild(tmpNode)
        #Control structures
        elif self.token[1] == "if":
            currNode.addChild( self.token )
            print("\t<Statement> -> if <Conditional> then <Statement> else <Statement> endif")
            currNode.addChild( self.conditional() )
            if self.peekToken() is not None and self.peekToken()[1] == "then":
                self.nextToken()
                currNode.addChild( self.token )
                currNode.addChild( self.statementList(["else", "endif"]) )
                if self.peekToken() is not None and self.peekToken()[1] == "else":
                    self.nextToken()
                    currNode.addChild( self.token )
                    currNode.addChild( self.statementList("endif") )
                if self.peekToken() is not None and self.peekToken()[1] == "endif":
                    self.nextToken()
                    currNode.addChild( self.token )
                else:   #ERROR: Needs endif
                    self.printError('Expected keyword "endif" after statement-list')
            else: #ERROR: Needs "then"
                self.printError('Expected keyword "then" before statement-list')
        elif self.token[1] == "while":
            currNode.addChild( self.token )
            print("\t<Statement> -> while <Conditional> do <Statement> whileend")
            currNode.addChild( self.conditional() )
            if self.peekToken() is not None and self.peekToken()[1] == "do":
                self.nextToken()
                currNode.addChild( self.token )
                currNode.addChild( self.statementList('whileend') )
                if self.peekToken() is not None and self.peekToken()[1] == 'whileend':
                    self.nextToken()
                    currNode.addChild( self.token )
                else:   #ERROR: Needs "whileend"
                    self.printError('Expected keyword "whileend" after statement-list')
            else:   #ERROR: should have "do"
                self.printError('Expected keyword "do" before statement-list')
        else:   #ERROR: Next token does not form a statement
            self.printUnexpectedError(' Was expecting a statement.')
        return currNode
        
    def assign(self):
        currNode = TreeNode("A")
        self.nextToken()
        if self.token[1] == "=":
            print("\t<Assign> -> <ID> = <Expression>;")
            currNode.addChild( self.token )
            currNode.addChild( self.expression() )
        else: #ERROR: Expecting "=" for assignment statement.
            self.printUnexpectedError('Was expecting operator "=" for assignment statement')
        return currNode


    #EXTRA: How about declarative assignments? "int x=1;"
    def declarative(self):
        subRoot = TreeNode("D")
        self.nextToken() #ID
        subRoot.addChild( self.token )
        currNode = subRoot
        print("\t<Declarative> -> <Type> <ID> <MoreIds>; | <empty>")
        while self.peekToken() is not None and self.peekToken()[1] == ',':
            tmpNode = TreeNode("MI")
            self.nextToken()
            tmpNode.addChild( self.token )
            if self.peekToken() is not None and (self.peekToken()[0] != "IDENTIFIER"): #ERROR: Invalid multiple declarative statement
                self.nextToken()
                self.printUnexpectedError('Was expecting an IDENTIFIER token for more declarations')
            print("\t<MoreIds> -> , <ID> <MoreIds> | <empty>")
            self.nextToken()
            tmpNode.addChild( self.token )
            currNode.addChild( tmpNode )
            currNode = tmpNode
        currNode.addChild( "<empty>" )
        return subRoot
        
        
    def expression(self):
        currNode = TreeNode("E")
        print("\t<Expression> -> <Term> | <Term> + <Expression> | <Term> - <Expression>")
        currNode.addChild( self.term() )
        tmpTok = self.peekToken()
        if tmpTok is not None and tmpTok[1] in ['+', '-']:
            self.nextToken()
            currNode.addChild( self.token )
            currNode.addChild( self.expression() )
        return currNode
        
        
    def term(self):
        currNode = TreeNode("T")
        print("\t<Term> -> <Term> * <Factor> | <Term> / <Factor> | <Factor>")
        currNode.addChild( self.factor() )
        tmpTok = self.peekToken()
        if tmpTok is not None and tmpTok[1] in ['*', '/']:
            self.nextToken()
            currNode.addChild( self.token )
            currNode.addChild( self.term() )
        return currNode
    
    
    def factor(self):
        currNode = TreeNode("F")
        self.nextToken()
        currNode.addChild( self.token )
        print("\t<Factor> -> ( <Expression> ) | <ID> | <num>")
        if self.token[1] == '(':
            currNode.addChild( self.expression() )
            self.nextToken()
            currNode.addChild( self.token )
            if self.token[1] != ')': #ERROR: Expected ')' after expression
                self.printUnexpectedError("Expected SEPARATOR ')' after expression")
        elif self.token[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT'] or self.token[1] in ['True', 'False']:
            return currNode #IS VALID. Return to go back to callee function
        else:   #ERROR: Not a valid Factor.
            self.printUnexpectedError("Expected a Factor in the form of ( <Expression> ), or an IDENTIFIER, or NUMERIC token", "Error: Invalid Factor")
        return currNode
        
    #EXTRA: <Conditional> -> ( <Conditional> )
    def conditional(self):
        currNode = TreeNode("C")
        print("\t<Conditional> -> <Expression> <Relop> <Expression> | <Expression>")
        currNode.addChild( self.expression() )
        tmpTok = self.peekToken()
        if tmpTok is not None:
            if tmpTok[1] == "<":
                self.nextToken()
                currNode.addChild( self.token )
                tmpTok2 = self.peekToken()
                if tmpTok2 is not None and tmpTok2[1] in ['=', '>']:
                    self.nextToken() #Eval as "<=" or "<>"
                    currNode.addChild( self.token )
                currNode.addChild( self.expression() ) #Eval as "<"
            elif tmpTok[1] == ">":
                self.nextToken()
                currNode.addChild( self.token )
                tmpTok2 = self.peekToken()
                if tmpTok2 is not None and tmpTok2[1] == "=":
                    self.nextToken() # Eval as >=
                    currNode.addChild( self.token )
                currNode.addChild( self.expression() ) #Eval as >
            elif tmpTok[1] == "=":
                self.nextToken()
                currNode.addChild( self.token )
                tmpTok2 = self.peekToken()
                if tmpTok2 is not None:
                    if tmpTok2[1] == '=':
                        self.nextToken()
                        currNode.addChild( self.token )
                        currNode.addChild( self.expression() )#Eval as ==
                    else:   #Eval as assignment, counted as invalid
                        self.printUnexpectedError("Expected RELATIVE OPERATOR between expressions. Did you mean '=='?")
        #OTHERWISE just a lone expression. (Valid)
        return currNode
        
            
        

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
