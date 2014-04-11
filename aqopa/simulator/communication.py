'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import copy
import sys
from aqopa.model import original_name, name_indexes,\
    CommunicationInstruction, TupleExpression, ComparisonExpression, COMPARISON_TYPE_EQUAL, CallFunctionExpression
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
        self.router = Router()
        
    def add_topology(self, name, topology):
        self.router.add_topology(name, topology)
        
    def has_topology(self, name):
        return self.router.has_topology(name)
    
    def get_router(self):
        return self.router
    
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
        filters = []
        for f in communication_instruction.filters:
            if isinstance(f, CallFunctionExpression):
                filters.append(expression_populator.populate(f, receiver))
            else:
                filters.append(f)
        return ChannelMessageRequest(receiver, communication_instruction)
    
    
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

        def update_paths(topology_name, sender, distances):
            topology = self.topologies[topology_name]
            routing = self.routing[topology_name]

            hosts_to_update = [(sender, distances[sender], [sender])]
            while len(hosts_to_update) > 0:
                # Get element from the en of list (FIFO)
                current_host_tuple = hosts_to_update.pop()
                current_host = current_host_tuple[0]
                current_distance = current_host_tuple[1]
                current_path = copy.copy(current_host_tuple[2])

                if current_host in topology:
                    host_topology = topology[current_host]
                    for next_host in host_topology['quality']:
                        # If is on the shortest path
                        if next_host in distances \
                                and (distances[next_host] == current_distance + host_topology['quality'][next_host]):
                            current_path.append(next_host)

                            # Insert next host to
                            hosts_to_update.insert(0, (next_host, distances[next_host], current_path))

                            # Add all possible connection in the path
                            for i in range(0, len(current_path)-1):
                                from_host = current_path[i]
                                nxt_host = current_path[i+1]
                                to_host = current_path[-1]
                                if from_host not in routing:
                                    routing[from_host] = {}
                                if nxt_host not in routing[from_host]:
                                    routing[from_host][nxt_host] = []
                                if to_host not in routing[from_host][nxt_host]:
                                    routing[from_host][nxt_host].append(to_host)


#
#        Printer().print_routing(self.routing[topology_name])
#

        update_paths(topology_name, sender, distances)
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




