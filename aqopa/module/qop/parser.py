#!/usr/bin/env python

from aqopa.model import AssignmentInstruction, \
    CallFunctionInstruction, IfInstruction, WhileInstruction, \
    CommunicationInstruction, CallFunctionExpression, TupleExpression, ComparisonExpression, \
    IdentifierExpression

"""
@file       parser.py
@brief      a parser file aka "facts finder" - finds all the facts
            that can affect the QoP params in the loaded QoP-ML model
@author     Katarzyna Mazur
"""


class FactsFinder():
    
    def __init__(self, module, simulator):
        self.module = module
        self.simulator = simulator
        self.all_facts = []

    def execute(self, context):
        instruction = context.get_current_instruction()
        if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction,
                                         IfInstruction, WhileInstruction]:
            return
        self._find_all_facts(context)

    def _find_all_facts(self, context):
        for host in context.hosts:
            for processes in host.instructions_list:
                for expression in processes.instructions_list:
                    instruction = context.get_current_instruction()
                    if isinstance(instruction, AssignmentInstruction):
                        expression = instruction.expression
                    elif isinstance(instruction, CallFunctionInstruction):
                        expression = CallFunctionExpression(instruction.function_name, instruction.arguments,
                                                            instruction.qop_arguments)
                    else:
                        expression = instruction.condition
                    qop_arg = self._get_all_facts_details_for_expression(context, expression)
                    for arg in qop_arg:
                        if arg not in self.all_facts:
                            self.all_facts.append(arg)

        for fact in self.all_facts:
            self.module.add_new_fact(self.simulator, context.get_current_host(), fact)

    def _get_all_facts_details_for_expression(self, context, expression):
        if isinstance(expression, TupleExpression):
            return self._get_all_facts_details_for_tuple_expression(context, expression)
        elif isinstance(expression, CallFunctionExpression):
            return self._get_all_facts_details_for_simple_expression(context, expression)
        elif isinstance(expression, ComparisonExpression):
            return self._get_all_facts_details_for_comparison_expression(context, expression)
        return []

    def _get_all_facts_details_for_tuple_expression(self, context, expression):
        qop_args = []
        for i in range(0, len(expression.elements)):
            qop_arg = self._get_all_facts_details_for_expression(context, expression.elements[i])
            if type(qop_arg) is list:
                qop_args.extend(qop_arg)
            else:
                qop_args.append(qop_arg)
        return qop_args

    def _get_all_facts_details_for_simple_expression(selfs, context, expression):
        qop_args = []
        for expr in expression.qop_arguments:
            qop_args.append(str(expr))
        return qop_args

    def _get_all_facts_details_for_comparison_expression(self, context, expression):
        qop_args = []
        l = self._get_all_facts_details_for_expression(context, expression.left)
        r = self._get_all_facts_details_for_expression(context, expression.right)
        if type(l) is list:
            qop_args.extend(l)
        else:
            qop_args.append(l)
        if type(r) is list:
            qop_args.extend(r)
        else:
            qop_args.append(r)
        return qop_args