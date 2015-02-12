#!/bin/env/python

import copy
#from aqopa.simulator.error import RuntimeException

'''
Created on 23-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

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
        
    def clone(self):
        return Function(copy.copy(self.name), copy.deepcopy(self.qop_params), copy.copy(self.comment))
        
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
    
    def __init__(self, name, buffor_size, tag_name=None):
        self.name = name
        self.buffor_size = buffor_size # Buffor size < 0 is unlimited
        self.tag_name = tag_name

    def __unicode__(self):
        buffor_size = str(self.buffor_size) if self.buffor_size >= 0 else "*"
        return u"channel %s [%s]" % (self.name, buffor_size)
    
    def clone(self):
        return Channel(copy.copy(self.name), copy.copy(self.buffor_size))

class Equation():
    
    def __init__(self, simple, composite):
        self.simple = simple
        self.composite = composite
        
    def __unicode__(self):
        return u"eq %s = %s" % ( unicode(self.composite), unicode(self.simple) )
    
    def clone(self):
        return Equation(self.simple.clone(), self.composite.clone())
    
################################
#        Expressions
################################
    
class BooleanExpression():
    
    def __init__(self, val):
        self.val = bool(val)
        
    def clone(self):
        return BooleanExpression(copy.copy(self.val))
        
    def __unicode__(self):
        return u"true" if self.val else u"false"
    
    def is_true(self):
        return self.val
    
class IdentifierExpression():
    
    def __init__(self, identifier):
        self.identifier = identifier
        
    def __unicode__(self):
        return unicode(self.identifier)
    
    def clone(self):
        return IdentifierExpression(copy.copy(self.identifier))
    
class CallFunctionExpression():
    
    def __init__(self, function_name, arguments=[], qop_arguments=[]):
        self.function_name = function_name
        self.arguments = arguments
        self.qop_arguments = qop_arguments
        
    def __unicode__(self):
        u = u"%s(%s)" % (unicode(self.function_name), unicode(', '.join([unicode(a) for a in self.arguments])))
        if len(self.qop_arguments) > 0:
            u += "[%s]" % unicode(', '.join([unicode(a) for a in self.qop_arguments]))
        return u

    def clone(self):
        # Regular clone
        expr = CallFunctionExpression(copy.copy(self.function_name),
                                      [a.clone() for a in self.arguments],
                                      [copy.copy(a) for a in self.qop_arguments])

        # Copy additional values (may come from predefined functions or keep calculated size, etc.)
        regular_vars = ['function_name', 'arguments', 'qop_arguments']
        for attr_name in self.__dict__:
            if attr_name not in regular_vars:
                setattr(expr, attr_name, copy.deepcopy(self.__dict__[attr_name]))
        return expr


COMPARISON_TYPE_EQUAL = 1
COMPARISON_TYPE_NOT_EQUAL = 2

class ComparisonExpression():
    
    def __init__(self, left, right, comparison_type):
        self.left = left
        self.right = right
        self.comparison_type = comparison_type
        
    def __unicode__(self):
        return "%s %s %s" % (unicode(self.left), u'==' if self.is_equal_type() else '!=',
                             unicode(self.right))

    def is_equal_type(self):
        return self.comparison_type == COMPARISON_TYPE_EQUAL
    
    def clone(self):
        return ComparisonExpression(self.left.clone(), self.right.clone(), self.comparison_type)
    
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
        return TupleElementExpression(copy.copy(self.variable_name),
                                      copy.copy(self.index))
      
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
    
    def clone(self):
        return CallFunctionInstruction(copy.copy(self.function_name), 
                                      [ a.clone() for a in self.arguments ],
                                      [ copy.copy(a) for a in self.qop_arguments ])
        
class FinishInstruction():
    
    def __init__(self, command):
        self.command = command
        
    def clone(self):
        return FinishInstruction(copy.copy(self.command))
        
    def __unicode__(self):
        return "%s;" % unicode(self.command)
    
class ContinueInstruction():
    
    def clone(self):
        return ContinueInstruction()
    
    def __unicode__(self):
        return u"continue;"

class BreakInstruction():

    def clone(self):
        return BreakInstruction()

    def __unicode__(self):
        return u"break;"
    
class AssignmentInstruction():
    
    def __init__(self, variable_name, expression):
        self.variable_name = variable_name
        self.expression = expression
        
    def clone(self):
        return AssignmentInstruction(copy.copy(self.variable_name), 
                                     self.expression.clone())
        
    def __unicode__(self):
        return u"%s = %s;" % (unicode(self.variable_name), unicode(self.expression))


class CommunicationInstruction():
    
    def __init__(self, communication_type, channel_name, variable_name, filters):
        self.communication_type = communication_type
        self.channel_name = channel_name
        self.variable_name = variable_name
        self.filters = filters
        
    def clone(self):
        filters = []
        for f in self.filters:
            if isinstance(f, basestring):
                filters.append(copy.copy(f))
            else:
                filters.append(f.clone())
        return CommunicationInstruction(copy.copy(self.communication_type),
                                        copy.copy(self.channel_name), 
                                        copy.copy(self.variable_name),
                                        filters)
        
    def is_out(self):
        return self.communication_type == COMMUNICATION_TYPE_OUT
        
    def __unicode__(self):
        if self.communication_type == COMMUNICATION_TYPE_IN:
            filters_str = u""
            if len(self.filters) > 0:
                filters_str = u", ".join([unicode(f) for f in self.filters])
                filters_str = u": |%s|" % filters_str
            return u"in (%s: %s%s);" % (unicode(self.channel_name),
                                        unicode(self.variable_name),
                                        filters_str)
        else:
            return u"out (%s: %s);" % (unicode(self.channel_name), unicode(self.variable_name))


class IfInstruction():
    
    def __init__(self, condition, true_instructions, false_instructions=[]):
        self.condition = condition
        self.true_instructions = true_instructions
        self.false_instructions = false_instructions
        
    def clone(self):
        t_instructions = []
        for i in self.true_instructions:
            t_instructions.append(i.clone())
        f_instructions = []
        for i in self.false_instructions:
            f_instructions.append(i.clone())
        return IfInstruction(self.condition.clone(), t_instructions, f_instructions)
        
    def __unicode__(self):
        return u"if (%s) ..." % unicode(self.condition)
        
class WhileInstruction():
    
    def __init__(self, condition, instructions):
        self.condition = condition
        self.instructions = instructions
        
    def __unicode__(self):
        return u"while (%s) ..." % unicode(self.condition)

    def clone(self):
        instructions = []
        for i in self.instructions:
            instructions.append(i.clone())
        return WhileInstruction(self.condition.clone(), instructions)
        
################################
#        Hosts
################################

class HostSubprocess():
    
    def __init__(self, name, instructions_list):
        self.name = name
        self.instructions_list = instructions_list
        self.all_channels_active = False
        self.active_channels = []
        
    def clone(self):
        
        instructions_list = []
        for i in self.instructions_list:
            instructions_list.append(i.clone())
        
        p = HostSubprocess(copy.copy(self.name), instructions_list)
        p.all_channels_active = copy.copy(self.all_channels_active)
        p.active_channels = copy.deepcopy(self.active_channels)
        return p
        
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
        
        instructions_list = []
        for i in self.instructions_list:
            instructions_list.append(i.clone())
        
        p = HostProcess(copy.copy(self.name), instructions_list)
        p.all_channels_active = copy.copy(self.all_channels_active)
        p.active_channels = copy.deepcopy(self.active_channels)
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
        
        predefined_values = []
        for i in self.predefined_values:
            predefined_values.append(i.clone())
        
        h = Host(copy.copy(self.name), copy.copy(self.schedule_algorithm), instructions_list, predefined_values)
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
        self.metrics_sets = []
        self.communication = {'mediums': {}}
        
    def __unicode__(self):
        return u"version %d" % self.name
    
    def clone(self):
        r_hosts = []
        for rh in self.run_hosts:
            r_hosts.append(rh.clone())
        m_sets = []
        for ms in self.metrics_sets:
            m_sets.append(ms.clone())
        v = Version(copy.copy(self.name))
        v.run_hosts = r_hosts
        v.metrics_sets = m_sets
        return v
    
class VersionRunHost():
    
    def __init__(self, host_name):
        self.host_name = host_name
        self.all_channels_active = False
        self.active_channels = []
        self.repetitions = 1
        self.repeated_channels = [] # deprecated
        self.run_processes = []
        
    def __unicode__(self):
        return u"run host %s (...)" % self.host_name
    
    def clone(self):
        r_processes = []
        for rp in self.run_processes:
            r_processes.append(rp.clone())
        rh = VersionRunHost(copy.copy(self.host_name))
        rh.all_channels_active = self.all_channels_active
        rh.active_channels = copy.deepcopy(self.active_channels)
        rh.repetitions = self.repetitions
        rh.repeated_channels = copy.deepcopy(self.repeated_channels)
        rh.run_processes = r_processes
        return rh
    
class VersionRunProcess():
    
    def __init__(self, process_name):
        self.process_name = process_name
        self.all_subprocesses_active = False
        self.active_subprocesses = []
        self.repetitions = 1
        self.repeated_channels = [] # deprecated
        self.follower = None
        
    def __unicode__(self):
        s = u"run %s (...)" % self.process_name
        if self.follower:
            s += " -> %s" % unicode(self.follower)
        return s
    
    def clone(self):
        rp = VersionRunProcess(copy.copy(self.process_name))
        rp.all_subprocesses_active = self.all_subprocesses_active
        rp.active_subprocesses = copy.deepcopy(self.active_subprocesses)
        rp.repetitions = self.repetitions
        rp.repeated_channels = copy.deepcopy(self.repeated_channels)
        if self.follower:
            rp.follower = self.follower.clone()
        return rp

################################
#        Metrics
################################

class MetricsConfiguration():
    
    def __init__(self, name, specifications):
        self.name = name
        self.specifications = specifications
        
    def __unicode__(self):
        return u"conf %s { ... }" % self.name
    
    def clone(self):
        return MetricsConfiguration(copy.copy(self.name), copy.deepcopy(self.specifications))

class MetricsSet():
    
    def __init__(self, host_name, configuration_name):
        self.host_name = host_name
        self.configuration_name = configuration_name
    
    def __unicode__(self):
        return u"set host %s (%s) { ... }" % (self.host_name, self.configuration_name)
    
    def clone(self):
        return MetricsSet(copy.copy(self.host_name), copy.copy(self.configuration_name))
        
class MetricsData():
    
    def __init__(self, name, blocks, plus = False, star = False):
        self.name = name
        self.blocks = blocks
        self.star = star
        self.plus = plus
        
    def __unicode__(self):
        return u"data %s { ... }" % self.name
        
    def clone(self):
        blocks = []
        for b in self.blocks:
            blocks.append(b.clone())
        return MetricsData(copy.copy(self.name), blocks, copy.copy(self.plus), copy.copy(self.star))
        
class MetricsPrimitiveBlock():
    
    def __init__(self, header, metrics):
        self.header = header
        self.metrics = metrics
        
    def clone(self):
        metrics = []
        for m in self.metrics:
            metrics.append(m.clone())
        return MetricsPrimitiveBlock(self.header.clone(), metrics)
        
class MetricsPrimitiveHeader():
    
    def __init__(self, params, services_params):
        self.params = params
        self.services_params = services_params
        
    def clone(self):
        params = []
        for p in self.params:
            params.append(p.clone())
        s_params = []
        for p in self.services_params:
            s_params.append(p.clone())
        return MetricsPrimitiveHeader(params, s_params)
    
class MetricsServiceParam():
    
    def __init__(self, service_name, param_name, unit=None):
        self.service_name = service_name
        self.param_name = param_name
        self.unit = unit
        
    def clone(self):
        return MetricsServiceParam(copy.copy(self.service_name),
                                   copy.copy(self.param_name),
                                   copy.copy(self.unit))
        
class MetricsPrimitive():
    
    def __init__(self, arguments):
        self.arguments = arguments
        
    def clone(self):
        return MetricsPrimitive(copy.deepcopy(self.arguments))
      
################################
#        Communication
################################

class TopologyRuleHost():
    
    def __init__(self, identifier, index_range=None, i_shift=None):
        self.identifier = identifier
        self.index_range = index_range
        self.i_shift = i_shift

    def __unicode__(self):
        s = self.identifier
        if self.index_range is not None:
            s += "["
            if self.index_range[0] is not None:
                s += str(self.index_range[0])
            s += ":"
            if self.index_range[1] is not None:
                s += str(self.index_range[1])
            s += "]"
        elif self.i_shift is not None:
            s += "[i"
            if self.i_shift >= 0:
                s += "+"
            s += str(self.i_shift) + "]"
        return unicode(s)

class TopologyRule():
    
    def __init__(self, left_host, arrow, right_host, parameters=None):
        self.left_host = left_host
        self.right_host = right_host
        self.arrow = arrow
        self.parameters = parameters if parameters is not None else {}

    def __unicode__(self):
        params_list = []
        for p in self.parameters:
            params_list.append(u"{0}={1}".format(p, self.parameters[p]))
        params_str = u""
        if len(params_list) > 0:
            params_str = u" : " + u", ".join(params_list)
        right_host_str = u"*"
        if self.right_host is not None:
            right_host_str = unicode(self.right_host)
        return u"{0} {1} {2}{3};".format(unicode(self.left_host), self.arrow, right_host_str, params_str)
      
################################
#       Algorithms
################################

class AlgCallFunction():
    
    def __init__(self, function_name, args):
        self.function_name = function_name
        self.args = args
        
class AlgWhile():
    
    def __init__(self, condition, instructions):
        self.condition = condition
        self.instructions = instructions
        
class AlgIf():
    
    def __init__(self, condition, true_instructions, false_instructions):
        self.condition = condition
        self.true_instructions = true_instructions
        self.false_instructions = false_instructions
        
class AlgReturn():
    
    def __init__(self, expression):
        self.expression = expression
        
class AlgAssignment():
    
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression
    