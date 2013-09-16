'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class ParserException(Exception):   
    
    def __init__(self, *args, **kwargs):
        """ """
        self.syntax_errors = []
        if 'syntax_errors' in kwargs:
            self.syntax_errors = kwargs['syntax_errors']
            del kwargs['syntax_errors']
        super(ParserException, self).__init__(*args)
        
class ModelParserException(ParserException):
    pass
        
class MetricsParserException(ParserException):
    pass
        
class ConfigurationParserException(ParserException):
    pass


class QoPMLModelParser():
    
    def parse(self, s):
        """
        Parses string s and returns the store of all required parsed objects.
        The parser can also store created objects in his own store.
        Sometimes modules will add parsing rules and the results should be keept by the modules,
        so information about custom stores filling in is kept in modules code. 
        """
        raise NotImplementedError()
    
    def get_syntax_errors(self):
        """
        Returns list of syntax errors.
        """
        raise NotImplementedError()
    


    