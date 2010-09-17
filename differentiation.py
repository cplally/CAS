'''
Differentiation routines for CAS.
'''

from parser import Func, Operator, MinusOp, Name, Number, ParseTree
from simplification import reduce
from operator import add, sub, mul, floordiv, pow

## First, the master differentiator -- called externally
## -----------------------------------------------------------------------------
def diff(expr, var):
    '''
    Apply the differentiation rules given in diff_rules to expr_tree.
    '''
    def sub_diff(expr, var):
        try:
            if not isinstance(expr, ParseTree):
                return diff_rules[type(expr)](expr, var)
            else:
                return diff_rules[type(expr.root)](expr, var)
        except KeyError:
            print(expr)
            print('No rule to differentiate given expression -- check input')
    
    return reduce(sub_diff(expr, var))
## -----------------------------------------------------------------------------
## Differentiation of functions
## -----------------------------------------------------------------------------
def diff_func(expr, var):
    '''
    Differentiate a function
    '''
    try:
        return chain_rule(func_diff_rules[expr.root.value], expr, var)
    except KeyError:
        return chain_rule(
            lambda e, v: ParseTree([Func('d[%s, %s]' % (e.root.value, v)),
                                    e.left]),
            expr,
            var)

def chain_rule(func, expr, var):
    '''
    Perform the chain rule
    '''
    return ParseTree([Operator('*'), func(expr, var), diff(expr.left, var)])

def d_sin(expr, var):
    '''
    Differentiate the sin function
    '''
    return ParseTree([Func('cos'), expr.left])

def d_cos(expr, var):
    '''
    Differentiate the cos function
    '''
    return ParseTree([MinusOp('-'),
                      ParseTree([Func('sin'), expr.left])])

def d_tan(expr, var):
    '''
    Differentiate the tan function
    '''
    return ParseTree([Operator('+'),
                      Number(1),
                      ParseTree([Operator('^'),
                                 ParseTree([Func('tan'), expr.left]),
                                 Number(2)])])

def d_exp(expr, var):
    '''
    Differentiate the exponential function
    '''
    return ParseTree([Func('exp'), expr.left])
## -----------------------------------------------------------------------------
## Now we move on to the differentiation of operator expressions.
## -----------------------------------------------------------------------------
def diff_op(expr, var):
    '''
    Differentiate an operator expression
    '''
    # there are a five different operators (^, *, /, +, -) and four distinct
    # rules; we need a case for each rule
    if expr.root.value in ('+', '-'):
        # this is an addition or subtraction
        return d_add_sub(expr, var)
    elif expr.root.value == '*':
        # a multiplication
        return d_mult(expr, var)
    elif expr.root.value == '/':
        # a division
        return d_div(expr, var)
    elif expr.root.value == '^':
        # an exponent
        return chain_rule(d_expt, expr, var)
    else:
        # uh oh...
        print('Something is wrong -- that\'s not an operator CAS recognizes.')

def d_add_sub(expr, var):
    '''
    Differentiate an addition or subtraction expression
    '''
    return ParseTree([expr.root,
                      diff(expr.left, var),
                      diff(expr.right, var)])

def d_mult(expr, var):
    '''
    Differentiate a multiplication expression
    '''
    return ParseTree([Operator('+'),
                      ParseTree([Operator('*'),
                                 expr.left,
                                 diff(expr.right, var)]),
                      ParseTree([Operator('*'),
                                 diff(expr.left, var),
                                 expr.right])])
def d_div(expr, var):
    '''
    Differentiate a division expression
    '''
    return diff(ParseTree([Operator('*'),
                           expr.left,
                           ParseTree([Operator('^'),
                                      expr.right,
                                      ParseTree([MinusOp('-'),
                                                 Number('1')])])]),
                var)

def d_expt(expr, var):
    '''
    Differentiate an exponentiation expression
    '''
    return ParseTree([Operator('*'),
                      expr.right,
                      ParseTree([Operator('^'),
                                 expr.left,
                                 ParseTree([MinusOp('-'),
                                            expr.right,
                                            Number('1')])])])
## -----------------------------------------------------------------------------
## Name
## -----------------------------------------------------------------------------
def diff_name(expr, var):
    if expr.value == var:
        return Number(1)
    else:
        return Number(0)
## -----------------------------------------------------------------------------
## Number
## -----------------------------------------------------------------------------
def diff_number(expr, var):
    return Number(0)
## -----------------------------------------------------------------------------
## Build the rules tables
## -----------------------------------------------------------------------------
diff_rules = {Func:diff_func,
              Operator:diff_op,
              MinusOp:diff_op,
              Name:diff_name,
              Number:diff_number}

func_diff_rules = {'sin':d_sin,
                   'cos':d_cos,
                   'tan':d_tan,
                   'exp':d_exp}
## END -------------------------------------------------------------------------
