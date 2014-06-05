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

        self.not_for_requests = []  # List of requests that this expression should not been used by

    def cancel_for_request(self, request):
        self.not_for_requests.append(request)

    def is_for_request(self, request):
        return request not in self.not_for_requests

    def is_used(self):
        return len(self.not_for_hosts)

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
        self.is_waiting = True
        self.receiver = receiver
        self.instruction = communication_instruction
        self.expression_populator = expression_populator  # populator used to populate current version of filters
        self.assigned_message = None

    def get_populated_filters(self):
        """
        Get list of filters with populated expressions - ready for comparison.
        """
        filters = []
        for f in self.instruction.filters:
            if f == '*':
                filters.append(f)
            else:
                filters.append(self.expression_populator.populate(f, self.receiver))
        return filters

    def clean(self):
        self.is_waiting = False
        self.assigned_message = None

    def start_waiting(self):
        self.is_waiting = True

    def get_message_from_buffer(self, buffer):
        """
        Adds messages from the given list and returns number of added messages.
        """
        # Get messages only if receiver is actually waiting
        filters = self.get_populated_filters()
        if self.is_waiting:
            if self.assigned_message is None and len(buffer) > 0:
                for message in buffer:
                    # Check if message passes the filters
                    if not message.pass_filters(filters):
                        continue
                    self.assigned_message = message
                    buffer.remove(message)
                    return True
        return False

    def ready_to_fulfill(self):
        """
        Return True when request has as many messages as he is waiting for.
        """
        return self.assigned_message is not None

    def fulfill(self):
        """
        Assigns requested variables with received messages.
        """
        if not self.ready_to_fulfill():
            raise RuntimeException("Request of host {0} in instruction {1} is not ready to fulfill."
                                   .format(self.receiver.name, unicode(self.instruction)))

        # Set variable sent in message
        self.receiver.set_variable(self.instruction.variable_name, self.assigned_message.expression.clone())

        # Move instructions context to the next instruction
        self.receiver.get_instructions_context_of_instruction(self.instruction)\
            .goto_next_instruction()
        self.receiver.mark_changed()


class Channel():
    """
    Simulation channel.
    """
    
    def __init__(self, name, buffer_size, tag_name=None):
        self.name = name
        self.tag_name = tag_name
        self._buffer_size = buffer_size   # Size of buffer, negative means that buffer is unlimited,
                                          # zero means that channel is asynhronous
        self._connected_hosts = []  # List of hosts that can use this channel
        self._connected_processes = []  # List of processes that can use this channel
        self._buffers = {}  # Hosts' buffers - the host is the key, the list of sent messages is the value

        self._waiting_requests = []
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

    def get_buffer_for_host(self, host):
        """
        Returns the content of buffer assigned to host.
        """
        if host not in self._buffers:
            self._buffers[host] = []
        return self._buffers[host]

    def get_existing_request_for_instruction(self, receiver, instruction):
        """
        Returns request on which channel is waiting for message or None if it is not waiting.
        """
        for i in range(0, len(self._waiting_requests)):
            request = self._waiting_requests[i]
            if request.instruction == instruction and request.receiver == receiver:
                return request
        return None

    def is_waiting_on_instruction(self, receiver, instruction):
        """
        Returns True if channel is waiting for message.
        """
        request = self.get_existing_request_for_instruction(receiver, instruction)
        if request:
            return request.is_waiting
        return False

    def wait_for_message(self, request):
        """
        Add host to the queue of hosts waiting for messages.
        Host can wait for many expressions.
        """
        if not self.is_connected_with_host(request.receiver):
            raise RuntimeException("Channel '%s' is not connected with host '%s'." % (self.name, request.receiver.name))

        # Check if this request already exists
        existing_request = self.get_existing_request_for_instruction(request.receiver, request.instruction)

        # If it does not exist add
        if not existing_request:
            self._waiting_requests.append(request)
        else:
            # If request exists, check if it is waiting on IN instruction now
            if not existing_request.is_waiting:
                # If it is now (request stays in channel only to fill the buffer) start waiting on this request
                existing_request.start_waiting()

        # Check if request can be bound with expressions
        self._bind_messages_with_receivers()

    def get_filtered_requests(self, message, router):
        """
        Returns list of requests that can accept the message
        """
        requests = []
        for request in self._waiting_requests:
            # Check if there is a link between sender and receiver
            if not router.link_exists(self, message.sender, request.receiver):
                continue
            # Check if message has not been declined for waiting host
            if not message.is_for_request(request):
                continue
            # Check if message passes the filters
            filters = request.get_populated_filters()
            if not message.pass_filters(filters):
                continue
            requests.append(request)
        return requests

    def get_filtered_messages(self, request, router):
        """
        Returns list of messages from buffer that can be assigned to request
        """
        messages = []
        buffer = self.get_buffer_for_host(request.receiver)
        filters = request.get_populated_filters()
        for message in buffer:
            # Check if there is a link between sender and receiver
            if not router.link_exists(self, message.sender, request.receiver):
                continue
            # Check if message passes the filters
            if not message.pass_filters(filters):
                continue
            messages.append(message)
        return messages

    def send_message(self, sender_host, message, router):
        """
        Accept message with expressions.
        """
        if not self.is_connected_with_host(sender_host):
            raise RuntimeException("Channel '%s' is not connected with host '%s'." % (self.name, sender_host.name))

        # Put sent message in the buffers of receivers
        # Receivers are retrieved from the requests present in the channel
        # When the channel is synchronous the buffers are cleaned after the binding try
        # and requests are removed after they are fulfilled
        for request in self.get_filtered_requests(message, router):
            if request.receiver not in self._buffers:
                self._buffers[request.receiver] = []
            self._buffers[request.receiver].append(message)

        # Check if request can be bound with expressions
        self._bind_messages_with_receivers()

    def _bind_messages_with_receivers(self):
        """
        Assign messages from buffers to requests.
        """
        # Update all requests
        for request in self._waiting_requests:
            # Add messages from buffer to request
            # Add not more that request wants (it is one message)
            if request.receiver not in self._buffers:
                self._buffers[request.receiver] = []
            request.get_message_from_buffer(self._buffers[request.receiver])

            # Here the request is filled with all requested messages
            # or there was not enough messages in the buffer

            # If the request is filled with all requested messages = ready to fulfill
            if request.ready_to_fulfill():
                # Fulfill it
                request.fulfill()

                # If channel is synchronous, delete the request - a new one will be created
                # when the intruction is executed again
                if self.is_synchronous():
                    self._waiting_requests.remove(request)
                else:
                    # If channel is asynchronous, clean the request - still accept messages to the buffer
                    request.clean()

        # Clean buffers if channel is synchronous
        if self.is_synchronous():
            for i in self._buffers:
                self._buffers[i] = []

class Manager():
    """ Channels manager class """
    
    def __init__(self, channels):
        self.channels = channels
        self.router = Router()

    def add_medium(self, name, topology, default_parameters):
        self.router.add_medium(name, topology, default_parameters)
        
    def has_medium(self, name):
        return self.router.has_medium(name)

    # def add_algorithm(self, name, algorithm):
    #     self.algorithm_resolver.add_algorithm(name, algorithm)
    #
    # def has_algorithm(self, name):
    #     return self.algorithm_resolver.has_algorithm(name)
    #
    # def get_algorithm(self, name):
    #     return self.algorithm_resolver.get_algorithm(name)

    def get_router(self):
        return self.router

    # def get_algorithm_resolver(self):
    #     return self.algorithm_resolver

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


class Router():
    
    def __init__(self):

        self.mediums = {}     # { MEDIUM_NAME -> {
                              #  'default_q' -> ...,
                              #  'default_...' -> ...,
                              #  'default_...' -> ...,

                              #  'topology' ->
                              #     { SENDER -> {
                              #         'hosts': [HOST, HOST, ...]
                              #         'q': { HOST -> QUALITY, HOST -> QUALITY, ... },
                              #         PARAMETER: { HOST -> QUALITY, HOST -> QUALITY, ... },
                              #         ...
                              #     } }
                              #  }
                              # }

        self.routing = {}  # { MEDIUM_NAME ->
                           #    SENDER -> {
                           #        NEXT -> [RECEIVER1, RECEIVER2, ...),
                           #        ...
                           #    }
                           # }
        
    def add_medium(self, name, topology, default_parameters):
        self.mediums[name] = {
            'topology': topology,
            'default_parameters': default_parameters}
                                      # { MEDIUM_NAME -> {
                                      #  'default_parameters' -> {
                                      #   'default_q' -> ...,
                                      #   'default_...' -> ...,
                                      #   'default_...' -> ...,
                                      #  }
                                      #
                                      #  'topology' ->
                                      #     { SENDER -> {
                                      #         'hosts': [HOST, HOST, ...]
                                      #         'q': { HOST -> QUALITY, HOST -> QUALITY, ... }
                                      #         PARAMETER: { HOST -> VALUE, HOST -> VALUE, ... },
                                      #         ...
                                      #     } }
                                      #  }
                                      # }
        self.routing[name] = {}  # SENDER -> {
                                 #     NEXT -> [RECEIVER1, RECEIVER2, ...),
                                 #     ...
                                 # }
        
    def has_medium(self, name):
        return name in self.mediums

    def link_exists(self, channel, sender, receiver):
        """
        Returns True if there exists a link between sender and receiver.
        If communication structure exists the link must be specified. If channel medium has no structure it is assumed
        that channel may be used by all hosts.
        """
        medium_name = channel.tag_name
        if medium_name not in self.mediums:
            return True
        topology = self.mediums[medium_name]['topology']
        if len(topology) == 0:
            return True
        return self.get_link_quality(medium_name, sender, receiver) is not None

    def get_link_parameter_value(self, parameter, medium_name, sender, receiver=None, default=None, no_link_value=None):
        """
        Returns value of parameter between sender and receiver in medium.
        When receiver is None the parameter is get for situation when sender is broadcasting.
        """
        def topology_default():
            defaults = self.mediums[medium_name]['default_parameters']
            default_parameter_name = 'default_'+parameter
            if default_parameter_name in defaults:
                return defaults[default_parameter_name]
            return default
        if medium_name not in self.mediums:
            return default
        medium = self.mediums[medium_name]
        if len(medium['topology']) == 0:
            return default
        if sender not in medium['topology']:
            return no_link_value

        sender_hosts = medium['topology'][sender]['hosts']
        sender_topology = medium['topology'][sender]['parameters']
        if parameter not in sender_topology:
            if receiver in sender_hosts:
                return topology_default()
            else:
                return no_link_value
        sender_parameters = sender_topology[parameter]
        if receiver not in sender_parameters:
            if receiver in sender_hosts:
                return topology_default()
            else:
                return no_link_value
        return sender_parameters[receiver]

    def get_link_quality(self, medium_name, sender, receiver, default=1, no_link_value=None):
        """ """
        return self.get_link_parameter_value('q', medium_name, sender, receiver, default=default,
                                             no_link_value=no_link_value)

    def get_sender_links_qualities(self, medium_name, sender, exclude_broadcast=False):
        """ """
        medium = self.mediums[medium_name]
        if sender not in medium['topology']:
            return {}
        default_quality = 1
        defaults = medium['default_parameters']
        if 'default_q' in defaults:
            default_quality = defaults['default_q']
        sender_topology = medium['topology'][sender]
        sender_qualities = sender_topology['q'] if 'q' in sender_topology else {}
        qualities = {}
        for h in sender_topology['hosts']:
            if h is None and exclude_broadcast:
                continue
            if h in sender_qualities:
                qualities[h] = sender_qualities[h]
            else:
                qualities[h] = default_quality
        return qualities

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

    def get_hosts_sending_to_receiver(self, medium_name, receiver):
        """
        Returns ditictionary:
         host -> quality
        containing hosts that can send message to receiver.
        """
        if not self.has_medium(medium_name):
            return {}
        hosts = {}
        for sender in self.mediums[medium_name]['topology']:

            q = self.get_link_quality(medium_name, sender, receiver)
            if q is not None:
                hosts[sender] = q
        return hosts

    def get_next_hop_host(self, medium_name, sender, receiver):
        """
        Returns the next host which is in the path between sender and receiver.
        If path does not exist, None is returned.
        """
        # Check if path already exists
        existing_next_hop = self._find_existing_next_hop_host(medium_name, sender, receiver)
        if existing_next_hop is not None:
            return existing_next_hop

        # Build path using Dijsktra algorithm
        topology = self.mediums[medium_name]['topology']

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
                qualities = self.get_sender_links_qualities(medium_name, closest, exclude_broadcast=True)
                for next_host in qualities:
                    if (next_host not in distances) \
                            or ((closes_distance + qualities[next_host]) < distances[next_host]):
                        distances[next_host] = closes_distance + qualities[next_host]
            out.append(closest)
            closest, closes_distance = find_closest_host(distances, out)

        # for h in distances:
        #     print h.name, distances[h]

        def update_paths(medium_name, receiver, distances):
            routing = self.routing[medium_name]
            # Start from receiver
            current_host = receiver
            distance = distances[receiver]
            # Add receiver to path
            hosts_path = [receiver]
            # Repeat until we finish handling sender
            while distance > 0:
                # Find all hosts that are connected with current host
                previous_hosts = self.get_hosts_sending_to_receiver(medium_name, current_host)
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

#        Printer().print_routing(self.routing[topology_name])

        if receiver not in distances:
            raise RuntimeException("The path between {0} and {1} undefined.".format(sender.name, receiver.name))

        update_paths(medium_name, receiver, distances)
        return self._find_existing_next_hop_host(medium_name, sender, receiver)


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




