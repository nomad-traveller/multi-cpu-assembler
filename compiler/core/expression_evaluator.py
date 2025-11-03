"""
An AST-based expression evaluator. It recursively walks the AST generated
by the expression parser and computes the final value.
"""
from core.expression_parser import BinOp, UnaryOp, Number, Symbol

def evaluate_expression(node, symbol_table, line_num, current_address: int = 0):
    """
    Recursively evaluates an expression AST node.
    
    Args:
        node: The AST node to evaluate
        symbol_table: Symbol table for resolving symbols
        line_num: Line number for error reporting
        current_address: Current program counter address for * symbol
    """
    if node is None:
        return None
    
    if type(node).__name__ == 'Number':
        return node.value
    if type(node).__name__ == 'Symbol':
        if node.name == '*':
            return current_address  # Return the current address
        value = symbol_table.resolve(node.name)
        if value is None:
            raise ValueError(f"Undefined symbol '{node.name}' on line {line_num}")
        return value
    if isinstance(node, UnaryOp):
        right = evaluate_expression(node.right, symbol_table, line_num, current_address)
        if node.op == '-':
            return -right
        if node.op == '<':
            return right & 0xFF
        if node.op == '>':
            return (right >> 8) & 0xFF
    if isinstance(node, BinOp):
        left = evaluate_expression(node.left, symbol_table, line_num, current_address)
        right = evaluate_expression(node.right, symbol_table, line_num, current_address)
        if node.op == '+': return left + right
        if node.op == '-': return left - right
        if node.op == '*': return left * right
        if node.op == '/': return left // right
        if node.op == '&': return left & right
        if node.op == '|': return left | right
        if node.op == '^': return left ^ right
        if node.op == '<<': return left << right
        if node.op == '>>': return left >> right
    
    # This case handles a raw integer passed in (e.g. from an old part of the code)
    if isinstance(node, int):
        return node
        
    raise ValueError(f"Unknown AST node type: {type(node).__name__} on line {line_num}")