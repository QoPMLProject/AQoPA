'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.model import original_name, name_indexes,\
    CommunicationInstruction, TupleExpression, ComparisonExpression, COMPARISON_TYPE_EQUAL, CallFunctionExpression
from aqopa.simulator.error import RuntimeException


class ChannelMessage():
    """
    Message sent through channel.
    """
    
    def __init__(self, sender, expression, expression_checker, expression_populator, expression_reducer):
        self.sender = sender  # The host that sent the expression
        self.expression = expression  # The sent expression
        self.expression_checker = expression_checker  # checker used to check if message passes given filters
        self.expression_populator = expression_populator #
        self.expression_reducer = expression_reducer

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
                if not self.expression_checker.result(cmp_expr, self.sender,
                                                      self.expression_populator,
                                                      self.expression_reducer):
                    return False
        return True


class ChannelMessageRequest():
    """
    Representation of hosts' requests for messages.
    """
    
    def __init__(self, receiver, communication_instruction):
        """ """
        self.receiver = receiver
        self.instruction = communication_instruction


class Channel():
    """
    Simulation channel.
    """
    
    def __init__(self, name, buffer_size):
        self.name = name
        self._buffer_size = buffer_size   # Size of buffer, negative means that buffer is unlimited,
                                                    # zero means that channel is asynhronous 
        
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

    def is_waiting_for_message(self, request):
        """
        Returns True if channel is waiting for message.
        """
        for i in range(0, len(self._waiting_requests)):
            waiting_request = self._waiting_requests[i]
            if waiting_request.instruction == request.instruction and waiting_request.receiver == request.receiver:
                return True
        return False

    def wait_for_message(self, request):
        """
        Add host to the queue of hosts waiting for messages.
        Host can wait for many expressions.
        """
        if not self.is_connected_with_host(request.receiver):
            raise RuntimeException("Channel '%s' is not connected with host '%s'." % (self.name, request.receiver.name))
        
        if not self.is_waiting_for_message(request):
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
        
    def _bind_sent_expressions_with_receivers(self):
        """
        Checks if have any messages and requests and if yes, bind them.
        """
        checked_hosts = []
        for request in self._waiting_requests:
            # If receiver has been already checked in this function call
            # omit his next requests (FIFO)
            if request.receiver in checked_hosts:
                continue
            checked_hosts.append(request.receiver)

            needed_expressions_nb = len(request.instruction.variables_names)
            filters = request.instruction.filters

            found_msgs = []
            for message in self._sent_messages:
                # Omit messages that has been used by host
                if message.is_used_by_host(request.receiver):
                    continue

                # Check if message passes the filters
                if not message.pass_filters(filters):
                    continue

                found_msgs.append(message)

                # Stop loop if all needed expressions are found
                if len(found_msgs) >= needed_expressions_nb:
                    break

            # If, after loop, all needed expressions are found
            # use them by receiver
            if len(found_msgs) >= needed_expressions_nb:
                for i in range(0, needed_expressions_nb):
                    message = found_msgs[i]
                    request.receiver.set_variable(request.instruction.variables_names[i],
                                                  message.expression)
                    message.use_by_host(request.receiver)
                
                request.receiver.get_instructions_context_of_instruction(request.instruction)\
                    .goto_next_instruction()
                request.receiver.mark_changed()
            
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
        self.topologies = {}
        
    def add_topology(self, name, topology):
        self.topologies[name] = topology
        
    def has_topology(self, name):
        return name in self.topologies
        
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

    def build_message(self, sender, expression, expression_checker,
                      expression_populator, expression_reducer):
        """
        Creates a message that will be sent.
        """
        return ChannelMessage(sender, expression, expression_checker,
                              expression_populator, expression_reducer)

    def build_message_request(self, receiver, communication_instruction,
                              expression_populator, expression_reducer):
        """
        Creates a request for message when host executes instruction IN
        """
        filters = []
        for f in communication_instruction.filters:
            if isinstance(f, CallFunctionExpression):
                filters.append(expression_populator.populate(f, receiver, expression_reducer))
            else:
                filters.append(f)
        return ChannelMessageRequest(receiver, communication_instruction)
    
    