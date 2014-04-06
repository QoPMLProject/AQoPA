from aqopa.model import original_name, CallFunctionExpression

###############################
#    PREDEFINED FUNCTIONS
###############################

# Function ID
from aqopa.simulator.error import RuntimeException


def _predefined_id_function__populate(call_function_expression, host, populator, reducer):
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


def _predefined_id_function__clone(call_function_expression):
    cloned = call_function_expression.clone()
    setattr(cloned, '_host_name', getattr(call_function_expression, '_host_name', None))
    return cloned


def _predefined_id_function__are_equal(left, right):
    if left.function_name != right.function_name:
        return False
    left_host_name = getattr(left, '_host_name', None)
    right_host_name = getattr(right, '_host_name', None)
    if left_host_name is None or right_host_name is None:
        return False
    return left_host_name == right_host_name

###############################
#    PREDEFINED MANAGEMENT
###############################

functions_map = {
    'id': {
        'populate': _predefined_id_function__populate,
        'clone': _predefined_id_function__clone,
        'compare': _predefined_id_function__are_equal
    }
}


def is_function_predefined(function_name):
    return function_name in functions_map


def populate_call_function_expression_result(call_function_expression, host, populator, reducer):
    fun_name = call_function_expression.function_name
    if not is_function_predefined(fun_name):
        return call_function_expression
    return functions_map[fun_name]['populate'](call_function_expression, host, populator, reducer)


def clone_call_function_expression(call_function_expression):
    fun_name = call_function_expression.function_name
    if not is_function_predefined(fun_name):
        return call_function_expression.clone()
    return functions_map[fun_name]['clone'](call_function_expression)


def are_equal_call_function_expressions(left, right):
    if not isinstance(left, CallFunctionExpression) or not isinstance(right, CallFunctionExpression):
        raise RuntimeException("Trying to compare predefined functions expressions, but they are not.")
    return functions_map[left.function_name]['are_equal'](left, right)

