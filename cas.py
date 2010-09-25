import differentiation
import integration
from parser import Parser, ParseTree, Operators, relative_precedence,\
    Func, Transform, MinusOp

from fractions import Fraction
import os

class Expr():
    def __init__(self, expr_string='', expr_tree=None):
        self.string_repr = expr_string
        if expr_tree:
            self.tree_repr = expr_tree
        else:
            self.tree_repr = Parser().parse(self.string_repr)

    def d(self, var):
        '''
        Differentiate the expression with respect to the variable given by the
        string var.
        
        Example: f.d('x') to differentiate some expression f wrt the variable x.
        '''
        return Expr(expr_tree=differentiation.diff(self.tree_repr, var))

    def integrate(self, var):
        '''
        Integrate the expression with respect to var; used in similar fashion as
        d.
        '''
        return Expr(expr_tree=integration.integrate(self.tree_repr, var))
    
    def plot(self, title=None, labels=None, range=None):
        '''
        Plot the expression using gnuplot.
        
        If title is specified, it will be used as the plot title.
        If labels is a tuple of strings, said strings will be used as the axis
        labels.
        When range is specified as a tuple of tuples of numbers (eg., ((0,1),
        (-1,1))), the first two will be set as the xrange and the last two, as
        the yrange.
        '''
        # some things we need from outside
        from tempfile import NamedTemporaryFile
        from subprocess import Popen
        
        # the expression must be sent to gnuplot in the proper format
        plot_func = self.__str__(gnuplot_mode=True)
        # we need to create a temporary file to hold the gnuplot commands; its
        # contents will be sent to gnuplot via the subprocess facilities
        plot_file = NamedTemporaryFile(mode='w+')
        
        # now we move on to building up the commands
        # first, a setting to make our plots look nicer
        plot_file.write('set samples 200\n')
        # second, has the user specified a title for the plot?
        if title:
            plot_file.write('set title "%s"\n' % title)
        # ok, how about labels for the axes?
        if labels:
            plot_file.write('set xlabel "%s"\nset ylabel "%s"\n' % labels)
        # has the range been specified?
        if range:
            if range[0]:
                plot_file.write('set xrange [%s:%s]\n' % range[0])
            if len(range) == 2 and range[1]:
                plot_file.write('set yrange [%s:%s]\n' % range[1])
        # write plot_func to plot_file
        plot_file.write('plot %s\n' % plot_func)
        
        # flush; need this so that we can send the file to gnuplot
        plot_file.flush()
        
        # now, plot!
        p = Popen('gnuplot -persist %s' % plot_file.name, shell=True)
        p.wait()
        # clean up
        plot_file.close()
        
    def __format(self, gnuplot_mode=False):
        '''
        Format output for printing and for plotting
        '''
        def gnuplotized(value):
            if value == '^' and gnuplot_mode is True:
                return '**'
            else:
                return value
        
        def operators_p(*ops):
            if False in [(lambda x: x in Operators)(op) for op in ops]:
                return False
            else:
                return True
        
        def precedence_for_parens(root, subtree):
            if operators_p(root.value, subtree.root.value) and\
                      relative_precedence(root.value, subtree.root.value) > 0:
                return ['('] + converter(subtree) + [')']
            else:
                return converter(subtree)
        
        def parenthesizer(expr):
            parenthesized_expr = []
            
            # do we need to parenthesize the left subtree?
            if isinstance(expr.left, ParseTree):
                parenthesized_expr += \
                    precedence_for_parens(expr.root, expr.left)
            else:
                parenthesized_expr += converter(expr.left)
            # now add the operator
            parenthesized_expr += [gnuplotized(expr.root.value)]
            # what about the right subtree?
            if isinstance(expr.right, ParseTree):
                parenthesized_expr += \
                    precedence_for_parens(expr.root, expr.right)
            else:
                if expr.root.value == '^' and type(expr.right.value) == Fraction:
                    parenthesized_expr += ['(%s)' % expr.right]
                else:
                    parenthesized_expr += converter(expr.right)
            
            return parenthesized_expr
        
        def converter(expr):
            if not isinstance(expr, ParseTree):
                return ['%s' % expr.value]
            else:
                if isinstance(expr.root, Func):
                    return [expr.root.value] + ['('] + converter(expr.left) +\
                        [')']
                elif isinstance(expr.root, Transform):
                    return [expr.root.value] + ['['] + converter(expr.left) +\
                        [', '] + converter(expr.right) + [']']
                elif isinstance(expr.root, MinusOp):
                    return [expr.root.value] + converter(expr.left)
                elif expr.right:
                    return parenthesizer(expr)
        
        return converter(self.tree_repr)
    
    def __str__(self, gnuplot_mode=False):
        output = ''
        for token in self.__format(gnuplot_mode):
            output += token
        return output
