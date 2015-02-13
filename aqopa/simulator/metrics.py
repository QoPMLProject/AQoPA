'''
Created on 14-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.simulator.error import RuntimeException
from aqopa.model import TupleExpression, CallFunctionExpression, CallFunctionInstruction, IdentifierExpression, TupleElementExpression


class HostMetrics():
    """
    Whole metrics configuration for particular hosts.
    Configuration includes the name, the device configuration params,
    three types of metrics: normal, plus and star.
    """
    def __init__(self, name):
        self.name = name
        self.configurations = []
        
        self.normal_blocks = []
        self.plus_blocks = []
        self.star_blocks = []
        
        self.connected_hosts = []
        
    def is_connected_with_host(self, host):
        """ """
        return host in self.connected_hosts

class Block():
    """
    Block of metrics containing all metrics with the same params 
    and service params definition.
    """
    def __init__(self, params, service_params):
        self.params = params
        self.service_params = service_params
        self.metrics = []

    def add_metric(self, metric):
        """ """
        self.metrics.append(metric)
        metric.block = self
        
    def find_primitives(self, function_name, qop_arguments):
        """ """
        if len(qop_arguments) < len(self.params):
            return []
        
        found_metrics = []
        for m in self.metrics:
            if m.function_name != function_name:
                continue
            
            params_ok = True
            for i in range(0, len(m.arguments)):
                if qop_arguments[i] != m.arguments[i]:
                    params_ok = False

            if not params_ok:
                continue

            found_metrics.append(m)

        return found_metrics


class Metric():
    """
    One metrics row with defined: call arguments and service arguments.
    Call arguments are used for metric lookup and service arguments are used
    to define new state or by modules to calculate some informations.
    """
    def __init__(self, function_name, arguments, service_arguments):
        self.function_name = function_name
        self.arguments = arguments
        self.service_arguments = service_arguments   
        self.block = None 

class Manager():
    """
    Metrics manager. 
    Class used for operations on metrics: searching, etc.
    """
    def __init__(self, host_metrics):
        self.host_metrics = host_metrics
        
    def find_primitive(self, host, call_function_expression):
        """
        Method finds metric for function call in host.
        Method searches the metric in three kinds: normal, plus and star.
        If more than one metrics is found, runtime exception is raised. 
        """
        found_host_metric = None
        for host_metric in self.host_metrics:
            if host_metric.is_connected_with_host(host):
                found_host_metric = host_metric
                break
            
        if not found_host_metric:
            return None
        
        normal_metrics = []
        plus_metrics = []
        star_metrics = []

        if len(found_host_metric.normal_blocks) > 0:
            for mb in found_host_metric.normal_blocks:
                if len(mb.params) <= len(call_function_expression.qop_arguments):
                    normal_metrics.extend(mb.find_primitives(
                        call_function_expression.function_name,
                        call_function_expression.qop_arguments))
        
        if len(found_host_metric.plus_blocks) > 0:
            for mb in found_host_metric.plus_blocks:
                if len(mb.params) <= len(call_function_expression.qop_arguments):
                    plus_metrics.extend(mb.find_primitives(
                        call_function_expression.function_name,
                        call_function_expression.qop_arguments))
        
        if len(found_host_metric.star_blocks) > 0:
            for mb in found_host_metric.star_blocks:
                if len(mb.params) <= len(call_function_expression.qop_arguments):
                    star_metrics.extend(mb.find_primitives(
                        call_function_expression.function_name,
                        call_function_expression.qop_arguments))
                
        if len(normal_metrics) + len(plus_metrics) + len(star_metrics) > 1:
            raise RuntimeException("Found many metrics for function '%s' with qopanalysis arguments: %s." \
                                   % (call_function_expression.function_name,
                                      ', '.join(call_function_expression.qop_arguments)))
        
        if len(normal_metrics) > 0:
            return normal_metrics[0]
        if len(plus_metrics) > 0:
            return plus_metrics[0]
        if len(star_metrics) > 0:
            return star_metrics[0]
        return None
        
        
    def get_expression_size(self, expression, context, host):
        """
        Returns the size in bytes of expression according to metrics.
        Metrics van specify exact size (ie. in bytes, bits, kilobytes, kilobits, megabytes, megabits)
        or ratio size (ie. 0.5 equals 50%) used ie. in compression.
        Expression cannot have variables - it must be filled with variables' values.
        """
        size = 0

        if isinstance(expression, IdentifierExpression):
            # If expression is an variable, get its value size
            return self.get_expression_size(host.get_variable(expression.identifier), context, host)

        if isinstance(expression, TupleElementExpression):
            variable = host.get_variable(expression.variable_name)
            variable = context.expression_reducer.reduce(variable)
            if not isinstance(variable, TupleExpression):
                raise RuntimeException('Cannot get tuple element on expression: %s.' % unicode(variable))
            return self.get_expression_size(variable.elements[expression.index], context, host)

        elif isinstance(expression, TupleExpression):
            # If expression is tuple, just sum its elements' sizes
            for expr in expression.elements:
                size += self.get_expression_size(expr, context, host)
            return size    
            
        if isinstance(expression, CallFunctionExpression) or isinstance(expression, CallFunctionInstruction):
            expression = context.expression_reducer.reduce(expression)
            metric = self.find_primitive(host, expression)
            
            if not metric:
                raise RuntimeException("Cannot get expression size: No metric found for expression '%s'." 
                                       % unicode(expression))

            block = metric.block
            for i in range(0, len(block.service_params)):
                sparam = block.service_params[i]

                if sparam.service_name.lower() != "size":
                    continue
                
                metric_type = sparam.param_name.lower()
                metric_unit = sparam.unit
                metric_value = metric.service_arguments[i]
            
                if metric_type == "ratio":
                    mparts = metric_value.split(':')
                    element_index = int(mparts[0])-1
                    percent = float(mparts[1])
                    
                    size = self.get_expression_size(expression.arguments[element_index], context, host) \
                            * percent
                elif metric_type == "sum_ratio":
                    ratios = metric_value.split(',')
                    size = 0.0
                    for ratio in ratios:
                        rparts = ratio.strip().split(':')
                        element_index = int(rparts[0])-1
                        percent = float(rparts[1])

                        size += self.get_expression_size(expression.arguments[element_index], context, host) \
                                * percent
                elif metric_type == "exact":
                    if metric_unit == 'B':
                        size = float(metric_value)
                    elif metric_unit == 'b':
                        size = float(metric_value)/8.0
                    else:
                        raise RuntimeException('Cannot get expression size: Unsupported size value for exact type.')

                elif metric_type == "block":
                    mparts = metric_value.split(':')
                    element_index = int(mparts[0])-1
                    unit_value = int(mparts[1])

                    factor = 1.0
                    if metric_unit == 'b':
                        factor = 1.0 / 8.0

                    argument_size = self.get_expression_size(expression.arguments[element_index], context, host)
                    argument_size_excess = argument_size % unit_value

                    size = argument_size
                    if argument_size_excess > 0:
                        size += unit_value - argument_size_excess
                    size *= factor

                elif metric_type == "nested":
                    mparts = metric_value.split(':')
                    element_index = int(mparts[0])-1
                    nested_element_index = int(mparts[1])-1

                    nested_expression = expression.arguments[element_index]

                    if isinstance(nested_expression, IdentifierExpression):
                        nested_expression = host.get_variable(nested_expression.identifier)

                    if not isinstance(nested_expression, CallFunctionExpression) and \
                        not isinstance(nested_expression, CallFunctionInstruction):
                        raise RuntimeException('Cannot get nested expression size: Not a function call.')

                    size = self.get_expression_size(nested_expression.arguments[nested_element_index], context, host)

                else:
                    raise RuntimeException('Cannot get expression size: Unsupported size type.')

                return size
        raise RuntimeException('Cannot get expression size: Unsupported expression type. Expression: {0}.'
                               .format(unicode(expression)))