'''
Created on 23-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import copy
#from qopml.interpreter.simulator.error import RuntimeException

################################################
#             Names functions
################################################
        
def original_name(name):
    """
    Return name without indexes.
    """
    return name.split('.')[0]

def name_indexes(name):
    """
    Return indexes of name.
    """
    indexes = name.split('.')
    if len(indexes) == 0:
        indexes = []
    else:
        indexes = indexes[1:]
    return [ int(i) for i in indexes ]

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
        

COMMUNICATION_TYPE_IN = 1
COMMUNICATION_TYPE_OUT = 2
    
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
    
################################
#        Expressions
################################
    
class BooleanExpression():
    
    def __init__(self, val):
        self.val = bool(val)
        
    def __unicode__(self):
        return u"true" if self.val else u"false"
    
    def is_true(self):
        return self.val
    
    def clone(self):
        return copy.deepcopy(self)
    
class IdentifierExpression():
    
    def __init__(self, identifier):
        self.identifier = identifier
        
    def __unicode__(self):
        return unicode(self.identifier)
    
    def clone(self):
        return copy.deepcopy(self)
    
class CallFunctionExpression():
    
    def __init__(self, function_name, arguments=[], qop_arguments=[]):
        self.function_name = function_name
        self.arguments = arguments
        self.qop_arguments = qop_arguments
        
    def __unicode__(self):
        return u"%s(%s)[%s]" % ( unicode(self.function_name), unicode(', '.join([ unicode(a) for a in self.arguments])),
                                  unicode(', '.join([ unicode(a) for a in self.qop_arguments])) )
        
    def clone(self):
        return CallFunctionExpression(copy.copy(self.function_name), 
                                      [ a.clone() for a in self.arguments ],
                                      [ copy.copy(a) for a in self.qop_arguments ])
        
class ComparisonExpression():
    
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def __unicode__(self):
        return "%s == %s" % (unicode(self.left), unicode(self.right))
    
    def clone(self):
        return ComparisonExpression(self.left.clone(), self.right.clone())
    
class TupleExpression():
    
    def __init__(self, elements):
        self.elements = elements
        
    def __unicode__(self):
        return u"(%s)" % unicode(', '.join([unicode(e) for e in self.elements]))
    
    def clone(self):
        return TupleExpression([e.clone() for e in self.elements])
    
class TupleElementExpression():
    
    def __init__(self, variable_name, index):
        self.variable_name = variable_name
        self.index = index
        
    def __unicode__(self):
        return u"%s[%d]" % (unicode(self.variable_name), self.index)
    
    def clone(self):
        return copy.deepcopy(self)
      
################################
#        Instructions
################################
    
class CallFunctionInstruction():
    
    def __init__(self, function_name, arguments=[], qop_arguments=[]):
        self.function_name = function_name
        self.arguments = arguments
        self.qop_arguments = qop_arguments
        
    def __unicode__(self):
        return u"%s(%s)[%s];" % ( unicode(self.function_name), unicode(', '.join([ unicode(a) for a in self.arguments])),
                                  unicode(', '.join([ unicode(a) for a in self.qop_arguments])) )
    
class FinishInstruction():
    
    def __init__(self, command):
        self.command = command
        
    def __unicode__(self):
        return "%s;" % unicode(self.command)
    
class ContinueInstruction():
    
    def __unicode__(self):
        return u"continue;"
    
class AssignmentInstruction():
    
    def __init__(self, variable_name, expression):
        self.variable_name = variable_name
        self.expression = expression
        
    def __unicode__(self):
        return u"%s = %s;" % (unicode(self.variable_name), unicode(self.expression))
    
class CommunicationInstruction():
    
    def __init__(self, communication_type, channel_name, variables_names):
        self.communication_type = communication_type
        self.channel_name = channel_name
        self.variables_names = variables_names
        
    def is_out(self):
        return self.communication_type == COMMUNICATION_TYPE_OUT
        
    def __unicode__(self):
        type_name = 'in' if self.communication_type == COMMUNICATION_TYPE_IN else 'out'
        return u"%s (%s: %s);" % (unicode(type_name), unicode(self.channel_name), unicode(', '.join(self.variables_names)))
        
class IfInstruction():
    
    def __init__(self, condition, true_instructions, false_instructions=[]):
        self.condition = condition
        self.true_instructions = true_instructions
        self.false_instructions = false_instructions
        
    def __unicode__(self):
        return u"if (%s) ..." % unicode(self.condition)
        
class WhileInstruction():
    
    def __init__(self, condition, instructions):
        self.condition = condition
        self.instructions = instructions
        
    def __unicode__(self):
        return u"while (%s) ..." % unicode(self.condition)

################################
#        Hosts
################################

class HostSubprocess():
    
    def __init__(self, name, instructions_list):
        self.name = name
        self.instructions_list = instructions_list
        self.all_channels_active = False
        self.active_channels = []
        
    def __unicode__(self):
        return u"subprocess %s" % unicode(self.name)

class HostProcess():
    
    def __init__(self, name, instructions_list):
        self.name = name
        self.instructions_list = instructions_list
        self.all_channels_active = False
        self.active_channels = []
        
        self.follower = None
        
    def clone(self):
        p = HostProcess(self.name, self.instructions_list)
        p.all_channels_active = self.all_channels_active
        p.active_channels = self.active_channels
        return p
        
    def __unicode__(self):
        return u"process %s" % unicode(self.name)
        
        
class Host():
    
    def __init__(self, name, schedule_algorithm, instructions_list, predefined_values=[]):
        self.name = name
        self.schedule_algorithm = schedule_algorithm
        self.instructions_list = instructions_list
        self.predefined_values = predefined_values
        self.all_channels_active = False
        self.active_channels = []
        
    def __unicode__(self):
        return u"host %s" % unicode(self.name)
        
    def clone(self):
        
        instructions_list = []
        for i in self.instructions_list:
            if isinstance(i, HostProcess):
                instructions_list.append(i.clone())
            else:
                instructions_list.append(i)
        
        h = Host(self.name, self.schedule_algorithm, instructions_list, self.predefined_values)
        h.all_channels_active = self.all_channels_active
        h.active_channels = self.active_channels
        return h
        
################################
#        Versions
################################

class Version():
    
    def __init__(self, name):
        self.name = name
        self.run_hosts = []
        
    def __unicode__(self):
        return u"version %d" % self.name
    
class VersionRunHost():
    
    def __init__(self, host_name):
        self.host_name = host_name
        self.all_channels_active = False
        self.active_channels = []
        self.repetitions = 1
        self.repeated_channels = []
        self.run_processes = []
        
    def __unicode__(self):
        return u"run host %s (...)" % self.host_name
    
class VersionRunProcess():
    
    def __init__(self, process_name):
        self.process_name = process_name
        self.all_subprocesses_active = False
        self.active_subprocesses = []
        self.repetitions = 1
        self.repeated_channels = []
        self.follower = None
        
    def __unicode__(self):
        s = u"run %s (...)" % self.process_name
        if self.follower:
            s += " -> %s" % unicode(self.follower)
        return s
    

################################
#        Metrics
################################

class MetricsConfiguration():
    
    def __init__(self, name, specifications):
        self.name = name
        self.specifications = specifications
        
    def __unicode__(self):
        return u"conf %s { ... }" % self.name

class MetricsSet():
    
    def __init__(self, host_name, configuration_name):
        self.host_name = host_name
        self.configuration_name = configuration_name     
    
    def __unicode__(self):
        return u"set host %s (%s) { ... }" % (self.host_name, self.configuration_name)
    
class MetricsData():
    
    def __init__(self, name, blocks, plus = False, star = False):
        self.name = name
        self.blocks = blocks
        self.star = star
        self.plus = plus
        
    def __unicode__(self):
        return u"data %s { ... }" % self.name
        
class MetricsPrimitiveBlock():
    
    def __init__(self, header, metrics):
        self.header = header
        self.metrics = metrics
        
class MetricsPrimitiveHeader():
    
    def __init__(self, params, services_params):
        self.params = params
        self.services_params = services_params
        
class MetricsServiceParam():
    
    def __init__(self, service_name, param_name, unit=None):
        self.service_name = service_name 
        self.param_name = param_name
        self.unit = unit
        
class MetricsPrimitive():
    
    def __init__(self, arguments):
        self.arguments = arguments
    