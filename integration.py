'''
Integration routines for CAS.

Currently, CAS can integrate the trigonometric functions sin, cos, and tangent,
powers of a variable, and any sum or difference of these.
'''

from parser import Func, Operator, MinusOp, Name, Number, ParseTree, Transform
from simplification import reduce

## The master integrator, called by Expr.integrate
## -----------------------------------------------------------------------------
def integrate(expr, var):
    def sub_int(expr, var):
        try:
            if not isinstance(expr, ParseTree):
                return int_rules[type(expr)](expr, var)
            else:
                return int_rules[type(expr.root)](expr, var)
        except KeyError:
            print(expr)
            print('No rule to integrate given expression')
        
    return reduce(sub_int(expr, var))
## -----------------------------------------------------------------------------
## Integration of the trigonometric functions
## -----------------------------------------------------------------------------
def int_func(expr, var):
    '''
    Integrate the trig functions
    '''
    try:
        if expr.left.value == var:
            return trig_int_rules[expr.root.value](expr, var)
        else:
            raise KeyError
    except KeyError:
        return ParseTree([Transform('integrate'), expr, Name(var)])
    
def i_sin(expr, var):
    '''
    Integrate the sin function.
    '''
    return ParseTree([MinusOp('-'),
                      ParseTree([Func('cos'), Name(var)])])

def i_cos(expr, var):
    '''
    Integrate the cos function
    '''
    return ParseTree([Func('sin'), Name(var)])

def i_tan(expr, var):
    '''
    Integrate the tan function
    '''
    return ParseTree([MinusOp('-'),
                      ParseTree([Func('ln'),
                                 ParseTree([Func('abs'),
                                            ParseTree([Func('cos'), Name(var)])])])])

trig_int_rules = {'sin':i_sin,
                  'cos':i_cos,
                  'tan':i_tan}
## -----------------------------------------------------------------------------
## Integration of operator expressions
## -----------------------------------------------------------------------------
def int_op(expr, var):
    if expr.root.value in ('+', '-'):
        return i_add_sub(expr, var)
    elif expr.root.value == '*':
        return i_mult(expr, var)
    elif expr.root.value == '^' and expr.left.value == var:
        return i_pow(expr, var)
    else:
        return ParseTree([Transform('integrate'), expr, Name(var)])

def i_add_sub(expr, var):
    '''
    Integrate an addition or subtraction expression
    '''
    return ParseTree([expr.root,
                      integrate(expr.left, var),
                      integrate(expr.right, var)])

def i_mult(expr, var):
    '''
    Integrate those multiplication expressions consisting of a number and a
    symbolic expression
    '''
    if isinstance(expr.left, Number):
        return ParseTree([expr.root,
                          expr.left,
                          integrate(expr.right, var)])
    elif isinstance(expr.right, Number):
        return ParseTree([expr.root,
                          expr.right,
                          integrate(expr.left, var)])
    else:
        return ParseTree([Transform('integrate'), expr, Name(var)])

def i_pow(expr, var):
    return ParseTree([Operator('/'),
                      ParseTree([Operator('^'),
                                 expr.left,
                                 ParseTree([Operator('+'),
                                            expr.right,
                                            Number(1)])]),
                      ParseTree([Operator('+'), expr.right, Number(1)])])
## -----------------------------------------------------------------------------
## Integration of a constants
## -----------------------------------------------------------------------------
def int_const(expr, var):
    return ParseTree([Operator('*'),
                      expr,
                      Name(var)])
## -----------------------------------------------------------------------------
def int_name(expr, var):
    # if the given expression is the first power of the integration variable,
    # then we can integrate it with the power rule
    if expr.value == var:
        return ParseTree([Operator('/'),
                          ParseTree([Operator('^'), expr, Number(2)]),
                          Number(2)])
    # otherwise, expr is a constant, as far as this integration is concerned
    else:
        return int_const(expr, var)
## -----------------------------------------------------------------------------
## Integration rules table
## -----------------------------------------------------------------------------
int_rules = {Func:int_func,
             Operator:int_op,
             Name:int_name,
             Number:int_const}
## END -------------------------------------------------------------------------
