'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import copy
from aqopa.model import CommunicationInstruction, TupleExpression, ComparisonExpression, COMPARISON_TYPE_EQUAL, \
    CallFunctionExpression, AlgWhile, AlgReturn, AlgIf, AlgAssignment, AlgCallFunction
from aqopa.simulator.error import RuntimeException


class ChannelMessage():
    """
    Message sent through channel.
    """
    
    def __init__(self, sender, expression, expression_checker):
        self.sender = sender  # The host that sent the expression
        self.expression = expression  # The sent expression
        self.expression_checker = expression_checker  # checker used to check if message passes given filters

        self.given_to_hosts = []  # List of hosts that this expression has been given to

    def use_by_host(self, host):
        self.given_to_hosts.append(host)

    def is_used_by_host(self, host):
        return host in self.given_to_hosts

    def is_used(self):
        return len(self.given_to_hosts)

    def pass_filters(self, filters):
        """
        Returns True if message passes all given filters
        """
        if len(filters) == 0:
            return True
        else:
            if not isinstance(self.expression, TupleExpression) \
                    or (len(self.expression.elements) < len(filters)):
                return False

        for i in range(0, len(filters)):
            f = filters[i]
            if isinstance(f, basestring):  # star - accept everything
                continue
            else:
                cmp_expr = ComparisonExpression(f, self.expression.elements[i], COMPARISON_TYPE_EQUAL)
                if not self.expression_checker.result(cmp_expr, self.sender):
                    return False
        return True


class ChannelMessageRequest():
    """
    Representation of hosts' requests for messages.
    """
    
    def __init__(self, receiver, communication_instruction, expression_populator):
        """ """
        self.receiver = receiver
        self.instruction = communication_instruction
        self.expression_populator = expression_populator  # populator used to populate current version of filters

    def get_populated_filters(self):
        filters = []
        for f in self.instruction.filters:
            if f == '*':
                filters.append(f)
            else:
                filters.append(self.expression_populator.populate(f, self.receiver))
        return filters


class Channel():
    """
    Simulation channel.
    """
    
    def __init__(self, name, buffer_size, tag_name=None):
        self.name = name
        self._buffer_size = buffer_size   # Size of buffer, negative means that buffer is unlimited,
                                                    # zero means that channel is asynhronous 
        self.tag_name = tag_name
        self._connected_hosts = []  # List of hosts that can use this channel
        self._connected_processes = []  # List of processes that can use this channel

        self._waiting_requests = []
        self._sent_messages = []
        self._dropped_messages_cnt = 0
        
    def connect_with_host(self, host):
        """
        Connect channel with host if it is not already connected.
        """
        if host in self._connected_hosts:
            return
        self._connected_hosts.append(host)

    def is_connected_with_host(self, host):
        """
        Returns True if host is connected with this channel.
        """
        return host in self._connected_hosts
        
    def connect_with_process(self, process):
        """
        Connect channel with process if it is not already connected.
        """
        if process in self._connected_processes:
            return
        self._connected_processes.append(process)
        
    def is_connected_with_process(self, process):
        """
        Returns True if process is connected with this channel.
        """
        return process in self._connected_processes

    def is_synchronous(self):
        """
        Returns True if channel is synchronous.
        """
        return self._buffer_size == 0
    
    def has_unlimited_buffer(self):
        """
        Returns True if channel has unlimited buffer.
        """
        return self._buffer_size < 0
    
    def get_dropped_messages_nb(self):
        """
        Return number of messages dropped on this channel
        """
        return self._dropped_messages_cnt

    def get_unused_messages_nb(self):
        """
        Return number of sent messages that has not been binded with any host.
        """
        nb = 0
        for message in self._sent_messages:
            if not message.is_used():
                nb += 1
        return nb

    def is_waiting_on_instruction(self, receiver, instruction):
        """
        Returns True if channel is waiting for message.
        """
        for i in range(0, len(self._waiting_requests)):
            waiting_request = self._waiting_requests[i]
            if waiting_request.instruction == instruction and waiting_request.receiver == receiver:
                return True
        return False

    def wait_for_message(self, request):
        """
        Add host to the queue of hosts waiting for messages.
        Host can wait for many expressions.
        """
        if not self.is_connected_with_host(request.receiver):
            raise RuntimeException("Channel '%s' is not connected with host '%s'." % (self.name, request.receiver.name))
        
        if not self.is_waiting_on_instruction(request.receiver, request.instruction):
            self._waiting_requests.append(request)
            
        # Check if request can be bound with expressions
        self._bind_sent_expressions_with_receivers()
    
    def send_messages(self, sender_host, messages):
        """
        Accept message with expressions.
        """
        if not self.is_connected_with_host(sender_host):
            raise RuntimeException("Channel '%s' is not connected with host '%s'." % (self.name, sender_host.name))
            
        for msg in messages:
            self._sent_messages.append(msg)
        
        # Check if request can be bound with expressions
        self._bind_sent_expressions_with_receivers()

    def get_fulfilled_requests(self, messages=None, messages_request=None, include_all_sent_messages=False):
        """
        Returns list of tuples (request, [messages that will be binded to this request]).
        The result list may contain all sent messages - not only those from optional parameter.
        """
        # We have decided that one message can be assigined to one host ONLY ONCE
        # and that the next request can be fulfilled when all previous have been fulfilled.
        # TODO: Maybe it will be worth changing later.

        all_messages = []
        all_messages.extend(self._sent_messages)
        if messages is not None:
            all_messages.extend(messages)

        all_requests = []
        all_requests.extend(self._waiting_requests)
        if messages_request is not None:
            all_requests.append(messages_request)

        def find_request_tuple(tuples, request):
            for t in tuples:
                if t[0] == request:
                    return t
            return None

        tuples = []
        checked_hosts = []
        for request in all_requests:
            # If receiver has been already checked in this function call
            # omit his next requests (FIFO)
            if request.receiver in checked_hosts:
                continue
            checked_hosts.append(request.receiver)

            needed_expressions_nb = len(request.instruction.variables_names)
            filters = request.get_populated_filters()

            found_msgs = []
            for message in all_messages:
                # Omit messages that has been used by host
                if message.is_used_by_host(request.receiver):
                    continue

                # Check if message passes the filters
                if not message.pass_filters(filters):
                    continue

                found_msgs.append(message)

                # Stop loop if all needed expressions are found
                if not include_all_sent_messages and (len(found_msgs) >= needed_expressions_nb):
                    break

            # If, after loop, all needed expressions are found
            # assign receiver to all messages
            if len(found_msgs) >= needed_expressions_nb:
                for i in range(0, len(found_msgs)):
                    message = found_msgs[i]
                    t = find_request_tuple(tuples, request)
                    if t is None:
                        t = (request, [message])
                        tuples.append(t)
                    else:
                        t[1].append(message)
        return tuples

    def _bind_sent_expressions_with_receivers(self):
        """
        Checks if have any messages and requests and if yes, bind them.
        """
        # Handle all fulfilled requests (those for which all required messages are found)
        for request, messages in self.get_fulfilled_requests(messages=None):
            # For each required expression
            needed_expressions_nb = len(request.instruction.variables_names)
            for i in range(0, needed_expressions_nb):
                message = messages[i]
                # Set variable sent in message
                request.receiver.set_variable(request.instruction.variables_names[i],
                                              message.expression.clone())
                # Set message as used by host
                message.use_by_host(request.receiver)

            # Move instructions context to the next instruction
            request.receiver.get_instructions_context_of_instruction(request.instruction)\
                .goto_next_instruction()
            request.receiver.mark_changed()

            # Remove request from list of waiting requests
            self._waiting_requests.remove(request)

        # Update sent messages list according to buffer size
        removed_messages = []
        if self.is_synchronous():
            removed_messages = self._sent_messages
            self._sent_messages = []
        elif not self.has_unlimited_buffer():
            for i in range(0, len(self._sent_messages) - self._buffer_size):
                removed_messages.append(self._sent_messages.pop(0))

        for message in removed_messages:
            if not message.is_used():
                self._dropped_messages_cnt += 1


class Manager():
    """ Channels manager class """
    
    def __init__(self, channels):
        self.channels = channels
        self.router = Router()
        self.algorithm_resolver = AlgorithmResolver()
        
    def add_topology(self, name, topology):
        self.router.add_topology(name, topology)
        
    def has_topology(self, name):
        return self.router.has_topology(name)

    def add_algorithm(self, name, algorithm):
        self.algorithm_resolver.add_algorithm(name, algorithm)

    def has_algorithm(self, name):
        return self.algorithm_resolver.has_algorithm(name)
    
    def get_router(self):
        return self.router

    def get_algorithm_resolver(self):
        return self.algorithm_resolver
    
    def find_channel(self, name, predicate=None):
        """
        """
        for ch in self.channels:
            if ch.name == name:
                if predicate is not None and not predicate(ch):
                    continue
                return ch
        return None
        
    def find_channel_for_current_instruction(self, context):
        """
        Finds channel connected with process/host from current instruction
        and with the channel name from instruction. 
        """
        instruction = context.get_current_instruction()
        if not isinstance(instruction, CommunicationInstruction):
            return None
        return self.find_channel_for_host_instruction(context, context.get_current_host(), 
                                                      instruction)
        
    def find_channel_for_host_instruction(self, context, host, instruction):
        """
        Finds channel connected with process/host from current instruction 
        of passed host and with the channel name from instruction. 
        """
        process = host.get_current_instructions_context().get_process_of_current_list()
        if process:
            return self.find_channel(instruction.channel_name,
                                     predicate=lambda x: x.is_connected_with_process(process))
        else:
            return self.find_channel(instruction.channel_name,
                                     predicate=lambda x: x.is_connected_with_host(host))

    def build_message(self, sender, expression, expression_checker):
        """
        Creates a message that will be sent.
        """
        return ChannelMessage(sender, expression, expression_checker)

    def build_message_request(self, receiver, communication_instruction,
                              expression_populator):
        """
        Creates a request for message when host executes instruction IN
        """
        return ChannelMessageRequest(receiver, communication_instruction, expression_populator)


#TODO: Move to timeanalysis module

class AlgorithmResolver():

    def __init__(self):
        self.algorithms = {}

    def add_algorithm(self, name, algorithm):
        self.algorithms[name] = algorithm

    def has_algorithm(self, name):
        return name in self.algorithms

    def get_time(self, context, host, alg_name, message_expression, link_quality=None):
        if not self.has_algorithm(alg_name):
            return 0
        alg = self.algorithms[alg_name]
        variables = {
            alg['parameter']: message_expression,
        }
        return AlgorithmCalculator(context, host, alg_name, variables,
                                   alg['instructions'], link_quality).get_time()


class AlgorithmCalculator():

    def __init__(self, context, host, algorithm_name, variables, instructions, link_quality):
        self.context = context
        self.host = host
        self.algorithm_name = algorithm_name
        self.variables = variables
        self.instructions = instructions
        self.link_quality = link_quality

        self.instructions_stack = [instructions]
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
                raise RuntimeException("Link quality is not specified in {0} algorithm. "
                                       "Do you use quality() in OUT algorithm? The link is not specified when sending."
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
        orders = [['==', '!=', '<=', '>=', '>', '<', '&&', '||'], ['*', '/'], ['--', '-', '+']]
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
            if self.calculate_value(current_instruction.condition):
                self.add_instructions_list(current_instruction.instructions)
            else:
                self.goto_next_instruction()
        elif isinstance(current_instruction, AlgIf):
            if self.calculate_value(current_instruction.condition):
                self.add_instructions_list(current_instruction.true_instructions)
            else:
                self.add_instructions_list(current_instruction.false_instructions)
        elif isinstance(current_instruction, AlgAssignment):
            self.variables[current_instruction.identifier] = self.calculate_value(current_instruction.expression)
            self.goto_next_instruction()


    def get_time(self):
        while not self.finished():
            self.execute_current_instruction()
        if self.return_value is None:
            raise RuntimeException("Algorithm {0} has no return value. Did you forget to use return instruction?"
                                   .format(self.algorithm_name))
        return self.return_value
    
class Router():
    
    def __init__(self):
        self.topologies = {}  # { TOPOLOGY_NAME ->
                              #     { SENDER -> {
                              #         'hosts': [HOST, HOST, ...]
                              #         'quality': { HOST -> QUALITY, HOST -> QUALITY, ... }
                              #     } }
                              # }
        self.routing = {}  # { TOPOLOGY_NAME ->
                           #    SENDER -> {
                           #        NEXT -> [RECEIVER1, RECEIVER2, ...),
                           #        ...
                           #    }
                           # }
        
    def add_topology(self, name, topology):
        self.topologies[name] = topology  # { SENDER -> {
                                          #         'hosts': [HOST, HOST, ...]
                                          #         'quality': { HOST -> QUALITY, HOST -> QUALITY, ... }
                                          #     }
        self.routing[name] = {}  # SENDER -> {
                                 #     NEXT -> [RECEIVER1, RECEIVER2, ...),
                                 #     ...
                                 # }
        
    def has_topology(self, name):
        return name in self.topologies

    def get_link_quality(self, topology_name, sender, receiver):
        """ """
        return self.topologies[topology_name][sender]['quality'][receiver]

    def _find_existing_next_hop_host(self, topology_name, sender, receiver):
        """
        Finds existing next hop host in the path from sender to receiver.
        If path does not exist, return None.
        """
        routing = self.routing[topology_name]
        if not sender in routing:
            return None
        sender_routing = routing[sender]
        for next_hop in sender_routing:
            if receiver in sender_routing[next_hop]:
                return next_hop
        return None

    def get_hosts_sending_to_receiver(self, topology_name, receiver):
        """
        Returns ditictionary:
         host -> quality
        containing hosts that can send message to receiver.
        """
        if not self.has_topology(topology_name):
            return {}
        hosts = {}
        for sender in self.topologies[topology_name]:
            sender_topology = self.topologies[topology_name][sender]
            if receiver in sender_topology['quality']:
                hosts[sender] = sender_topology['quality'][receiver]
        return hosts

    def get_next_hop_host(self, topology_name, sender, receiver):
        """
        Returns the next host which is in the path between sender and receiver.
        If path does not exist, None is returned.
        """
        # Check if path already exists
        existing_next_hop = self._find_existing_next_hop_host(topology_name, sender, receiver)
        if existing_next_hop is not None:
            return existing_next_hop
        # Build path using Dijsktra algorithm
        topology = self.topologies[topology_name]

        def find_closest_host(distances, out):
            closest_host = None
            d = -1
            for h in distances:
                if d < 0 or d > distances[h]:
                    if h not in out:
                        closest_host = h
                        d = distances[h]
            return closest_host, d

        # Dijsktra
        distances = {sender: 0}
        out = []
        closest, closes_distance = find_closest_host(distances, out)
        while (closest is not None) and (closest != receiver):
            if closest in topology:
                qualities = topology[closest]['quality']
                for next_host in qualities:
                    if (next_host not in distances) \
                            or ((closes_distance + qualities[next_host]) < distances[next_host]):
                        distances[next_host] = closes_distance + qualities[next_host]
            out.append(closest)
            closest, closes_distance = find_closest_host(distances, out)

        def update_paths(topology_name, receiver, distances):
            routing = self.routing[topology_name]
            # Start from receiver
            current_host = receiver
            distance = distances[receiver]
            # Add receiver to path
            hosts_path = [receiver]
            # Repeat until we finish handling sender
            while distance > 0:
                # Find all hosts that are connected with current host
                previous_hosts = self.get_hosts_sending_to_receiver(topology_name, current_host)
                for prev_host in previous_hosts:
                    # If prev host has not calculated distance, omit him
                    if prev_host not in distances:
                        continue
                    # Check if this host is on the shortest path
                    prev_quality = previous_hosts[prev_host]
                    if distances[prev_host] + prev_quality == distances[current_host]:
                        # Go one step earlier
                        current_host = prev_host
                        # Decrease current distance
                        distance -= prev_quality
                        if prev_host not in routing:
                            routing[prev_host] = {}
                        next_host = hosts_path[0]
                        if next_host not in routing[prev_host]:
                            routing[prev_host][next_host] = []
                        for i in range(0, len(hosts_path)):
                            routing[prev_host][next_host].append(hosts_path[i])
                        # Add host to path
                        hosts_path.insert(0, prev_host)
                        break
#
#        Printer().print_routing(self.routing[topology_name])
#

        update_paths(topology_name, receiver, distances)
        return self._find_existing_next_hop_host(topology_name, sender, receiver)


class Printer():

    def print_topology(self, topology):
        for sender in topology:
            snlen = len(sender.name)
            print sender.name

            for next in topology[sender]['quality']:
                print " " * snlen, ' -> ', next.name, ' : ', topology[sender]['quality'][next]

    def print_routing(self, routing):
        for sender in routing:
            snlen = len(sender.name)
            print sender.name

            for next in routing[sender]:
                nnlen = len(next.name)
                print " " * snlen, ' -> ', next.name

                for receiver in routing[sender][next]:
                    print " " * (snlen+nnlen+4), ' -> ', receiver.name




