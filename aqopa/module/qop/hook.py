#!/usr/bin/env python

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
        #     print "qop_arguments:"+str(instruction.qop_arguments)
        #     for i in instruction.arguments:
        #         print "QoP args:"+str(i.identifier)

        if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction,
                                     IfInstruction, WhileInstruction]:
            return

        self._update_all_facts(context)
        self._update_occured_facts(context)
        return ExecutionResult()

    ####################################
    #           ALL FACTS              #
    ####################################

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

    def _get_all_facts_details_for_expression(self, context, expression):
        if isinstance(expression, TupleExpression):
            return self._get_all_facts_details_for_tuple_expression(context, expression)
        elif isinstance(expression, CallFunctionExpression):
            return self._get_all_facts_details_for_simple_expression(context, expression)
        elif isinstance(expression, ComparisonExpression):
            return self._get_all_facts_details_for_comparison_expression(context, expression)
        elif isinstance(expression, IdentifierExpression) :
            return self._get_all_facts_details_for_identifier_expression(context, expression)
        return []

    def _get_all_facts_details_for_tuple_expression(self, context, expression):
        qop_args = []
        for i in range(0, len(expression.elements)):
            print " expression.elements[i] = " + str( expression.elements[i])
            qop_arg = self._get_occured_facts_details_for_expression(context, expression.elements[i])
            qop_args.extend(qop_arg)
        return qop_args

    def _get_all_facts_details_for_simple_expression(self, context, expression):
        qop_args = []
        #for expr in expression.arguments:
        for expr in expression.qop_arguments:
            qop_args.append(self._get_all_facts_details_for_expression(context, expr))
        return qop_args

    def _get_all_facts_details_for_comparison_expression(self, context, expression):
        qop_args = []
        qop_args.extend(self._get_all_facts_details_for_expression(context, expression.left))
        qop_args.extend(self._get_all_facts_details_for_expression(context, expression.right))
        print "expression.left = " + str(expression.left)
        print "expression.right = " + str(expression.right)

    def _get_all_facts_details_for_identifier_expression(self, context, expression):
        return expression.identifier

    ####################################
    #           OCCURED FACTS          #
    ####################################

    def _update_occured_facts(self, context):
        """
        Update occured facts in context according to current instruction.
        """

        # get current instruction
        instruction = context.get_current_instruction()

        # some kind of debugging
        #print "_update_occured_facts"

    def _get_occured_facts_details_for_expression(self, context, expression):
        if isinstance(expression, TupleExpression):
            #print "TupleExpression _get_occured_facts_details_for_expression"
            return self._get_occured_facts_details_for_tuple_expression(context, expression)
        elif isinstance(expression, CallFunctionExpression):
            #print "CallFunctionExpression _get_occured_facts_details_for_expression"
            return self._get_occured_facts_details_for_simple_expression(context, expression)
        elif isinstance(expression, ComparisonExpression):
            #print "ComparisonExpression _get_occured_facts_details_for_expression"
            return self._get_occured_facts_details_for_comparison_expression(context, expression)
        return []

    def _get_occured_facts_details_for_tuple_expression(self, context, expression):
        qop_args = []
        for i in range(0, len(expression.elements)):
            qop_arg = self._get_occured_facts_details_for_expression(context, expression.elements[i])
            qop_args.extend(qop_arg)
            # some kind of debugging
            #print "_get_occured_facts_details_for_tuple_expression : " + str(qop_arg)
        return qop_args

    def _get_occured_facts_details_for_simple_expression(self, context, expression):
        qop_args = []
        for expr in expression.arguments:
            qop_arg = self._get_occured_facts_details_for_expression(context, expr)
            qop_args.extend(qop_arg)
            # some kind of debugging
            print "_get_occured_facts_details_for_simple_expression : " + str(qop_arg)
        return qop_args

    def _get_occured_facts_details_for_comparison_expression(self, context, expression):
        pass