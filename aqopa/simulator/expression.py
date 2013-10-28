'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import copy
from aqopa.model import IdentifierExpression, CallFunctionExpression, TupleExpression,\
    BooleanExpression, ComparisonExpression, TupleElementExpression
from aqopa.simulator.error import RuntimeException


class Populator():
    
    def populate(self, expression, variables, reducer):
        """
        Returns new expression with replaced variables names 
        with copies of values of variables from variables list.
        Reducer is used for special types of variables, 
        eg. tuple element expressions.
        """
        if isinstance(expression, IdentifierExpression):
            if expression.identifier not in variables:
                raise RuntimeException("Variable '%s' does not exist." % expression.identifier)
            return variables[expression.identifier].clone()
            
        if isinstance(expression, CallFunctionExpression):
            arguments = []
            for arg in expression.arguments:
                arguments.append(self.populate(arg, variables, reducer))
            qop_arguments = []
            for qop_arg in expression.qop_arguments:
                qop_arguments.append(qop_arg)
            return CallFunctionExpression(expression.function_name, arguments, qop_arguments)
            
        if isinstance(expression, TupleExpression):
            elements = []
            for e in expression.elements:
                elements.append(self.populate(e, variables, reducer))
            return TupleExpression(elements)
        
        if isinstance(expression, TupleElementExpression):
            if expression.variable_name not in variables:
                raise RuntimeException("Variable '%s' does not exist." % expression.variable_name)
            expr = variables[expression.variable_name]
            if not isinstance(expr, TupleExpression):
                expr = reducer.reduce(expr)
            if not isinstance(expr, TupleExpression):
                raise RuntimeException("Cannot compute expression %s. Variable '%s' is not a tuple. It is: %s." % (unicode(expression), expression.variable_name, unicode(expr)))
            if len(expr.elements) <= expression.index:
                raise RuntimeException("Cannot compute expression %s. Variable '%s' does not have index %s. It has %d elements." % 
                                        (expression.variable_name, expression.index, len(expr.elements)))
            return self.populate(expr.elements[expression.index], variables, reducer)
        
        return expression.clone()


class Checker():
    """
    Expression checker.
    Class used to check the result of expressions.
    """
    
    def _are_equal(self, left, right):
        """
        Method checks if both expressions are the same.
        
        Expressions cannot contains identifiers. All identifiers should be replaced with its values.
        Checks whether all function calls and boolean expressions have the same values,
        function names and parameters' values.
        """
        if left.__class__ != right.__class__:
            return False
        
        if isinstance(left, BooleanExpression):
            return left.val == right.val

        if isinstance(left, CallFunctionExpression):
            if left.function_name != right.function_name:
                return False
            if len(left.arguments) != len(right.arguments):
                return False
            for i in range(0, len(left.arguments)):
                if not self._are_equal(left.arguments[i], right.arguments[i]):
                    return False
        return False
    
    def result(self, condition, variables, functions, populator, reducer):
        """
        Method checks the result of condition.
        Returns True if condition is true or can be reduced to true condition.
        
        At the moment only comparision condition is available.  
        """
        
        if isinstance(condition, BooleanExpression):
            return condition.is_true()
        
        if isinstance(condition, ComparisonExpression):
            left = condition.left
            right = condition.right
            
            left = populator.populate(left, variables, reducer)
            right = populator.populate(right, variables, reducer)
            
            left = reducer.reduce(left)
            right = reducer.reduce(right)
            
            result = self._are_equal(left, right)
            del left
            del right
            return result
        
        return False

class ReductionPoint():
    """
    Class representing point where expression can be reduced.
    """
    
    def __init__(self, equation, expression, replacement, modified_part=None, modified_element_info=None):
        
        self.equation       = equation      # Equation that is used to reduce
        self.expression     = expression    # Expression that will be reduced
                                            # Reduction can replace whole expression 
                                            # or the part of expression
        self.replacement    = replacement   # Expression that will replace reduced part
        self.replaced = None                # Part of expression that was replaced with replacement
                                
        self.modified_part          = modified_part         # Part of expression that will be modified
                                                            # If None, whole expression should be replaced
        self.modified_element_info  = modified_element_info # Information which element 
                                                            # of modified part should be replaced
    
    def equals_to(self, reduction_point):
        """
        Returns True if self and reduction_points try to reduct the expression in the same place.
        """
        return self.expression == reduction_point.expression \
            and self.modified_part == reduction_point.modified_part \
            and self.modified_element_info == reduction_point.modified_element_info
        
    def _get_replaced_part(self):
        """
        Returns the part of expression that will be replaced.
        """
        if isinstance(self.modified_part, CallFunctionExpression):
            return self.modified_part.arguments[self.modified_element_info]
        
    def _replace_part(self, replacement):
        """
        Replace the part of modified_part according to modified_element_info.
        """
        if isinstance(self.modified_part, CallFunctionExpression):
            self.modified_part.arguments[self.modified_element_info] = replacement
        
    def reduce(self):
        """
        Returns reduced expression. 
        Method saves informaction for rolling back the reduction.
        """ 
        if self.modified_part is None:
            return self.replacement 
        
        self.replaced = self._get_replaced_part()
        self._replace_part(self.replacement)
        return self.expression
        
    def rollback(self):
        """
        Rolls back the reduction. 
        Returns expression to the form before reduction. 
        """
        if self.modified_part is None:
            return self.expression
        
        self._replace_part(self.replaced)
        self.replaced = None
        return self.expression

class Reducer():
    """
    Expression reducer.
    Class used to recude complex expressions with usage of equations.
    """
    
    def __init__(self, equations):
        self.equations = equations
        
        
    def _get_reduction_points_for_equation(self, equation, whole_expression, current_expression, 
                                           parent_expression=None, modified_element_info=None):
        """
        Recursive strategy of finding points.
        """
        points = []
        variables = {}
        
        if equation._can_reduce(current_expression, equation.composite, variables):
            
            if isinstance(equation.simple, IdentifierExpression):
                simpler_value = variables[equation.simple.identifier]
            else:
                simpler_value = equation.simple
                
            points.append(ReductionPoint(equation, 
                                         expression=whole_expression, 
                                         replacement=simpler_value, 
                                         modified_part=parent_expression, 
                                         modified_element_info=modified_element_info))
        
        if isinstance(current_expression, CallFunctionExpression):
            
            for i in range(0, len(current_expression.arguments)):
                e = current_expression.arguments[i]
                for p in self._get_reduction_points_for_equation(equation, 
                                                                 whole_expression, 
                                                                 current_expression=e,
                                                                 parent_expression=current_expression,
                                                                 modified_element_info=i):
                    points.append(p)
        
        return points
        
    def get_reduction_points_for_equation(self, equation, expression):
        """
        Method returns list of points where equation can reduce expression.
        
        Example:
        equation:   f(x) = x
        expression: f(a(f(b())))
                    ^   ^
        Two reduction points selected above,
        """
        return self._get_reduction_points_for_equation(equation=equation, 
                                          whole_expression=expression, 
                                          current_expression=expression,
                                          parent_expression=None,
                                          modified_element_info=None)
        
    def _get_reduction_points(self, expression):
        """
        Method finds points in expression where it can be reduced.
        """
        points = []
        for eq in self.equations:
            for p in self.get_reduction_points_for_equation(eq, expression):
                points.append(p)
        return points
        
    def reduce(self, expression):
        """
        Reduces expression with usage of equations.
        Returns reduced expression.
        Raises exception if ambiguity is found.
        """
        continue_reducing = True
   
        """     
        # Wrap expression and user wrapper variable
        # Used to simulate real pass-by-reference
        # If expression was passed without wrapped variable and equation wanted to
        # replace whole exception, it would not work, because whole variable cannot be changed
        # For example:
        # eq enc(K, dec(K, X)) = X
        # expression: enc(k(), dec(k(), b()) should be reduced to b()
        # If we pass whole expression variable to reduce we cannot change it whole
        # def f(x,v) -> x = v
        # e = A(a=1)
        # f(e, A(a=2)) - will not work, because e is reference to instance, but passed by value
        # When we pass wrapper, we can change its element (ie. expression)
        """
        
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
                    expression = reduction_point.reduce()
                    
                    # Generate new reduction points
                    new_reduction_points = self._get_reduction_points(expression)
                    
                    for old_reduction_point in old_reduction_points:
                        found = False
                        for new_reduction_point in new_reduction_points:
                            if old_reduction_point.equals_to(new_reduction_point):
                                found = True
                                break
                        if not found:
                            raise RuntimeException("Equations '%s' and '%s are ambiguous for expression: %s." % 
                                                   (unicode(old_reduction_point.equation),
                                                    unicode(new_reduction_point.equation),
                                                    unicode(expression)))
                            
                    # Cancel reduction
                    expression = reduction_point.rollback()
                    
                # Ambiguity error checked
                    
                # Make factual reduction
                reduction_point = reduction_points[0]
                
                # Reduce and commit reduction
                expression = reduction_point.reduce()
                
                continue_reducing = True
             
            return expression
                
                
                
                
                
                