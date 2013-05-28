'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import copy
from qopml.interpreter.model import IdentifierExpression, CallFunctionExpression, TupleExpression
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
        
    def _get_reduction_points(self, expression):
        raise NotImplementedError()
        
    def reduce(self, expression):
        """
        Reduces expression with usage of equations.
        Returns True if expression is reduced or False if it is not reducable.
        Raises exception if ambiguity is found.
        """
        
        reduced = False
        continue_reducing = True
        
        # Reduce until no reduction can be performed.
        # One reduction can give way for another reduction.
        while continue_reducing:
            continue_reducing = False
            
            # For each equation we find points where expression can be reduced
            reduction_points = self._get_reduction_points(expression)
        
            if len(reduction_points) > 0:
                
                # For each poing:
                #  - temporary reduce at this point
                #  - remove used point from reduction points list
                #  - generate new reduction points list for reduced expression
                #  - if any of points from old list is not present in new list raise ambiguity exception
                #  ! New reduction points may come
                
                for reduction_point in reduction_points:
                    
                    # Generate list with reduction points before reduction
                    old_reduction_points = copy.copy(reduction_points)
                    old_reduction_points.remove(reduction_point)
                    
                    # Reduce temporary
                    reduction_point.reduce()
                    
                    # Generate new reduction points
                    new_reduction_points = self._get_reduction_points(expression)
                    
                    
                    
                     
                
                
                
                
                
                
                