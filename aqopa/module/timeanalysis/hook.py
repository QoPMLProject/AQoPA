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
    
    def _get_time_for_exact_range_metric(self, metric_type, metric_unit, metric_value, expression, host, context):
        """
        Returns execution time of expression which has exact or range metric assigned.
        """

        if metric_unit in ["ms", "s"]:
            # Get time
            if metric_type == "exact":
                time_value = float(metric_value)
            else:  # range
                mvalues = metric_value.split('..')
                val_from = float(mvalues[0])
                val_to = float(mvalues[1])
                time_value = val_from + (val_to-val_from)*random.random()

            # Update time according to the time unit
            if metric_unit == "ms":
                return time_value / 1000.0
            else:  # metric_unit == "s":
                return time_value

        elif metric_unit in ["mspb", "mspB", "kbps", "mbps"]:

            mparts = metric_value.split(':')
            time_metric = mparts[0]
            indexes = None 
            if len(mparts) == 2:
                indexes = [int(i) for i in mparts[1].split(',')]

            # Get time
            if metric_type == "exact":
                time_value = float(time_metric)
            else:  # range
                mvalues = time_metric.split('..')
                val_from = float(mvalues[0])
                val_to = float(mvalues[1])
                time_value = val_from + (val_to-val_from)*random.random()

            size = 0
            if indexes is None:
                populated_expression = context.expression_populator.populate(expression, 
                                                                             context.get_current_host())
                size = context.metrics_manager.get_expression_size(populated_expression, 
                                                                   context, context.get_current_host())
            else:
                for index in indexes:
                    populated_expression = context.expression_populator.populate(
                        expression.arguments[index-1], context.get_current_host())

                    size += context.metrics_manager.get_expression_size(
                        populated_expression, context, context.get_current_host())

            if metric_unit in ["mspb", "mspB"]:
                msperbyte = float(time_value)
                if metric_unit == "mspb":
                    msperbyte /= 8.0
            elif metric_unit == "kbps":
                msperbyte = 8000.0 / 1024.0 / time_value
            else: # mbps
                msperbyte = 8000.0 / 1024.0 / 1024.0 / time_value

            # Make s from ms
            sperbyte = msperbyte / 1000.0
            return sperbyte * size
    
    def _get_time_for_block_metric(self, metric_type, metric_unit, metric_value, expression, host, context):
        """
        Returns execution time of expression which has block metric assigned.
        """
        mparts = metric_value.split(':')
        element_index = None
        if len(mparts) == 3:
            element_index = int(mparts[0])-1
            unit_time = float(mparts[1])
            unit_size = int(mparts[2])
        else:
            unit_time = float(mparts[0])
            unit_size = int(mparts[1])

        time_unit = metric_unit[0]
        if time_unit == "ms":
            unit_time /= 1000.0
        size_unit = metric_unit[1]

        expression_to_populate = expression if element_index is None else expression.arguments[element_index]
        populated_expression = context.expression_populator.populate(expression_to_populate, host)
        argument_size = context.metrics_manager.get_expression_size(populated_expression,
                                                                    context, host)
        units = ceil(argument_size / float(unit_size))

        time = units * unit_time
        if size_unit == 'b':
            time *= 8.0
        return time
    
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

                if metric_type in ["exact", "range"]:

                    time = self._get_time_for_exact_range_metric(metric_type, metric_unit, metric_value, 
                                                                 expression, context.get_current_host(), context)
                elif metric_type == "block":

                    time = self._get_time_for_block_metric(metric_type, metric_unit, metric_value,
                                                           expression, context.get_current_host(), context)
                elif metric_type == 'algorithm':
                    algorithm_name = metric_value
                    if not context.algorithms_resolver.has_algorithm(algorithm_name):
                        raise RuntimeException("Communication algorithm {0} undeclared.".format(algorithm_name))

                    alg = context.algorithms_resolver.get_algorithm(algorithm_name)
                    variables = {alg['parameter']: expression}
                    time = context.algorithms_resolver.calculate(context, context.get_current_host(),
                                                                 algorithm_name, variables)

                    # Update time according to the time unit
                    if metric_unit == "ms":
                        time /= 1000.0

            if time > 0:
                time_details.append((expression, time))

        for expr in expression.arguments:
            argument_time, argument_time_details = self._get_time_details_for_expression(context, expr)
            time += argument_time
            time_details.extend(argument_time_details)

        return time, time_details

    def _get_time_for_communication_step(self, context, host, channel, metric, message, receiver=None):
        """ Returns time of sending/receiving message """

        if metric['type'] == 'metric':
            metric_value = metric['value']
        elif metric['type'] == 'algorithm':
            algorithm_name = metric['name']
            if not context.algorithms_resolver.has_algorithm(algorithm_name):
                raise RuntimeException("Communication algorithm {0} undeclared.".format(algorithm_name))

            link_quality = context.channels_manager.get_router().get_link_quality(channel.tag_name,
                                                                                  message.sender,
                                                                                  receiver)
            alg = context.algorithms_resolver.get_algorithm(algorithm_name)
            variables = {
                'link_quality': link_quality,
                alg['parameter']: message.expression,
            }
            metric_value = context.algorithms_resolver.calculate(context, host, algorithm_name, variables)
        else:
            return 0

        unit = metric['unit']
        if unit == 'ms':
            # exact time
            return metric_value / 1000.0
        else:
            # time depending on the size
            populated_expression = context.expression_populator.populate(message.expression, message.sender)
            # size in bytes
            size = context.metrics_manager.get_expression_size(populated_expression, context, message.sender)

            mspB = 0
            if unit == 'mspB':
                mspB = float(metric_value)
            elif unit == 'mspb':
                mspB = float(metric_value) * 8.0
            elif unit == 'kbps':
                mspB = 1.0 / (float(metric_value) * 0.128)
            elif unit == 'mbps':
                mspB = 1.0 / (float(metric_value) * 0.000128)

            spB = mspB / 1000.0

            return spB * size

    def _find_communication_metric(self, context, channel, sender, receiver=None):
        """
        Return the communication metric from topology.
        """
        return context.channels_manager.get_router().get_link_parameter_value('time', channel.tag_name, sender, receiver)

    def _get_time_of_sending_point_to_point(self, context, channel, message, request):
        """ Returns time of message sending process """
        metric = self._find_communication_metric(context, channel, message.sender, receiver=request.receiver)
        if metric is None:
            return 0
        return self._get_time_for_communication_step(context, message.sender, channel, metric, message, receiver=request.receiver)

    def _get_time_of_sending_boradcast(self, context, channel, message):
        """ Returns time of message sending process """
        metric = self._find_communication_metric(context, channel, message.sender, receiver=None)
        if metric is None:
            return 0
        return self._get_time_for_communication_step(context, message.sender, channel, metric, message, receiver=None)

    def _get_time_of_receiving(self, context, channel, message, request):
        """ Returns time of message receiving process """
        metric = self._find_communication_metric(context, channel, message.sender, receiver=request.receiver)
        if metric is None:
            return 0
        return self._get_time_for_communication_step(context, message.sender, channel, metric, message, receiver=request.receiver)

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

            # If hosts have the same time - the IN instruction should be executed before OUT execution
            # and other instructions (non-communication) should be executed before as well
            if host_time == min_hosts_time[1]:
                for instructions_context in h.get_all_instructions_contexts():
                    if instructions_context.finished():
                        continue
                    host_current_instruction = instructions_context.get_current_instruction()
                    if isinstance(host_current_instruction, CommunicationInstruction):
                        if instruction.is_out() and not host_current_instruction.is_out():
                            host_channel = context.channels_manager.find_channel_for_host_instruction(
                                context, h, host_current_instruction)
                            if host_channel:
                                if not host_channel.is_waiting_on_instruction(h, host_current_instruction):
                                    delay_communication_execution = True
                    else:
                        delay_communication_execution = True

            # If checked (in loop) host is in the past relative to the time of actual host
            if host_time < min_hosts_time[1]:

                # In general, the instruction in host with smaller time
                # should be executed earlier
                host_delay_communication_execution = True

                # The only exception is when the host in the past is waiting on IN instruction
                # and the request cannot be fulfilled
                current_instruction = h.get_current_instructions_context().get_current_instruction()
                if isinstance(current_instruction, CommunicationInstruction):
                    if not current_instruction.is_out():
                        # The checked host (the one in the past) is waiting for the message
                        # Lets check if the messages for the host are in the channel
                        host_channel = context.channels_manager.find_channel_for_host_instruction(
                            context, h, current_instruction)
                        if host_channel:

                            # If host is not waiting on IN instruction - let it go first
                            # If host is waiting - check if it is fulfilled
                            if host_channel.is_waiting_on_instruction(h, current_instruction):
                                request = host_channel.get_existing_request_for_instruction(h, current_instruction)
                                if not request.ready_to_fulfill():
                                    host_delay_communication_execution = False

                if host_delay_communication_execution:
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

        if instruction.is_out():
            # OUT instruction
            sender = context.get_current_host()
            # Get list of messages being sent from upper executor or build new list
            if 'sent_message' in kwargs:
                sent_message = kwargs['sent_message']
            else:
                sent_message = context.channels_manager.build_message(
                    context.get_current_host(),
                    context.get_current_host().get_variable(instruction.variable_name).clone(),
                    context.expression_checker)
                kwargs['sent_message'] = sent_message

            sender_time = self.module.get_current_time(self.simulator, sender)
            # DEBUG #
            # print 'sending message from ', sender.name, 'at', sender_time
            # DEBUG #

            all_requests = channel.get_filtered_requests(sent_message, context.channels_manager.get_router())
            accepted_requests = []
            for request in all_requests:
                if self.module.get_request_created_time(self.simulator, request) > sender_time:
                    sent_message.cancel_for_request(request)
                else:
                    accepted_requests.append(request)

            if len(accepted_requests) > 1:
                # broadcast
                # Send message with broadcast metric, update sender's time and fill in the sending time in message
                broadcast_time = self._get_time_of_sending_boradcast(context, channel, sent_message)
                self.module.add_message_sent_time(self.simulator, sent_message, sender_time)
                self.module.add_message_sending_time(self.simulator, sent_message, broadcast_time)

                self.module.set_current_time(self.simulator, sender, sender_time + broadcast_time)

                for request in accepted_requests:
                    if request.is_waiting and request.assigned_message is None:
                        receiving_time = self._get_time_of_receiving(context, channel, sent_message, request)
                        receiving_time = max(receiving_time, broadcast_time)

                        started_waiting_at = self.module.get_request_created_time(self.simulator, request)
                        receiver_time = self.module.get_current_time(self.simulator, request.receiver)
                        receiver_time = max(receiver_time, sender_time)
                        self.module.set_current_time(self.simulator, request.receiver,
                                                     receiver_time + receiving_time)
                        # Add timetrace to module
                        self.module.add_channel_message_trace(self.simulator, channel, sent_message,
                                                              sent_message.sender, sender_time, broadcast_time,
                                                              request.receiver, started_waiting_at,
                                                              receiver_time, receiving_time)

                # DEBUG #
                # print 'msg from', sent_message.sender.name, \
                #     'at', sender_time, '(', broadcast_time, 'ms ) ', 'to', len(accepted_requests), 'of', \
                #     len(all_requests), 'hosts', '- message', unicode(sent_message.expression)
                # DEBUG #

            elif len(accepted_requests) == 1:
                # point to point
                # Send message with link metric, update sender's time and fill in the sending time in message
                request = accepted_requests[0]
                sending_time = self._get_time_of_sending_point_to_point(context, channel,
                                                                        sent_message, request)
                self.module.add_message_sent_time(self.simulator, sent_message, sender_time)
                self.module.add_message_sending_time(self.simulator, sent_message, sending_time)

                self.module.set_current_time(self.simulator, sender, sender_time + sending_time)

                receiving_time = self._get_time_of_receiving(context, channel, sent_message, request)
                receiving_time = max(receiving_time, sending_time)

                receiver_time = self.module.get_current_time(self.simulator, request.receiver)
                receiver_time = max(receiver_time, sender_time)
                self.module.set_current_time(self.simulator, request.receiver,
                                             receiver_time + receiving_time)

                started_waiting_at = self.module.get_request_created_time(self.simulator, request)
                # Add timetrace to module
                self.module.add_channel_message_trace(self.simulator, channel, sent_message,
                                                      sent_message.sender, sender_time, sending_time,
                                                      request.receiver, started_waiting_at,
                                                      receiver_time, receiving_time)
                # DEBUG #
                # print 'msg from', sent_message.sender.name, 'to', request.receiver.name, \
                #     'at', sender_time, '(', sending_time, 'ms ) ', 'and started receiving at', \
                #     receiver_time, '(t:', receiving_time, 'ms, wait since:', started_waiting_at, 'ms)', \
                #     'message', unicode(sent_message.expression)
                # DEBUG #

            else:  # zero receivers
                # Send message with broadcast metric and update sender's time - no receivers
                broadcast_time = self._get_time_of_sending_boradcast(context, channel, sent_message)
                self.module.add_message_sent_time(self.simulator, sent_message, sender_time)
                self.module.add_message_sending_time(self.simulator, sent_message, broadcast_time)

                self.module.set_current_time(self.simulator, sender, sender_time + broadcast_time)

                # DEBUG #
                # print 'all requests', len(all_requests), ' - accepted:', len(accepted_requests)
                # print 'msg from', sent_message.sender.name, \
                #     'at', sender_time, '(', broadcast_time, 'ms ) ', \
                #     'message', unicode(sent_message.expression)
                # DEBUG #

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
                self.module.add_request_created_time(self.simulator, request,
                                                     self.module.get_current_time(self.simulator, receiver))
                # DEBUG #
                # print 'msg requested by', receiver.name, 'at', self.module.get_current_time(self.simulator, receiver)
                # DEBUG #


            if request.assigned_message is None:
                # Set messages from the past as cancelled for this request
                all_messages = channel.get_filtered_messages(request, context.channels_manager.get_router())
                accepted_messages = []
                for message in all_messages:
                    if self.module.get_request_created_time(self.simulator, request) > \
                            self.module.get_message_sent_time(self.simulator, message):
                        message.cancel_for_request(request)
                    else:
                        accepted_messages.append(message)

                if len(accepted_messages) > 0:
                    message = accepted_messages[0]
                    sending_time = self.module.get_message_sending_time(self.simulator, message)
                    receiving_time = self._get_time_of_receiving(context, channel, message, request)
                    receiving_time = max(receiving_time, sending_time)

                    receiver_time = self.module.get_current_time(self.simulator, request.receiver)
                    self.module.set_current_time(self.simulator, request.receiver,
                                                 receiver_time + receiving_time)

                    # Add timetrace to module
                    message_sent_time = self.module.get_message_sent_time(self.simulator, message)
                    started_waiting_at = self.module.get_request_created_time(self.simulator, request)
                    self.module.add_channel_message_trace(self.simulator, channel, message,
                                                          message.sender, message_sent_time, sending_time,
                                                          request.receiver, started_waiting_at,
                                                          receiver_time, receiving_time)
        return ExecutionResult(result_kwargs=kwargs)
        