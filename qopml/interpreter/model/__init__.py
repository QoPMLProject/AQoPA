'''
Created on 23-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import copy

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
        self.val = val
        
    def __unicode__(self):
        return u"true" if self.val else u"false"
    
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
        return u"%s(%s)[%s];" % ( unicode(self.function_name), unicode(', '.join([ unicode(a) for a in self.arguments])),
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
        return u"(%s)" % unicode(', '.join(self.elements))
    
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
        return u"%s = %s;" % (unicode(self.variable_identifier), unicode(self.expression))
    
class CommunicationInstruction():
    
    def __init__(self, communication_type, channel_name, variables_names):
        self.communication_type = communication_type
        self.channel_name = channel_name
        self.variables_names = variables_names
        
    def __unicode__(self):
        type_name = 'in' if self.communication_type == COMMUNICATION_TYPE_IN else 'out'
        return u"%s (%s: %s)" % (unicode(type_name), unicode(self.channel_name), unicode(', '.join(self.variables_names)))
        
class IfInstruction():
    
    def __init__(self, conditional, true_instructions, false_instructions=[]):
        self.conditional = conditional
        self.true_instructions = true_instructions
        self.false_instructions = false_instructions
        
    def __unicode__(self):
        return u"if (%s) ..." % unicode(self.conditional)
        
class WhileInstruction():
    
    def __init__(self, conditional, instructions):
        self.conditional = conditional
        self.instructions = instructions
        
    def __unicode__(self):
        return u"while (%s) ..." % unicode(self.conditional)

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
        self._channels_map = {}
        
    def clone(self):
        p = HostProcess(self.original_name(), self.instructions_list)
        p.all_channels_active = self.all_channels_active
        p.active_channels = self.active_channels
        return p
        
    def original_name(self):
        """"""
        return original_name(self.name)
        
    def add_name_index(self, index):
        """
        Add index to the name. 
        Before: name = ch, index = 1. After: name = ch.1
        """
        self.name += ".%d" % index
        
    def connect_with_channel(self, channel):
        """
        Assigns channel to this host.
        """
        if channel.original_name() not in self._channels_map:
            self._channels_map[channel.original_name()] = []
        if channel in self._channels_map[channel.original_name()]:
            return
        self._channels_map[channel.original_name()].append(channel)
        channel.connect_with_host(self)
    
    def find_channel(self, name):
        """
        Search for and retuen assigned channel by name (including indexes)
        """
        original_channel_name = original_name(name)
        indexes = name_indexes(name)

        if original_channel_name not in self._channels_map:
            return None
        channels = self._channels_map[original_channel_name]
        if len(channels) == 0:
            return None
        
        for ch in channels:
            # Check if channels has the same original name
            if ch.original_name() == name:
                i = 0
                #Check if channels have the same indexes
                ch_indexes = ch.indexes()
                while i < len(indexes):
                    if indexes[i] != ch_indexes[i]:
                        break
                    i += 1
                # If while loop was broken
                if i < len(indexes):
                    continue
                else:
                    # All indexes were the same
                    return ch
        return None
        
    def __unicode__(self):
        return u"process %s" % unicode(self.name)
        
        self._channels_map = {}
        
        
class Host():
    
    def __init__(self, name, schedule_algorithm, instructions_list, predefined_values=[]):
        self.name = name
        self.schedule_algorithm = schedule_algorithm
        self.instructions_list = instructions_list
        self.predefined_values = predefined_values
        self.all_channels_active = False
        self.active_channels = []
        
        self.variables = {}
        self._channels_map = {}
        self._scheduler = None
        
    def __unicode__(self):
        return u"host %s" % unicode(self.name)
        
    def clone(self):
        h = Host(self.original_name(), self.schedule_algorithm, self.instructions_list, self.predefined_values)
        h.all_channels_active = self.all_channels_active
        h.active_channels = self.active_channels
        return h
        
    def original_name(self):
        """"""
        return original_name(self.name)
        
    def add_name_index(self, index):
        """
        Add index to the name. 
        Before: name = ch, index = 1. After: name = ch.1
        """
        self.name += ".%d" % index
        
    def set_scheduler(self, scheduler):
        """Set scheduler"""
        self._scheduler = scheduler
        
    def set_variable(self, name, value):
        """Set hotst's variable"""
        self.variables[name]= value
        
    def connect_with_channel(self, channel):
        """
        Assigns channel to this host.
        """
        if channel.original_name() not in self._channels_map:
            self._channels_map[channel.original_name()] = []
        if channel in self._channels_map[channel.original_name()]:
            return
        self._channels_map[channel.original_name()].append(channel)
        channel.connect_with_host(self)
    
    def find_channel(self, name):
        """
        Search for and retuen assigned channel by name (including indexes)
        """
        original_channel_name = original_name(name)
        indexes = name_indexes(name)

        if original_channel_name not in self._channels_map:
            return None
        channels = self._channels_map[original_channel_name]
        if len(channels) == 0:
            return None
        
        for ch in channels:
            # Check if channels has the same original name
            if ch.original_name() == name:
                i = 0
                #Check if channels have the same indexes
                ch_indexes = ch.indexes()
                while i < len(indexes):
                    if indexes[i] != ch_indexes[i]:
                        break
                    i += 1
                # If while loop was broken
                if i < len(indexes):
                    continue
                else:
                    # All indexes were the same
                    return ch
        return None
        
    

################################
#        Versions
################################

class Version():
    
    def __init__(self, number):
        self.number = number
        self.run_hosts = []
        
    def __unicode__(self):
        return u"version %d" % self.number
    
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
    