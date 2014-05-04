from aqopa.model import original_name, CallFunctionExpression,\
    IdentifierExpression
from aqopa.simulator.error import RuntimeException

###############################
#    PREDEFINED FUNCTIONS
###############################


# Function ID


def _predefined_id_function__populate(call_function_expression, host, populator, context=None):
    existing_host_name = getattr(call_function_expression, '_host_name', None)
    if existing_host_name is not None:
        return call_function_expression
    arguments = call_function_expression.arguments
    if len(arguments) == 0:
        expr_host_name = host.name
    else:
        expr_host_name = arguments[0].identifier
        if expr_host_name == original_name(expr_host_name):
            expr_host_name += ".0"
    setattr(call_function_expression, '_host_name', expr_host_name)
    return call_function_expression


def _predefined_id_function__are_equal(left, right):
    if left.function_name != right.function_name:
        return False
    left_host_name = getattr(left, '_host_name', None)
    right_host_name = getattr(right, '_host_name', None)
    if left_host_name is None or right_host_name is None:
        return False
    return left_host_name == right_host_name


# Function routing_next


def _predefined_routing_next_function__populate(call_function_expression, host, populator, context=None):

    topology_name = call_function_expression.arguments[0].identifier

    receiver_function_id_expression = populator.populate(call_function_expression.arguments[1], host)
    receiver_function_id_expression = _predefined_id_function__populate(receiver_function_id_expression, 
                                                                        host, populator)
    receiver_name = getattr(receiver_function_id_expression, '_host_name')
    
    receiver = None
    for h in context.hosts:
        if h.name == receiver_name:
            receiver = h
            break
         
    sender = host
    sender_name = sender.name
    if len(call_function_expression.arguments) > 2:
        sender_function_id_expression = populator.populate(call_function_expression.arguments[2], host)
        sender_function_id_expression = _predefined_id_function__populate(sender_function_id_expression, 
                                                                          host, populator)
        sender_name = getattr(sender_function_id_expression, '_host_name')
        if sender_name != sender.name:
            sender = None
            for h in context.hosts:
                if h.name == sender_name:
                    sender = h
                    break
    
    if sender is None:
        raise RuntimeException("Host '%s' undefined." % sender_name)
    if receiver is None:
        raise RuntimeException("Host '%s' undefined." % receiver_name)

    if sender == receiver:
        next_host = receiver
    else:
        next_host = context.channels_manager.get_router().get_next_hop_host(topology_name, sender, receiver)
        if next_host is None:
            raise RuntimeException("The route from host '%s' to host '%s' cannot be found."
                                   % (sender_name, receiver_name))
    # DEBUG
    # print host.name, ': ', unicode(call_function_expression), ' -> ', next_host.name
    # DEBUG
            
    id_function = CallFunctionExpression('id', arguments=[IdentifierExpression(next_host.name)])
    setattr(id_function, '_host_name', next_host.name)
    return id_function


###############################
#    PREDEFINED MANAGEMENT
###############################

class FunctionsManager():
    
    def __init__(self, context):
        self.context = context
        self.functions_map = {
                'id': {
                    'populate': _predefined_id_function__populate,
                    'are_equal': _predefined_id_function__are_equal
                },
                'routing_next': {
                    'populate': _predefined_routing_next_function__populate,
                    'are_equal': None
                }
            }

    def is_function_predefined(self, function_name):
        return function_name in self.functions_map
    
    def populate_call_function_expression_result(self, call_function_expression, host, populator):
        fun_name = call_function_expression.function_name
        if not self.is_function_predefined(fun_name):
            return call_function_expression
        return self.functions_map[fun_name]['populate'](call_function_expression, host, populator, context=self.context)

    def are_equal_call_function_expressions(self, left, right):
        if not isinstance(left, CallFunctionExpression) or not isinstance(right, CallFunctionExpression):
            raise RuntimeException("Trying to compare predefined functions expressions, but they are not.")
        return self.functions_map[left.function_name]['are_equal'](left, right)
    
