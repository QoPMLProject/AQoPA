'''
Created on 03-04-2014

@author: damian
'''
from aqopa.model import AlgWhile, TupleExpression, AlgCallFunction, AlgReturn, AlgIf, AlgAssignment
from aqopa.simulator.error import RuntimeException


class AlgorithmResolver():

    def __init__(self):
        self.algorithms = {}

    def add_algorithm(self, name, algorithm):
        self.algorithms[name] = algorithm

    def has_algorithm(self, name):
        return name in self.algorithms

    def get_algorithm(self, name):
        return self.algorithms[name]

    def calculate(self, context, host, alg_name, variables=None):
        if not self.has_algorithm(alg_name):
            return 0
        if variables is None:
            variables = {}
        return AlgorithmCalculator(context, host, alg_name, variables, self.algorithms[alg_name]).calculate()


class AlgorithmCalculator():

    def __init__(self, context, host, algorithm_name, variables, algorithm):
        self.context = context
        self.host = host
        self.algorithm_name = algorithm_name
        self.variables = variables
        self.algorithm = algorithm
        self.instructions = algorithm['instructions']
        self.link_quality = variables['link_quality'] if 'link_quality' in variables else 1

        self.instructions_stack = [algorithm['instructions']]
        self.instructions_stack_index = 0
        self.instructions_lists_indexes = {0: 0}

        self.left_associative_operators = ['--', '-', '+', '*', '/', '==', '!=', '<=', '>=', '>', '<', '&&', '||']
        self.right_associative_operators = []
        self.all_operators = self.left_associative_operators + self.right_associative_operators

        self.return_value = None

    def get_index_in_current_list(self):
        """ Returns the index of instruction in current list """
        return self.instructions_lists_indexes[self.instructions_stack_index]

    def in_main_stack(self):
        """ Returns True when current instruction is in main stack """
        return self.instructions_stack_index == 0

    def has_current_instruction(self):
        """ """
        return self.get_index_in_current_list() < len(self.instructions_stack[self.instructions_stack_index])

    def get_current_instruction(self):
        """ Returns the instruction that should be executed next """
        return self.instructions_stack[self.instructions_stack_index][self.get_index_in_current_list()]

    def finished(self):
        """ Returns True when algorithm is finished """
        return self.return_value is not None or (not self.has_current_instruction() and self.in_main_stack())

    def goto_next_instruction(self):
        """ """
        self.instructions_lists_indexes[self.instructions_stack_index] += 1
        while not self.finished() and not self.has_current_instruction():
            self.instructions_stack.pop()
            del self.instructions_lists_indexes[self.instructions_stack_index]
            self.instructions_stack_index -= 1

            if not self.finished():
                if not isinstance(self.get_current_instruction(), AlgWhile):
                    self.instructions_lists_indexes[self.instructions_stack_index] += 1

    def add_instructions_list(self, instructions):
        """ Adds new instructions list to the stack """
        self.instructions_stack.append(instructions)
        self.instructions_stack_index += 1
        self.instructions_lists_indexes[self.instructions_stack_index] = 0

    def calculate_function_value(self, call_function_instruction):
        if call_function_instruction.function_name == 'size':
            var_name = call_function_instruction.args[0]
            if var_name not in self.variables:
                raise RuntimeException("Variable {0} not defined in communication algorithm {1}."
                                       .format(var_name, self.algorithm_name))
            value = self.variables[var_name]
            # If tuple element expression
            if len(call_function_instruction.args) > 1:
                if not isinstance(value, TupleExpression):
                    raise RuntimeException("Variable {0} in communication algorithm {1} is not tuple, it is: {2}."
                                           .format(var_name, self.algorithm_name, unicode(value)))
                index = call_function_instruction.args[1]
                if len(value.elements) <= index:
                    raise RuntimeException("Variable {0} in communication algorithm {1} has "
                                           "{2} elements while index {3} is asked."
                                           .format(var_name, self.algorithm_name, len(value.elements), index))
                value = value.elements[index]
            return self.context.metrics_manager.get_expression_size(value, self.context, self.host)
        elif call_function_instruction.function_name == 'quality':
            if self.link_quality is None:
                raise RuntimeException("Link quality is undefined in {0} algorithm. "
                                       .format(self.algorithm_name))
            return self.link_quality
        raise RuntimeException("Unresolved reference to function {0}() in algorithm {1}."
                               .format(call_function_instruction.function_name, self.algorithm_name))

    def _is_operation_token(self, token):
        return isinstance(token, basestring) and token in self.all_operators

    def _operator_order(self, operator):
        """
        Returns the order of operator as number.
        """
        orders = [['==', '!=', '<=', '>=', '>', '<', '&&', '||'], ['--', '-', '+'], ['*', '/']]
        for i in range(0, len(orders)):
            if operator in orders[i]:
                return i
        raise RuntimeException("Operator {0} undefined in algorithm {1}.".format(operator, self.algorithm_name))

    def _make_rpn(self, expression):
        """ """
        stack = []
        rpn = []
        for token in expression:
            # if operator
            if self._is_operation_token(token):
                while len(stack) > 0:
                    top_operator = stack[len(stack)-1]
                    # if current operator is left-associative and its order is lower or equal than top operator
                    # or current operator is right-associative and its order is lower than top operator
                    if (token in self.left_associative_operators
                            and self._operator_order(token) <= self._operator_order(top_operator))\
                       or (token in self.right_associative_operators
                            and self._operator_order(token) < self._operator_order(top_operator)):
                        rpn.append(stack.pop())
                    else:
                        break
                stack.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                found_paran = False
                while len(stack) > 0:
                    top_operator = stack[len(stack)-1]
                    if top_operator == '(':
                        found_paran = True
                        stack.pop()
                        break
                    else:
                        rpn.append(stack.pop())
                if not found_paran:
                    raise RuntimeException("Incorrect number of brackets in algorithm {0}.".format(self.algorithm_name))
            else:  # else number
                if isinstance(token, AlgCallFunction):
                    token = self.calculate_function_value(token)
                elif isinstance(token, basestring):
                    if token not in self.variables:
                        raise RuntimeException("Variable {0} not defined in communication algorithm {1}."
                                               .format(token, self.algorithm_name))
                    token = self.variables[token]
                rpn.append(float(token))
        while len(stack) > 0:
            rpn.append(stack.pop())
        return rpn

    def _calculate_operation(self, operator, left, right):
        """ """
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            return left / right
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '>=':
            return left >= right
        elif operator == '>':
            return left > right
        elif operator == '<=':
            return left <= right
        elif operator == '<':
            return left < right
        else:
            raise RuntimeException("Incorrect operator {0} of brackets in algorithm {1}."
                                   .format(operator, self.algorithm_name))

    def _calculate_rpn(self, rpn_elements):
        """ """
        stack = []
        for token in rpn_elements:
            # if operator
            if self._is_operation_token(token):
                if token == '--':
                    value = stack.pop()
                    value = - value
                    stack.append(value)
                else:
                    a = stack.pop()
                    b = stack.pop()
                    stack.append(self._calculate_operation(token, b, a))
            else:  # number
                stack.append(token)
        return stack.pop()

    def calculate_value(self, expression):
        rpn_elements = self._make_rpn(expression)
        return self._calculate_rpn(rpn_elements)

    def execute_current_instruction(self):
        current_instruction = self.get_current_instruction()
        if isinstance(current_instruction, AlgReturn):
            self.return_value = self.calculate_value(current_instruction.expression)
            self.goto_next_instruction()
        elif isinstance(current_instruction, AlgWhile):
            if len(current_instruction.instructions) > 0 and self.calculate_value(current_instruction.condition):
                self.add_instructions_list(current_instruction.instructions)
            else:
                self.goto_next_instruction()
        elif isinstance(current_instruction, AlgIf):
            if self.calculate_value(current_instruction.condition):
                instructions = current_instruction.true_instructions
            else:
                instructions = current_instruction.false_instructions
            if len(instructions) > 0:
                self.add_instructions_list(instructions)
            else:
                self.goto_next_instruction()
        elif isinstance(current_instruction, AlgAssignment):
            self.variables[current_instruction.identifier] = self.calculate_value(current_instruction.expression)
            self.goto_next_instruction()

    def calculate(self):
        while not self.finished():
            self.execute_current_instruction()
        if self.return_value is None:
            raise RuntimeException("Algorithm {0} has no return value. Did you forget to use return instruction?"
                                   .format(self.algorithm_name))
        return self.return_value