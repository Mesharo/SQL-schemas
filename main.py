from antlr4 import *
from antlr4_postgresql.PostgreSQLLexer import PostgreSQLLexer
from antlr4_postgresql.PostgreSQLParser import PostgreSQLParser

if __name__ == "__main__":
    input_text = input("> ")
    lexer = PostgreSQLLexer(InputStream(input_text))
    stream = CommonTokenStream(lexer)
    parser = PostgreSQLParser(stream)

    tree = parser.r()

    print(tree.toStringTree(recog=parser))

"""
warning(146): PostgreSQLLexer.g4:1652:0: non-fragment lexer rule AfterEscapeStringConstantMode_NotContinued can
match the empty string
warning(146): PostgreSQLLexer.g4:1668:0: non-fragment lexer rule AfterEscapeStringConstantWithNewlineMode_NotContinued
can match the empty string
"""