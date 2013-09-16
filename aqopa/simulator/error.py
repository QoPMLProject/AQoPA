'''
Created on 27-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class EnvironmentDefinitionException(Exception):
    
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args)
        
        self.errors = []
        if 'errors' in kwargs:
            self.errors = kwargs['errors']
            del kwargs['errors']

class RuntimeException(Exception):
    pass

class InfiniteLoopException(RuntimeException):
    pass