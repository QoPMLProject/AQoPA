#!/usr/bin/env python

from .qop_param import QoPParameter
from aqopa.simulator.state import Hook, ExecutionResult
from aqopa.model import AssignmentInstruction,\
    CallFunctionInstruction, IfInstruction, WhileInstruction,\
    CommunicationInstruction, CallFunctionExpression, TupleExpression, ComparisonExpression, \
    IdentifierExpression

"""
@file       hook.py
@author     Katarzyna Mazur
"""

class PreInstructionHook(Hook):

    """
    Execution hook executed before default core execution of each instruction.
    Returns execution result.
    """

    # its static, cause we need to have the list for EVERY
    # simulator and its hosts, right?
    all_facts = []

    def __init__(self, module, simulator):
        self.module = module
        self.simulator = simulator

    def execute(self, context, **kwargs):
        instruction = context.get_current_instruction()

        # temp - test me!
        # if instruction.__class__ is CallFunctionInstruction:
        #     print "function_name: "+str(instruction.function_name)
        #     print "arguments: "+str(instruction.arguments)
        #     print "qop_arguments: "+str(instruction.qop_arguments)
        #     for i in instruction.arguments:
        #         print "qop_argument:"+str(i.identifier)

        if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction,
                                     IfInstruction, WhileInstruction]:
            return

        self._update_occured_facts(context)
        self._update_all_facts(context)
        return ExecutionResult()

    def _update_occured_facts(self, context):
        """
        Update all facts in context according to current instruction.
        """

        # get current instruction
        instruction = context.get_current_instruction()

        # check the instruction type and extract the expression from it
        if isinstance(instruction, AssignmentInstruction):
            expression = instruction.expression
        elif isinstance(instruction, CallFunctionInstruction):
            expression = CallFunctionExpression(instruction.function_name, instruction.arguments, instruction.qop_arguments)
        else:
            expression = instruction.condition

        # Return details for each expression in instruction
        # In some instruction may be more expressions (tuple, nested call function)
        fact = self._get_occured_facts_details_for_expression(context, expression)

        # add fact to the module's fact list
        self.module.add_occured_fact(self.simulator, context.get_current_host(), fact)

    def _get_occured_facts_details_for_expression(self, context, expression):
        if isinstance(expression, TupleExpression):
            return self._get_occured_facts_details_for_tuple_expression(context, expression)
        elif isinstance(expression, CallFunctionExpression):
            return self._get_occured_facts_details_for_simple_expression(context, expression)
        elif isinstance(expression, ComparisonExpression):
            return self._get_occured_facts_details_for_comparison_expression(context, expression)
        return []

    def _get_occured_facts_details_for_tuple_expression(self, context, expression):
        qop_args = []
        for i in range(0, len(expression.elements)):
            qop_arg = self._get_occured_facts_details_for_expression(context, expression.elements[i])
            if type(qop_arg) is list :
                qop_args.extend(qop_arg)
            else:
                qop_args.append(qop_arg)
        return qop_args

    def _get_occured_facts_details_for_simple_expression(self, context, expression):
        qop_args = []
        for expr in expression.qop_arguments:
            #e = self._get_occured_facts_details_for_expression(context, expr)
            qop_args.append(str(expr))
        return qop_args

    def _get_occured_facts_details_for_comparison_expression(self, context, expression):
        qop_args = []
        l = self._get_occured_facts_details_for_expression(context, expression.left)
        r = self._get_occured_facts_details_for_expression(context, expression.right)
        if type(l) is list :
            qop_args.extend(l)
        else:
            qop_args.append(l)
        if type(r) is list :
            qop_args.extend(r)
        else:
            qop_args.append(r)
        return qop_args

    def _update_all_facts(self, context):
        # make a list from all the facts within the simulator and its hosts,
        # simply concatenate all the facts from all the simulators and its all
        # hosts into a one, big list of facts available within the loaded model
        facts = self.module.get_occured_facts(self.simulator, context.get_current_host())
        for fact in facts:
            if fact not in PreInstructionHook.all_facts:
                PreInstructionHook.all_facts.append(fact)
        self.module.set_all_facts(PreInstructionHook.all_facts)