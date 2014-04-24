'''
Created on 31-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from math import ceil
import random
from aqopa.simulator.state import Hook, ExecutionResult
from aqopa.model import AssignmentInstruction,\
    CallFunctionInstruction, IfInstruction, WhileInstruction,\
    CommunicationInstruction, CallFunctionExpression, TupleExpression, ComparisonExpression, COMMUNICATION_TYPE_OUT, \
    COMMUNICATION_TYPE_IN
from aqopa.module.timeanalysis.error import TimeSynchronizationException
from aqopa.simulator.error import RuntimeException

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
        
        if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction, 
                                     IfInstruction, WhileInstruction, CommunicationInstruction]:
            return
        
        if isinstance(instruction, CommunicationInstruction):
            return self._execute_communication_instruction(context, **kwargs)
        else:
            self._update_time(context)
            return ExecutionResult()
            
    def _update_time(self, context):
        """ 
        Update times in context according to current instruction.
        """
        instruction = context.get_current_instruction()
        
        if isinstance(instruction, AssignmentInstruction):
            expression = instruction.expression
        elif isinstance(instruction, CallFunctionInstruction):
            expression = CallFunctionExpression(instruction.function_name, 
                                                instruction.arguments, 
                                                instruction.qop_arguments)
        else:
            expression = instruction.condition
            
        # Return details for each expression in instruction
        # In some instruction may be more expressions (tuple, nested call function)
        total_time, time_details = self._get_time_details_for_expression(context, expression)
        
        if total_time > 0:
            host = context.get_current_host()
            self.module.add_timetrace(self.simulator, host, host.get_current_process(),
                                      instruction, time_details,
                                      self.module.get_current_time(self.simulator, host),
                                      total_time)
            self.module.set_current_time(self.simulator, host, self.module.get_current_time(self.simulator, host) + total_time)
            
    def _get_time_details_for_expression(self, context, expression):
        """
        Returns calculated time that execution of expression takes.
        """
        if isinstance(expression, TupleExpression):
            return self._get_time_details_for_tuple_expression(context, expression)
        elif isinstance(expression, CallFunctionExpression):
            return self._get_time_details_for_simple_expression(context, expression)
        elif isinstance(expression, ComparisonExpression):
            return self._get_time_details_for_comparison_expression(context, expression)
        return 0, []

    def _get_time_details_for_tuple_expression(self, context, expression):
        """
        Calculate execution time for tuple expression. 
        """
        total_time = 0
        time_details = [] 
        for i in range(0, len(expression.elements)):
            element_total_time, element_time_details = self._get_time_details_for_expression(context, expression.elements[i])
            total_time += element_total_time
            time_details.extend(element_time_details)
        return total_time, time_details

    def _get_time_details_for_comparison_expression(self, context, expression):
        """
        Calculate execution time for tuple expression.
        """
        total_time = 0
        time_details = []

        element_total_time, element_time_details = self._get_time_details_for_expression(context, expression.left)
        total_time += element_total_time
        time_details.extend(element_time_details)

        element_total_time, element_time_details = self._get_time_details_for_expression(context, expression.right)
        total_time += element_total_time
        time_details.extend(element_time_details)

        return total_time, time_details
    
    def _get_time_details_for_simple_expression(self, context, expression):
        """
        Calculate time for expression.
        """
        time = 0
        time_details = []
        
        metric = context.metrics_manager\
            .find_primitive(context.get_current_host(), expression)

        if metric:
            block = metric.block
            
            for i in range(0, len(block.service_params)):
                sparam = block.service_params[i]
                
                if sparam.service_name.lower().strip() != "time":
                    continue

                metric_type = sparam.param_name.lower().strip()
                metric_unit = sparam.unit
                metric_value = metric.service_arguments[i].strip()

                if metric_type == "exact":

                    if metric_unit == "ms":
                        time = float(metric_value)

                    elif metric_unit == "s":
                        time = float(metric_value) * 1000

                    elif metric_unit == "mspb" or metric_unit == "mspB":

                        mparts = metric_value.split(':')
                        if len(mparts) != 2:
                            raise RuntimeException(
                                'Metric unit is set as %s, but call argument to get size of is not set.'
                                % metric_unit)

                        size = 0
                        call_params_indexes = mparts[1].split(',')
                        for index in call_params_indexes:
                            index = int(index)
                            populated_expression = context.expression_populator.populate(
                                                        expression.arguments[index-1],
                                                        context.get_current_host())

                            size += context.metrics_manager.get_expression_size(
                                                                populated_expression,
                                                                context,
                                                                context.get_current_host())

                        msperbyte = float(mparts[0])
                        if metric_unit == "mspb":
                            msperbyte = msperbyte / 8.0

                        time = msperbyte * size

                elif metric_type == "range":

                    mvalues = metric_value.split('..')
                    val_from = float(mvalues[0])
                    val_to = float(mvalues[1])

                    time = val_from + (val_to-val_from)*random.random()

                elif metric_type == "block":

                    mparts = metric_value.split(':')
                    element_index = int(mparts[0])-1
                    unit_time = float(mparts[1])
                    unit_size = int(mparts[2])

                    #time_unit = metric_unit[0]
                    size_unit = metric_unit[1]

                    argument_size = context.metrics_manager.get_expression_size(expression.arguments[element_index],
                                                                                context,
                                                                                context.get_current_host())
                    units = ceil(argument_size / float(unit_size))

                    time = units * unit_time
                    if size_unit == 'b':
                        time *= 8.0

            if time > 0:
                time_details.append((expression, time))

        for expr in expression.arguments:
            argument_time, argument_time_details = self._get_time_details_for_expression(context, expr)
            
            time += argument_time
            time_details.extend(argument_time_details)

        return time, time_details

    def _find_communication_metric(self, context, channel, host, communication_type):
        """ Returns metric for communication step. """
        qop_args = []
        if channel.tag_name is not None:
            qop_args = [channel.tag_name]
        comm_instruction = 'out' if communication_type == COMMUNICATION_TYPE_OUT else 'in'
        expression = CallFunctionExpression(comm_instruction, qop_arguments=qop_args)
        return context.metrics_manager.find_primitive(host, expression)

    def _get_time_for_communication_step(self, context, channel, host, metric, message, request=None):
        """ Returns time of sending/receiving message """
        time = 0
        block = metric.block
        for i in range(0, len(block.service_params)):
            sparam = block.service_params[i]
            if sparam.service_name.lower().strip() != "time":
                continue

            metric_type = sparam.param_name.lower().strip()
            metric_unit = sparam.unit
            metric_value = metric.service_arguments[i].strip()

            if metric_type == "exact":

                if metric_unit == "ms":
                    time = float(metric_value)

                elif metric_unit == "s":
                    time = float(metric_value) * 1000

                elif metric_unit == "mspb" or metric_unit == "mspB":

                    populated_expression = context.expression_populator.populate(
                                                message.expression, host)
                    size = context.metrics_manager.get_expression_size(
                                                        populated_expression,
                                                        context, host)
                    msperbyte = float(metric_value)
                    if metric_unit == "mspb":
                        msperbyte = msperbyte / 8.0

                    time = msperbyte * size

            elif metric_type == "algorithm":

                if not context.channels_manager.has_algorithm(metric_value):
                    raise RuntimeException("Communication algorithm {0} undeclared.".format(metric_value))

                link_quality = None
                if request is not None:
                    link_quality = context.channels_manager.get_router().get_link_quality(channel.tag_name,
                                                                                          message.sender,
                                                                                          request.receiver)
                return context.channels_manager.get_algorithm_resolver()\
                    .get_time(context, host, metric_value, message.expression, link_quality=link_quality)

            elif metric_type == "block":

                mparts = metric_value.split(':')
                unit_time = float(mparts[0])
                unit_size = int(mparts[1])
                size_unit = metric_unit[1]  # how big unit is
                populated_expression = context.expression_populator.populate(
                    message.expression, host)
                size = context.metrics_manager.get_expression_size(
                    populated_expression, context, host)
                units = ceil(size / float(unit_size))
                time = units * unit_time
                if size_unit == 'b':
                    time *= 8.0
        return time

    def _get_time_of_sending(self, context, channel, message):
        """ Returns time of message sending process """
        metric = self._find_communication_metric(context, channel, message.sender, COMMUNICATION_TYPE_OUT)
        if metric is None:
            return 0
        return self._get_time_for_communication_step(context, channel, message.sender, metric, message)

    def _get_time_of_receiving(self, context, channel, message, request):
        """ Returns time of message receiving process """
        metric = self._find_communication_metric(context, channel, request.receiver, COMMUNICATION_TYPE_IN)
        if metric is None:
            return 0
        return self._get_time_for_communication_step(context, channel, request.receiver, metric, message, request)

    def _execute_communication_instruction(self, context, **kwargs):
        """ """
        channel = context.channels_manager.find_channel_for_current_instruction(context)
        if not channel:
            return ExecutionResult(result_kwargs=kwargs)

        if kwargs is None:
            kwargs = {}

        instruction = context.get_current_instruction()

        # TODO: Consider situation when host has many context and in one context it is waiting for message
        # while in second one it can go further (non communication instruction)

        # Check if other hosts should send or receive their message through this channel before
        current_host_time = self.module.get_current_time(self.simulator, context.get_current_host())
        min_hosts_time = (context.get_current_host(), current_host_time)
        delay_communication_execution = False

        for h in context.hosts:
            # Omit finished hosts
            if h.finished():
                continue
            # Omit current host
            if h == context.get_current_host():
                continue
            # Omit hosts not using current channel
            if not channel.is_connected_with_host(h):
                continue

            # Check the time of other hosts
            host_time = self.module.get_current_time(self.simulator, h)
            # If checked (in loop) host is in the past relative to the time of actual host
            if host_time < min_hosts_time[1]:
                current_instruction = h.get_current_instructions_context().get_current_instruction()

                if isinstance(current_instruction, CommunicationInstruction):
                    # If the checked host (the one in the past) want to send message
                    # it should be first
                    if current_instruction.is_out():
                        delay_communication_execution = True
                    else:
                        # The checked host (the one in the past) is waiting for the message
                        # Lets check if the message fot the host is in the channel
                        # If there is, it should be executed first so wait for it
                        host_channel = context.channels_manager.find_channel_for_host_instruction(
                            context, h, current_instruction)

                        if host_channel:
                            messages_request = None
                            if not host_channel.is_waiting_on_instruction(h, current_instruction):
                                messages_request = context.channels_manager.build_message_request(
                                    h, current_instruction, context.expression_populator)

                            # Now we can update the times of hosts depending on the fulfilled request
                            fulfilled_requests = host_channel.get_fulfilled_requests(messages_request=messages_request,
                                                                                     include_all_sent_messages=True)
                            for request, messages in fulfilled_requests:
                                request_time = self.module.get_request_created_time(self.simulator, request)
                                # Traverse all messages needed to fulfill request
                                for msg in messages:
                                    # If sender time is smaller than time when received asked for message
                                    # it would mean that sender wants to send message from the past
                                    # to the  receiver who started to wait message later
                                    if self.module.get_message_sent_time(self.simulator, msg) < request_time:
                                        msg.use_by_host(request.receiver)

                            # Check if request of this host is fulfilled
                            # If yes, let it go first
                            fulfilled_requests = host_channel.get_fulfilled_requests(messages_request=messages_request)
                            for request, messages in fulfilled_requests:
                                if request.receiver == h and request.instruction == current_instruction:
                                    delay_communication_execution = True
                                    break
                else:
                    # If the checked host (the one in the past) executes some non-communication operation
                    # it should be done first
                    delay_communication_execution = True

        ## Delay execution of this instruction
        ## if needed according to previous check
        if delay_communication_execution:
            return ExecutionResult(custom_index_management=True,
                                   finish_instruction_execution=True,
                                   result_kwargs=kwargs)

        ##############################################
        # Now the host with minimal time is executed
        ##############################################

        sent_messages = None
        messages_request = None

        if instruction.is_out():
            # OUT instruction
            sender = context.get_current_host()
            # Get list of messages being sent from upper executor or
            # build new list
            if 'sent_messages' in kwargs:
                sent_messages = kwargs['sent_messages']
            else:
                sent_messages = []
                for p in instruction.variables_names:
                    # Expressions as variables values are already populated
                    sent_messages.append(context.channels_manager.build_message(
                        context.get_current_host(),
                        context.get_current_host().get_variable(p).clone(),
                        context.expression_checker))
                kwargs['sent_messages'] = sent_messages

            sender_time = self.module.get_current_time(self.simulator, sender)
            for msg in sent_messages:
                
                # DEBUG #
                print 'sending from', sender.name, 'at', self.module.get_current_time(self.simulator, sender), 'message', unicode(msg.expression)
                # DEBUG #
                
                # Get time of sending and update sender time
                sending_time = self._get_time_of_sending(context, channel, msg)
                self.module.add_message_sent_time(self.simulator, msg, sender_time)
                self.module.add_message_sending_time(self.simulator, msg, sending_time)
                sender_time += sending_time
                self.module.set_current_time(self.simulator, sender, sender_time)

        else:
            # IN instruction

            if 'messages_request' in kwargs:
                request = kwargs['messages_request']
            else:
                request = context.channels_manager.build_message_request(context.get_current_host(),
                                                                         instruction,
                                                                         context.expression_populator)
                kwargs['messages_request'] = request

            # If waiting request has NOT been created and added before
            if not channel.is_waiting_on_instruction(request.receiver, request.instruction):
                receiver = context.get_current_host()
                
                # DEBUG #
                print 'request in', receiver.name, 'at', self.module.get_current_time(self.simulator, receiver)
                # DEBUG #

                self.module.add_request_created_time(self.simulator, request,
                                                     self.module.get_current_time(self.simulator, receiver))
                messages_request = request

        # Now we can update the times of hosts depending on the fulfilled request
        fulfilled_requests = channel.get_fulfilled_requests(messages=sent_messages, messages_request=messages_request,
                                                            include_all_sent_messages=True)
        for request, messages in fulfilled_requests:
            request_time = self.module.get_request_created_time(self.simulator, request)
            # Traverse all messages needed to fulfill request
            for msg in messages:
                # If sender time is smaller than time when received asked for message
                # it would mean that sender wants to send message from the past
                # to the  receiver who started to wait message later
                if self.module.get_message_sent_time(self.simulator, msg) < request_time:
                    msg.use_by_host(request.receiver)

        # The messages from the past to the future are removed
        # Now lets try again to fulfill requests and update the times
        fulfilled_requests = channel.get_fulfilled_requests(messages=sent_messages,
                                                            messages_request=messages_request)
        for request, messages in fulfilled_requests:
            sorted_messages = []
            for msg in messages:
                added = False
                msg_time = self.module.get_message_sent_time(self.simulator, msg)
                for i in range(0, len(sorted_messages)):
                    sorted_msg_time = self.module.get_message_sent_time(self.simulator, sorted_messages[i])
                    if sorted_msg_time > msg_time:
                        sorted_messages.insert(i, msg)
                        added = True
                if not added:
                    sorted_messages.append(msg)

            receiver_time = self.module.get_current_time(self.simulator, request.receiver)
            
            msg_index = 0
            for msg in sorted_messages:
                # Msg time is greater or equal to request time
                message_time = self.module.get_message_sent_time(self.simulator, msg)
                # Check if current time of receiver is smaller that time when message was send
                # If yes, increase receiver time to the time when message was sent
                if receiver_time < message_time:
                    receiver_time = message_time
                # Add the time of receiving (usually equal to time of sending)
                receiver_time += self._get_time_of_receiving(context, channel, msg, request)
                # Get time when requester started waiting for the message
                started_waiting_at = self.module.get_request_created_time(self.simulator, request)
                # Get time of sending message
                sending_time = self.module.get_message_sending_time(self.simulator, msg)
                
                # DEBUG
                print 'binded in', request.receiver.name, 'var', request.instruction.variables_names[msg_index], \
                    'assigned', unicode(msg.expression) , 'at', receiver_time 
                msg_index += 1
                # DEBUG
                
                # Add timetrace to module
                self.module.add_channel_message_trace(self.simulator, channel, msg, 
                                                      msg.sender, message_time, sending_time, 
                                                      request.receiver, started_waiting_at, receiver_time)
            self.module.set_current_time(self.simulator, request.receiver, receiver_time)

        return ExecutionResult(result_kwargs=kwargs)
        