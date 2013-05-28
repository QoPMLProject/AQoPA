'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from qopml.interpreter.model import IdentifierExpression, CallFunctionExpression,\
    TupleExpression
from qopml.interpreter.simulator.error import RuntimeException

class Checker():
    """
    Expression checker.
    Class used to check the result of expressions.
    """
    
    def populate_variables(self, expression, variables):
        """
        Returns new expression with replaced variables names 
        with copies of values of variables from variables list.
        """
        if isinstance(expression, IdentifierExpression):
            if expression.identifier not in variables:
                raise RuntimeException("Variable '%s' does not exist" % expression.identifier)
            return variables[expression.identifier].clone()
            
        if isinstance(expression, CallFunctionExpression):
            pass
        
        if isinstance(expression, TupleExpression):
            pass
        
        return expression.clone()
    
    
    def result(self, condition, variables, functions):
        raise NotImplementedError()

class Reducer():
    """
    Expression reducer.
    Class used to recude complex expressions with usage of equations.
    """
    
    def __init__(self, equations):
        self.equations = equations
        
    def reduce(self, expression):
        pass