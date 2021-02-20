# cpsc323-lexical_analyzer-py
A lexical analyzer for a simple C-like language implemented in python. Done as HW 1 for CPSC 323 - Compilers and Languages

Please make sure all necessary files are in the same directory.
• lexer.py
• main.py
• sample_input.txt
• simple_dec_in.txt
• Any file that you would like to input to the lexer script.
To execute this program, all you will need to do is open and run “lexer.py” by using the terminal since we are using Python 3.
The filename may be input as a command line argument upon executing the script, such as executing “python lexer.py <FILENAME>” on command prompt, “python3 lexer.py <FILENAME>” on a Linux CLI. If no filename is fed as a command line argument, the terminal will prompt the user for a “Filename”, where you input a text file name that contains some source code for the program to analyze.
When inputting filenames, the user must make sure to have the file in the current working directory. Otherwise, the user will have to input a path to the file.
Lastly, the output of the program will be divided into list of “Tokens” and “Lexemes”.