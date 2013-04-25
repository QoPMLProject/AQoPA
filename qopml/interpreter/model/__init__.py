'''
Created on 23-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''


################################################
#              QoPML Model Elements
################################################


class Function():
    
    def __init__(self, name, params = [], qop_params = [], comment = ""):
        self.name = name
        self.params = params
        self.qop_params = qop_params
        self.comment = comment
        
    def __unicode__(self):
        
        comment = ""
        if self.comment:
            comment = "( %s )" % self.comment
            
        qop_params = ""
        if len(self.qop_params):
            qop_params = [ '%s : %s' % (name, ', '.join(pars)) for (name, pars) in self.qop_params ]
            qop_params = ', '.join(qop_params)
            qop_params = "[%s]" % qop_params
            
        return u"fun %s(%s) %s %s" % (self.name, ', '.join(self.params), qop_params, comment)
        
    
    
class Channel():
    
    def __init__(self, name, buffor_size):
        self.name = name
        self.buffor_size = buffor_size # Buffor size < 0 is unlimited

    def __unicode__(self):
        buffor_size = str(self.buffor_size) if self.buffor_size >= 0 else "*"
        return u"channel %s [%s]" % (self.name, buffor_size)
    

class Equation():
    
    def __init__(self, simple, composite):
        self.simple = simple
        self.composite = composite
        
    def __unicode__(self):
        return u"eq %s = %s" % ( unicode(self.composite), unicode(self.simple) )
    
    
class BooleanExpression():
    
    def __init__(self, val):
        self.val = val
        
    def __unicode__(self):
        return u"true" if self.val else u"false"
    
class IdentifierExpression():
    
    def __init__(self, identifier):
        self.identifier = identifier
        
    def __unicode__(self):
        return unicode(self.identifier)
    
class CallFunctionExpression():
    
    def __init__(self, function_name, arguments=[]):
        self.function_name = function_name
        self.arguments = arguments
        
    def __unicode__(self):
        return u"%s(%s)" % ( self.function_name, ', '.join([ unicode(a) for a in self.arguments]) )
        
        
        
        
        
        
    
    