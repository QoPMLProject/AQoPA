#!/usr/bin/env python

from aqopa.simulator.state import Hook, ExecutionResult
from aqopa.model import AssignmentInstruction,\
    CallFunctionInstruction, IfInstruction, WhileInstruction,\
    CommunicationInstruction, CallFunctionExpression, TupleExpression, ComparisonExpression

"""
@file       hook.py
@author     Katarzyna Mazur
"""


class PreInstructionHook(Hook):

    """
    Execution hook executed before default core execution of each instruction.
    Returns execution result.
    """

    def __init__(self, module, simulator):
        """ """
        self.module = module
        self.simulator = simulator

    def execute(self, context, **kwargs):
        """
        """
        instruction = context.get_current_instruction()

        # temp - test me!
        # if instruction.__class__ is CallFunctionInstruction:
        #     print "QoP function_name:"+str(instruction.function_name)
        #     print "QoP arguments:"+str(instruction.qop_arguments)
        #     for i in instruction.arguments:
        #         print "QoP args:"+str(i.identifier)

        if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction,
                                     IfInstruction, WhileInstruction]:
            return

        self._update_all_facts(context)
        self._update_occured_facts(context)
        return ExecutionResult()

    def _update_all_facts(self, context):
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
        fact = self._get_all_facts_details_for_expression(context, expression)

        # add fact to the module's fact list
        self.module.add_new_fact(self.simulator, context.get_current_host(), fact)

        # some kind of debugging
        #print "_update_all_facts"

    def _get_all_facts_details_for_expression(self, context, expression):
        if isinstance(expression, TupleExpression):
            return self._get_all_facts_details_for_tuple_expression(context, expression)
        elif isinstance(expression, CallFunctionExpression):
            return self._get_all_facts_details_for_simple_expression(context, expression)
        elif isinstance(expression, ComparisonExpression):
            return self._get_all_facts_details_for_comparison_expression(context, expression)
        return []

    def _get_all_facts_details_for_tuple_expression(self, context, expression):
        pass

    def _get_all_facts_details_for_simple_expression(self):
        pass

    def _get_all_facts_details_for_comparison_expression(self):
        pass

    def _update_occured_facts(self, context):
        """
        Update occured facts in context according to current instruction.
        """

        # get current instruction
        instruction = context.get_current_instruction()

        # some kind of debugging
        #print "_update_occured_facts"

    def _get_occured_facts_details_for_expression(self, context, expression):
        pass