# !/usr/bin/env python

from aqopa.model import AssignmentInstruction, \
    CallFunctionInstruction, IfInstruction, WhileInstruction, \
    CommunicationInstruction, CallFunctionExpression, TupleExpression, ComparisonExpression, \
    IdentifierExpression

"""
@file       parser.py
@brief      a parser file aka "facts finder" - finds all the facts
            that can affect the QoP (QoP params actually) in the loaded QoP-ML model
@author     Katarzyna Mazur
"""




# class FactsFinder():
#
#     def __init__(self, module, simulator):
#         self.module = module
#         self.simulator = simulator
#         self.all_facts = []
#
#     def execute(self, context):
#         instruction = context.get_current_instruction()
#         if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction,
#                                          IfInstruction, WhileInstruction]:
#             return
#         self._find_all_facts(context)
#
#     def _find_all_facts(self, context):
#         for host in context.hosts:
#             for processes in host.instructions_list:
#                 for i in processes.instructions_list:
#                     # print "i = " + str(i)
#                     if isinstance(i, AssignmentInstruction):
#                         expression = i.expression
#                     elif isinstance(i, CallFunctionInstruction):
#                         expression = CallFunctionExpression(i.function_name, i.arguments, i.qop_arguments)
#                     elif isinstance(i, CommunicationInstruction):
#                         pass
#                     else:
#                         expression = i.condition
#                     #print "expression = " + str(expression)
#                     print "_get_all_facts_details_for_expression = " + str(
#                         self._get_all_facts_details_for_expression(expression))
#
#
#     def _get_all_facts_details_for_expression(self, expression):
#         if isinstance(expression, TupleExpression):
#             return self._get_all_facts_details_for_tuple_expression(expression)
#         elif isinstance(expression, CallFunctionExpression):
#             return self._get_all_facts_details_for_simple_expression(expression)
#         elif isinstance(expression, ComparisonExpression):
#             return self._get_all_facts_details_for_comparison_expression(expression)
#         return []
#
#     def _get_all_facts_details_for_tuple_expression(self, expression):
#         qop_args = []
#         for i in range(0, len(expression.elements)):
#             print "expression.elements[i] = " + str(expression.elements[i])
#             qop_arg = self._get_all_facts_details_for_expression(expression.elements[i])
#             if type(qop_arg) is list:
#                 qop_args.extend(qop_arg)
#             else:
#                 qop_args.append(qop_arg)
#         return qop_args
#
#     def _get_all_facts_details_for_simple_expression(selfs, expression):
#         qop_args = []
#         for expr in expression.qop_arguments:
#             qop_args.append(str(expr))
#         return qop_args
#
#     def _get_all_facts_details_for_comparison_expression(self, expression):
#         qop_args = []
#         l = self._get_all_facts_details_for_expression(expression.left)
#         r = self._get_all_facts_details_for_expression(expression.right)
#         if type(l) is list:
#             qop_args.extend(l)
#         else:
#             qop_args.append(l)
#         if type(r) is list:
#             qop_args.extend(r)
#         else:
#             qop_args.append(r)
#         return qop_args