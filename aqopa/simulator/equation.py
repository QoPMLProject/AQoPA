'''
Created on 14-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.model import CallFunctionExpression, IdentifierExpression,\
    BooleanExpression
from aqopa.simulator.error import EnvironmentDefinitionException

class Equation():
    """
    Equation built for simulation from parsed equation.
    """
    def __init__(self, composite, simple):
        self.composite = composite
        self.simple = simple
        
    def __unicode__(self):
        """ """
        return u"eq %s = %s" % ( unicode(self.composite), unicode(self.simple) )
        
    def _are_equal(self, left_expression, right_expression):
        """
        Method returns True, when expressions are equal.
        Equality covers: called function names, logic values, identifiers names.
        """
        if left_expression.__class__ != right_expression.__class__:
            return False
        
        if isinstance(left_expression, BooleanExpression):
            return left_expression.val == right_expression.val
        
        if isinstance(left_expression, IdentifierExpression):
            return left_expression.identifier == right_expression.identifier
        
        if isinstance(left_expression, CallFunctionExpression):
            if left_expression.function_name != right_expression.function_name:
                return False
            if len(left_expression.arguments) != len(right_expression.arguments):
                return False
            
            for i in range(0, len(left_expression.arguments)):
                if not self._are_equal(left_expression.arguments[i], right_expression.arguments[i]):
                    return False
            return True
        
    def _can_reduce(self, reduced_expression, composite_expression, variables):
        """
        Method returns True if reduced_expression can be reduced with composite_expression.
        Recursive strategy.
        
        composite_expression is a paremeter, because it is changed while nesting reduction check.
        Otherwise it would be possible to retrieve it from composite field of self.
        
        In variables parameter method saves values of identifiers from composite_expression.
        Method saves expression from reduced_expression for each identifier from composite_expression
        which stand in the same place. 
        """
        if isinstance(composite_expression, IdentifierExpression):
            if composite_expression.identifier not in variables:
                variables[composite_expression.identifier] = reduced_expression
                return True
            else:
                current_val = variables[composite_expression.identifier]
                if self._are_equal(current_val, reduced_expression):
                    return True
                
        if isinstance(composite_expression, BooleanExpression):
            if not isinstance(reduced_expression, BooleanExpression):
                return False
            return self._are_equal(composite_expression, reduced_expression)
        
        if isinstance(composite_expression, CallFunctionExpression):
            if not isinstance(reduced_expression, CallFunctionExpression):
                return False
            if composite_expression.function_name != reduced_expression.function_name:
                return False
            if len(composite_expression.arguments) != len(reduced_expression.arguments):
                return False
        
            for i in range(0, len(composite_expression.arguments)):
                if not self._can_reduce(reduced_expression.arguments[i], 
                                        composite_expression.arguments[i], 
                                        variables):
                    return False
            return True
        
        return False

class Validator():
    
    def _find_function(self, functions, name):
        """"""
        for f in functions:
            if f.name == name:
                return f
        return None
    
    def _validate_function_names(self, expression, functions):
        """
        Method checs if all function exist and are callef woth correct number of parameters.
        Returns True or raises EnvironmentDefinitionException.
        """
        if isinstance(expression, CallFunctionExpression):
            function = self._find_function(functions, expression.function_name)
            if not function:
                raise EnvironmentDefinitionException('Function %s does not exist.' % expression.function_name)
            if len(function.params) != len(expression.arguments):
                raise EnvironmentDefinitionException('Function %s called with wrong number of arguments - expected: %d, got: %d.' 
                                                     % expression.function_name, len(function.params), len(expression.arguments))
            for arg in expression.arguments:
                if isinstance(arg, CallFunctionExpression):
                    self._validate_function_names(arg, functions)
        return True
    
    def _are_expressions_the_same(self, left, right, check_variables=False, variables={}):
        """
        Method checks if expressions are the same in aspect of equations, which means that
        both expressions could be used to reduce another expression.
        Method can check also the names variables from both expressions. Method checks 
        if variable X from left expression stands in all the same places (and no more) 
        that corresponding variable Y from right expressions.
        
        Example:
        f(x,y,x,x) == f(a,b,a,a) - are the same
        f(x,y,x,x) == f(a,b,a,b) - are not the same, because second b should be a
        """
        
        if left.__class__ != right.__class__:
            return False
        
        if isinstance(left, IdentifierExpression):
            if not check_variables:
                return True
            
            if left.identifier in variables:
                return variables[left.identifier] == right.identifier
            else:
                variables[left.identifier] = right.identifier
                return True
            
        if isinstance(left, BooleanExpression):
            return left.val == right.val
        
        if isinstance(left, CallFunctionExpression):
            
            if left.function_name != right.function_name:
                return False
            
            if len(left.arguments) != len(right.arguments):
                return False
            
            for i in range(0, len(left.arguments)):
                if not self._are_expressions_the_same(left.arguments[i], right.arguments[i], check_variables, variables):
                    return False
            return True
        
        return False
    
    def _expression_contains_identifier(self, expression, identifier):
        """
        Returns True if expression contains an identifier expression 
        with name equal to second parameter.
        """
        if isinstance(expression, IdentifierExpression):
            return expression.identifier == identifier
        
        if isinstance(expression, CallFunctionExpression):
            for arg in expression.arguments:
                if self._expression_contains_identifier(arg, identifier):
                    return True
            return False
        
        return False
    
    def _validate_syntax(self, parsed_equations, functions):
        """
        Method check the syntax of equations:
        - does composite part include the identifier from simple part (if simple part is identifier)?
        - do all functions exist and are callef woth correct number of parameters?
        Returns True or raises EnvironmentDefinitionException.
        """
        errors = []
        for eq in parsed_equations:
            try:
                self._validate_function_names(eq.composite, functions)
            except EnvironmentDefinitionException, e:
                errors.append(e.args[0])
                
            if isinstance(eq.simple, IdentifierExpression):
                if not self._expression_contains_identifier(eq.composite, eq.simple.identifier):
                    errors.append("Equation '%s' does not have identifier from simple expression '%s' in composite expression."
                                  % (unicode(eq), eq.simple.identifier))
        if len(errors) > 0:
            raise EnvironmentDefinitionException('Invalid syntax.', errors=errors)
    
    def validate(self, parsed_equations, functions):
        """
        Validates equations parsed from model according to functions.
        Returns True if validation is passed or raises EnvironmentDefinitionException.
        """
        
        # Validate syntax - function names and parametrs counts
        self._validate_syntax(parsed_equations, functions)
        
        errors = []
        
        # Search for equations that can reduce themselves
        # Check all possible pairs of equations
        for i in range (0, len(parsed_equations)):
            has_the_same_expression = False
            for j in range(i+1, len(parsed_equations)):
                variables_map = {}
                eq_left = parsed_equations[i]
                eq_right = parsed_equations[j]
                
                if self._are_expressions_the_same(eq_left.composite, eq_right.composite, check_variables=True, variables=variables_map):
                    if variables_map[eq_left.simple.identifier] == eq_right.simple.identifier:
                        has_the_same_expression = True
                        break
            if has_the_same_expression:
                errors.append("Equations '%s' and '%s' are the same." % (unicode(eq_left), unicode(eq_right)))
        
        # Todo: Check ambiguity
        
        return True

