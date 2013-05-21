'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class Checker():
    """
    Expression checker.
    Class used to check the result of expressions.
    """
    
    def populate_variables(self, expression, variables):
        """
        Replace variables names in expression with values 
        of variables from variables list.
        """
        raise NotImplementedError()

class Reducer():
    """
    Expression reducer.
    Class used to recude complex expressions with usage of equations.
    """
    
    def __init__(self, equations):
        self.equations = equations