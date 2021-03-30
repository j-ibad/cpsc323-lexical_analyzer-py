#!/usr/bin/env python3
'''
Project Name: Project 2 - Syntax Analyzer
Class:  CPSC 323 - 02, Spring 2021
Professor:  Prof. Anthony Le
Authors:    Winnie Pan
            Josh Ibad
            Titus Sudarno
            Thomas-James Le

'''


import lexer
import sys
import re

'''
Some grammars:
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

#List of types recognized by compiler
types = ["int", "float", "bool"]


''' TreeNode class
TreeNode class, for representing non-leaf nodes for the internal Parse Tree.
The internal Parse Tree uses the TreeNode clas for non-leaf nodes, storing the
type of the non-terminal expression, along with an adjacency list of its
children. Leaf nodes are simply stored as tokens.
'''
class TreeNode:
    '''Constructor:
    Creates an internal, non-leaf node for the ParseTree storing the non-terminal
    expression, and instantiates an empty adjacency list of its children.
        @param val - Non-terminal expression of node
    '''
    def __init__(self, val):
        self.val = val
        self.children = []
    
    
    '''
    Adds a child to the adjacency list of the TreeNode. By default, adds the
    new child to the tail of the list.
        @param child - Child of TreeNode to be added to the adjacency list
        @param index - Index at list in which to add child. Defaults to tail
    '''
    def addChild(self, child, index=None):
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
        
    '''
    Prints the subtree recursively, in preorder fashion. First prints the type
    of the current node, then prints its children. If the child is a non-leaf
    node, then the function is called recursively on the non-leaf TreeNode. If
    the child is a leaf node, the token is simply printed. Printing keeps track
    of the level of the tree, and formats the output with the spacer.
        @param level - Current height of the tree. Defaults to 0 for root
        @param spacer - String to prepend to all print statements for spacing
    '''
    def printSubtree(self, level=0, spacer=""):
        print(spacer + '["%s"\theight: %d, ' % (self.val, level) + "Children: {")
        for child in self.children:
            if isinstance(child, TreeNode):
                child.printSubtree(level+1, spacer + " ")
            else:
                print(spacer, end=" ")
                print(child)
        print(spacer + "} End of (%s, %d)]" % (self.val, level))


''' Parser Class
Class for parsing a file and performing syntax analysis. The class internally
calls a lexer on the input file. The resultant token-lexeme list is then passed
to the Parser for Syntax Analysis, using the Recursive Descent Parser method.
The Parser prints tokens along with production grammar rules matched to them.
After the whole file is analyzed, the resultant parse tree is also printed.
'''
class Parser:
    # Constructor
    #   Runs the lexer to analyze the input file. Then, performs syntax analysis
    #   on the tokens received, outputting to the output file.
    #   Generates a parse tree.
    def __init__(self, fIn, fOut):
        self.index = 0
        self.filename = fIn
        self.tokens = lexer.lexer(fIn)
        #print(self.tokens)
        self.token = None
        #PARSE TREE VARIABLES
        self.parseTreeRoot = self.statementList()
        
        print("\nPrinting Parse Tree:\n")
        self.parseTreeRoot.printSubtree()
    
    
    # Iterates to the next token in the list, printing it to output.
    #   If no more tokens to iterate over, an error is printed.
    def nextToken(self):
        if self.index >= len(self.tokens):
            #No more tokens error
            self.printError("Unexpected end of file. Expected more tokens.")
        self.token = self.tokens[self.index]
        #Write token
        print("Token:\t%-16s Lexeme:\t%s" % (self.token[0], self.token[1]))
        self.index += 1
    
    
    # Peeks at the next token if one exists. Otherwise, None is returned
    def peekToken(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        else:
            return None
    
    
    # Removes the next token from the token list, and sets it as current token.
    #   Used for removing tokens which are appended to others when reinterpretted.
    def popNextToken(self):
        if self.index < len(self.tokens):
            self.token = self.tokens.pop(self.index)
            #Write token
            print("Token:\t%-16s Lexeme:\t%s" % (self.token[0], self.token[1]))
            return self.token
        else:
            self.printError("Unexpected end of file. Expected more tokens.")
    

    # Prints an error message
    def printError(self, errorMsg):
        print("%s:%d:%d: Error: %s" % (self.filename, self.token[2][0], self.token[2][1], errorMsg))
        exit()
    
    
    # Special error that prints the unexpected token along with the error message
    def printUnexpectedError(self, errorMsg, errorType="Error"):
        print('%s:%d:%d: %s: Unexpected %s token "%s". %s' % (self.filename, self.token[2][0], self.token[2][1], errorType, self.token[0], self.token[1], errorMsg))
        exit()
    
    
    # Expression
    #   Production rules: <StatementList> -> <Statement> <StatementList> | <empty>
    #   Represented in parse tree as non-leaf node with value "SL"
    # The root of the parse tree is a statement list
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
    
    
    # Statement
    #   Production rules:   <Statement> -> <Assign> | <Declarative> | begin <StatementList> end
    #                           if <Conditional> then <StatementList> else <StatementList> endif |
    #                           if <Conditional> then <StatementList> endif | 
    #                           while <Conditional> do <StatementList> whileend | begin <StatementList> end
    #   Represented in parse tree as non-leaf node with value "S"
    def statement(self):
        currNode = TreeNode("S")
        self.nextToken()
        if self.token[1] == "begin":
            print("\t<Statement> -> begin <StatementList> end")
            currNode.addChild( self.token )
            currNode.addChild( self.statementList("end") )
            if self.peekToken() is not None and self.peekToken()[1] == "end":
                self.nextToken()
                currNode.addChild( self.token )
            else: #ERROR:   Needs "end"
                self.printError('Expected keyword "end" after statement-list')
        #Assignment and Declarations
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
            print("\t<Statement> -> if <Conditional> then <StatementList> endif | if <Conditional> then <StatementList> else <StatementList> endif")
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
            print("\t<Statement> -> while <Conditional> do <StatementList> whileend")
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
    
    
    # Assign
    #   Production rules: <Assign> -> <ID> = <Expression>;
    #   Represented in parse tree as non-leaf node with value "A"    
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


    # Declarative
    #   Production rules:   <Declarative> -> <Type> <ID> <MoreIds>; | <empty>
    #                       <MoreIds> -> , <ID> <MoreIds> | <empty
    #   Represented in parse tree as non-leaf node with value "D"
    #   MoreIDs are represented as "MI"
    #TODO: EXTRA: How about declarative assignments? "int x=1;"
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
        
    
    # Expression
    #   Production rules: <Expression> -> <Term> | <Term> + <Expression> | <Term> - <Expression>
    #   Represented in parse tree as non-leaf node with value "E"
    # Note: Removal of left recursion is not performed. Rather, the grammar is flipped to not have
    #   left recursion. This will be handled later by the object code generator.
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

        
    # Term:
    #   Production rules: <Term> -> <Term> * <Factor> | <Term> / <Factor> | <Factor>
    #   Represented in parse tree as non-leaf node with value "T"
    # Note: Removal of left recursion is not performed. Rather, the grammar is flipped to not have
    #   left recursion. This will be handled later by the object code generator.
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
    
    
    # Factor:
    #   Production rules: <Factor> -> '(' <Expression> ')' | <ID> | ('+' | '-')?(<FLOAT> | ('.')?<INT>)
    #   Represented in parse tree as non-leaf node with value "F"
    # Note: Additional processing of numbers are performed here to recognize all forms of numericals
    def factor(self):
        currNode = TreeNode("F")
        self.nextToken()
        currNode.addChild( self.token )
        print("\t<Factor> -> '(' <Expression> ')' | <ID> | ('+' | '-')?(<FLOAT> | ('.')?<INT>)")
        if self.token[1] == '(':
            currNode.addChild( self.expression() )
            self.nextToken()
            currNode.addChild( self.token )
            if self.token[1] != ')': #ERROR: Expected ')' after expression
                self.printUnexpectedError("Expected SEPARATOR ')' after expression")
        elif self.token[0] in ['IDENTIFIER', 'INTEGER', 'FLOAT'] or self.token[1] in ['True', 'False']:
            return currNode #IS VALID. Return to go back to callee function
        elif self.token[1] in ['+', '-']: #Treat as part of number
            tmpTok = self.popNextToken()
            if tmpTok[1] == '.':
                tmpTok2 = self.popNextToken()
                if tmpTok2[0] == 'INTEGER':
                    self.tokens[self.index-1][1] =  self.tokens[self.index-1][1] + tmpTok[1] + tmpTok2[1]#Append to front of number
                    self.tokens[self.index-1][0] = 'FLOAT'
                else:
                    self.printUnexpectedError("Expected float.")
            elif tmpTok[0] in ['INTEGER', 'FLOAT']:
                self.tokens[self.index-1][1] =  self.tokens[self.index-1][1] + tmpTok[1] #Append to front of number
                self.tokens[self.index-1][0] = tmpTok[0]
            else:
                self.printUnexpectedError("Expected numerical token.")
            #self.printUnexpectedError("Expected a Factor in the form of ( <Expression> ), or an IDENTIFIER, or NUMERIC token", "Error: Invalid Factor")
        elif self.token[1] == '.':
            tmpTok = self.popNextToken()
            if tmpTok[0] == 'INTEGER':
                self.tokens[self.index-1][1] =  self.tokens[self.index-1][1] + tmpTok[1]#Append to front of number
                self.tokens[self.index-1][0] = 'FLOAT'
            else:
                self.printUnexpectedError("Expected float.")
        else:   #ERROR: Not a valid Factor.
            self.printUnexpectedError("Expected a Factor in the form of ( <Expression> ), or an IDENTIFIER, or NUMERIC token", "Error: Invalid Factor")
        return currNode
        
        
    # Conditional
    #   Production rules: <Conditional> -> <Expression> <Relop> <Expression> | <Expression>
    #   Represented in parse tree as non-leaf node with value "C"
    #TODO: EXTRA: <Conditional> -> ( <Conditional> )
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
