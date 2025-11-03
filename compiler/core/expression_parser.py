"""
A robust expression parser using the Sly library.
It tokenizes an expression string and builds an Abstract Syntax Tree (AST).
"""
from sly import Lexer, Parser

# --- AST Node Classes ---
class BinOp:
    """Binary Operator AST Node"""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    """Unary Operator AST Node"""
    def __init__(self, op, right):
        self.op = op
        self.right = right

class Number:
    """Number literal AST Node"""
    def __init__(self, value):
        self.value = value

class Symbol:
    """Symbol/Identifier AST Node"""
    def __init__(self, name):
        self.name = name

# --- Lexer ---
class ExpressionLexer(Lexer):
    """Lexer for assembly expressions."""
    tokens = { ID, HEX, BIN, OCT, DEC,
               PLUS, MINUS, TIMES, DIVIDE,
               AND, OR, XOR,
               LSHIFT, RSHIFT,
               LPAREN, RPAREN,
               LT, GT }

    ignore = ' \t'

    # Tokens
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    HEX = r'\$[0-9a-fA-F]+'
    BIN = r'%[01]+'
    OCT = r'@[0-7]+'
    DEC = r'\d+'

    # Operators
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    AND = r'&'
    OR = r'\|'
    XOR = r'\^'
    LSHIFT = r'<<'
    RSHIFT = r'>>'
    LPAREN = r'\('
    RPAREN = r'\)'
    LT = r'<'
    GT = r'>'

    def error(self, t):
        raise ValueError(f"Illegal character '{t.value[0]}'")

# --- Parser ---
class ExpressionParser(Parser):
    """Parser for assembly expressions. Builds an AST."""
    tokens = ExpressionLexer.tokens

    precedence = (
        ('left', OR, XOR),
        ('left', AND),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('left', LSHIFT, RSHIFT),
        ('right', UMINUS), # Unary minus
        ('right', LT, GT), # Unary high/low byte
    )

    @_('expr PLUS expr')
    def expr(self, p):
        return BinOp(p.expr0, p.PLUS, p.expr1)

    @_('expr MINUS expr')
    def expr(self, p):
        return BinOp(p.expr0, p.MINUS, p.expr1)

    @_('expr TIMES expr')
    def expr(self, p):
        return BinOp(p.expr0, p.TIMES, p.expr1)

    @_('expr DIVIDE expr')
    def expr(self, p):
        return BinOp(p.expr0, p.DIVIDE, p.expr1)

    @_('expr AND expr')
    def expr(self, p):
        return BinOp(p.expr0, p.AND, p.expr1)

    @_('expr OR expr')
    def expr(self, p):
        return BinOp(p.expr0, p.OR, p.expr1)

    @_('expr XOR expr')
    def expr(self, p):
        return BinOp(p.expr0, p.XOR, p.expr1)

    @_('expr LSHIFT expr')
    def expr(self, p):
        return BinOp(p.expr0, p.LSHIFT, p.expr1)

    @_('expr RSHIFT expr')
    def expr(self, p):
        return BinOp(p.expr0, p.RSHIFT, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return UnaryOp(p.MINUS, p.expr)

    @_('LT expr')
    def expr(self, p):
        return UnaryOp(p.LT, p.expr)

    @_('GT expr')
    def expr(self, p):
        return UnaryOp(p.GT, p.expr)

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('term')
    def expr(self, p):
        return p.term

    @_('HEX')
    def term(self, p):
        return Number(int(p.HEX[1:], 16))

    @_('BIN')
    def term(self, p):
        return Number(int(p.BIN[1:], 2))

    @_('OCT')
    def term(self, p):
        return Number(int(p.OCT[1:], 8))

    @_('DEC')
    def term(self, p):
        return Number(int(p.DEC))

    @_('ID')
    def term(self, p):
        return Symbol(p.ID.upper())