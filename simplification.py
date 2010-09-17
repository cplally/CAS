'''
Simplification routines for CAS.
'''

from parser import Operator, MinusOp, Number, ParseTree
from operator import add, sub, mul, truediv, pow
from fractions import Fraction

class NonNumericExpr(Exception):
    '''
    This is an exception needed by reduce_numeric_expr
    '''
    def __init__(self, error_msg=''):
        Exception.__init__(self, error_msg)

def reduce(expr):
    '''
    Cleans up expr, reducing any easily-computed numeric expressions.
    '''
    if not isinstance(expr, ParseTree):
        return expr
    else:
        if expr.right:
            return minimal_simplify(ParseTree([expr.root,
                                               reduce(expr.left),
                                               reduce(expr.right)]))
        else:
            return minimal_simplify(ParseTree([expr.root, reduce(expr.left)]))

def minimal_simplify(expr):
    if isinstance(expr.root, Operator):
        return op_table[expr.root.value](expr)
    else:
        return expr

def reduce_numeric_expr(expr, op):
    '''
    Reduces a numeric expression (e.g., [+, 2, 2]); raises NonNumericExpr if
    expr has only one child, or if expr is not a numeric expression.
    '''
    if False not in [isinstance(x, Number) for x in expr.children]:
        left, right = expr.left.value, expr.right.value
        return Number(op(left, right))
    else:
        raise NonNumericExpr

def reduce_add_sub(expr):
    '''
    Reduction cases for addition, subtraction, or negation expressions
    '''
    # we need two operations, since this function handles both addition and
    # subtraction
    ops = {'+':add, '-':sub}
    
    # if the operands are both numeric, evaluate the expression
    try:
        return reduce_numeric_expr(expr, ops[expr.root.value])
    except NonNumericExpr:
        # now we move on to simplifications we can make for subtraction expressions
        if expr.root.value == '-':
            if expr.left.value == 0:
                if not expr.right:
                    return Number(0)
                else:
                    return ParseTree([MinusOp('-'), expr.right])
            elif expr.right and expr.right.value == 0:
                return expr.left
        # simplifying addition expressions
        elif expr.root.value == '+':
            if expr.left.value == 0:
                return expr.right
            elif expr.right.value == 0:
                return expr.left
        
        return expr

def reduce_mul(expr):
    '''
    Reduction case for multiplication expressions.
    '''
    try:
        return reduce_numeric_expr(expr, mul)
    except NonNumericExpr:
        if 0 in [x.value for x in expr.children]:
            return Number(0)
        elif expr.left.value == 1:
            return expr.right
        elif expr.right.value == 1.0:
            return expr.left
        else:
            return expr

def reduce_div(expr):
    '''
    Reduction case for division expressions.
    '''
    # for stylistic reasons, I do not want to convert fractions to decimals;
    # thus, I won't use reduce_numeric_expr right away.
    if False not in [isinstance(x, Number) for x in expr.children] and \
            (float not in [type(x.value) for x in expr.children]):
        return Number(Fraction(expr.left.value, expr.right.value))
    else:
        try:
            reduce_numeric_expr(expr, truediv)
        except NonNumericExpr:
            if expr.right.value == 1:
                return expr.left
            elif expr.right.value == 0:
                raise ZeroDivisionError
            else:
                return expr

def reduce_pow(expr):
    '''
    Reduction case for exponentiation expressions
    '''
    try:
        return reduce_numeric_expr(expr, pow)
    except:
        if expr.right.value == 1:
            return expr.left
        elif expr.right.value == 0:
            return Number(1)
        else:
            return expr
## -----------------------------------------------------------------------------
## The operator table
## -----------------------------------------------------------------------------
op_table = {'+':reduce_add_sub,
            '-':reduce_add_sub,
            '*':reduce_mul,
            '/':reduce_div,
            '^':reduce_pow}
## END -------------------------------------------------------------------------
