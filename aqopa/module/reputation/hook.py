'''
Created on 27-12-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from math import ceil
import random
from aqopa.module.reputation.algorithm import update_vars
from aqopa.simulator.state import Hook, ExecutionResult
from aqopa.model import AssignmentInstruction,\
    CallFunctionInstruction, IfInstruction, WhileInstruction,\
    CommunicationInstruction, CallFunctionExpression, TupleExpression, ComparisonExpression
from aqopa.module.timeanalysis.error import TimeSynchronizationException
from aqopa.simulator.error import RuntimeException

class PreInstructionHook(Hook):
    """
    Execution hook executed before default core execution of each instruction.
    Returns execution result.
    """
    
    def __init__(self, module, simulator):
        """ """
        self.module = module
        self.simulator = simulator

    def _prepare_host_variables(self, host):
        """
        Assign the init vars to host if not yet done.
        """
        if host in self.module.reputation_vars:
            return

        self.module.reputation_vars[host] = {}
        for v in self.module.init_vars:
            self.module.reputation_vars[host][v] = self.module.init_vars[v]
        
    def execute(self, context, **kwargs):
        """
        """
        instruction = context.get_current_instruction()
        if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction,
                                         IfInstruction, WhileInstruction]:
            return
        
        expression = None
        if isinstance(instruction, AssignmentInstruction):
            expression = instruction.expression
        elif isinstance(instruction, CallFunctionInstruction):
            expression = CallFunctionExpression(instruction.function_name,
                                                instruction.arguments,
                                                instruction.qop_arguments)
        else:
            expression = instruction.condition

        self._update_vars(context, expression)

        return ExecutionResult()
            
    def _update_vars(self, context, expression):
        """ 
        Update reputation variables in host according to current instruction.
        """

        if isinstance(expression, CallFunctionExpression):
            self._update_vars_simple(context, expression)
        elif isinstance(expression, TupleExpression):
            self._update_vars_tuple(context, expression)
        elif isinstance(expression, ComparisonExpression):
            self._update_vars_comparison(context, expression)

    def _update_vars_simple(self, context, expression):
        """
        Update reputation variables in host according to call function expression.
        """

        # Firstly update vars according to nested call functions
        for e in expression.arguments:
            self._update_vars(context, e)

        # Now update vars according to current call function
        host = context.get_current_host()
        self._prepare_host_variables(host)

        metric_expression = CallFunctionExpression(
            expression.function_name, expression.arguments, []
        )
        metric = context.metrics_manager\
            .find_primitive(host, metric_expression)

        if metric:
            block = metric.block

            algorithm_name = None
            for i in range(0, len(block.service_params)):
                sparam = block.service_params[i]

                if sparam.service_name.lower() != "reputation":
                    continue

                metric_type = sparam.param_name.lower()
                metric_value = metric.service_arguments[i]

                if metric_type == "algorithm":
                    algorithm_name = metric_value
                    break

            if algorithm_name:
                algorithm = self.module.get_algorithm(algorithm_name)

                if len(expression.qop_arguments) != len(algorithm['parameters']):
                    raise RuntimeException('Reputation algorithm "%s" required %d parameters, %d given.'
                                           % (algorithm_name, len(algorithm['parameters']),
                                              len(expression.qop_arguments)))

                vars = self.module.get_host_vars(host)
                i = 0
                for qop_arg in expression.qop_arguments:
                    try:
                        val = float(qop_arg)
                        vars[algorithm['parameters'][i]] = val
                        i += 1
                    except ValueError:
                        raise RuntimeException('Reputation argument "%s" in expression "%s" not a float number.'
                                               % (qop_arg, unicode(expression)))

                vars = update_vars(host, algorithm['instructions'], vars)

                for var_name in self.module.init_vars:
                    self.module.set_reputation_var(host, var_name, vars[var_name])

    def _update_vars_tuple(self, context, expression):
        """
        Update reputation variables in host according to tuple expression.
        """
        # Update vars according to tuple elements
        for e in expression.elements:
            self._update_vars(context, e)


    def _update_vars_comparison(self, context, expression):
        """
        Update reputation variables in host according to comparison expression.
        """
        # Update vars according to compared expressions
        self._update_vars(context, expression.left)
        self._update_vars(context, expression.right)
