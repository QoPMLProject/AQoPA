'''
Created on 31-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from math import ceil
import random
from aqopa.simulator.state import Hook, ExecutionResult
from aqopa.model import AssignmentInstruction,\
    CallFunctionInstruction, IfInstruction, WhileInstruction,\
    CommunicationInstruction, CallFunctionExpression, TupleExpression, ComparisonExpression
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
        
        
    def execute(self, context):
        """
        """
        instruction = context.get_current_instruction()
        
        if instruction.__class__ not in [AssignmentInstruction, CallFunctionInstruction, 
                                     IfInstruction, WhileInstruction, CommunicationInstruction]:
            return
        
        if isinstance(instruction, CommunicationInstruction):
            return self._execute_communication_instruction(context)
        else:
            self._update_time(context)
            return ExecutionResult()
            
    def _update_time(self, context):
        """ 
        Update times in context according to current instruction.
        """
        instruction = context.get_current_instruction()
        
        expression = None
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
                
                if sparam.service_name.lower() != "time":
                    continue

                metric_type = sparam.param_name.lower()
                metric_unit = sparam.unit
                metric_value = metric.service_arguments[i]

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
                                                        context.get_current_host().get_variables(),
                                                        context.expression_reducer)

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
                
    def _execute_communication_instruction(self, context):
        """ """
        channel = context.channels_manager.find_channel_for_current_instruction(context)
        if not channel:
            return None
        
        instruction = context.get_current_instruction()
        expressions_cnt = len(instruction.variables_names)

        # If host does not want to receive or send message,
        # let it go
        if isinstance(instruction, CommunicationInstruction):

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
                if not channel.connected_with_host(h):
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
                            vars_cnt = len(current_instruction.variables_names)
                            channel = context.channels_manager.find_channel_for_host_instruction(
                                context, h, current_instruction)
                            # If channel has enough vars
                            if len(channel.get_queue_of_sending_hosts(vars_cnt)) >= vars_cnt:
                                delay_communication_execution = True
                    else:
                        # If the checked host (the one in the past) executes some non-communication operation
                        # it should be done first
                        delay_communication_execution = True


                    #ch = context.channels_manager.find_channel_for_host_instruction(
                    #    context, h, current_instruction)
                    #if ch == channel:
                    #    if current_instruction.is_out():
                    #        host_time = self.module.get_current_time(self.simulator, h)
                    #        if host_time < min_hosts_time[1]:
                    #            min_hosts_time = (h, host_time)
                    #
                    #ch = None
                    #if instruction.is_out(): # OUT instruction
                    #    if not current_instruction.is_out(): # IN instruction
                    #        ch = context.channels_manager.find_channel_for_host_instruction(
                    #            context, h, current_instruction)
                    #else: # IN instruction
                    #    if current_instruction.is_out(): # OUT instruction
                    #        ch = context.channels_manager.find_channel_for_host_instruction(
                    #            context, h, current_instruction)
                    #if ch == channel:
                    #    continue
                    #
                    #if self.module.get_current_time(self.simulator, h) < current_host_time:
                    #    delay_communication_execution = True

            ## Delay execution of this instruction
            ## if needed according to previous check
            #if delay_communication_execution:
            #    if context.get_current_host() != min_hosts_time[0]:
            #        return ExecutionResult(custom_index_management=True,
            #                               finish_instruction_execution=True)

            if delay_communication_execution:
                return ExecutionResult(custom_index_management=True,
                                       finish_instruction_execution=True)

            if instruction.is_out():
                sender = context.get_current_host()
                receivers_list = channel.get_queue_of_receiving_hosts(expressions_cnt)
                time_of_sending = self.module.get_current_time(self.simulator, sender)
                for i in range(0, len(receivers_list)):
                    if not receivers_list[i]:  # No receiver for message
                        self.module.add_channel_message_trace(self.simulator, channel,
                                                              self.module.get_channel_next_message_id(self.simulator,
                                                                                                      channel),
                                                              sender, time_of_sending)
                    else:
                        if self.module.get_current_time(self.simulator, sender) < self.module.get_current_time(self.simulator, receivers_list[i]):

                            raise TimeSynchronizationException("Time synchronization error. Trying to send message from host '%s' at time %s ms while receiving host '%s' has time %s ms." %
                                                               (unicode(sender),
                                                                self.module.get_current_time(self.simulator, sender),
                                                                unicode(receivers_list[i]),
                                                                self.module.get_current_time(self.simulator, receivers_list[i])))

                        # When someone is already waiting for the message
                        # the sent at time and received at time are the same
                        time_of_receiving = time_of_sending
                        self.module.add_channel_message_trace(self.simulator, channel,
                                                              self.module.get_channel_next_message_id(self.simulator, channel),
                                                              sender, time_of_sending,
                                                              receivers_list[i], time_of_receiving)
                        self.module.set_current_time(self.simulator, receivers_list[i], time_of_receiving)


            else: # IN communication step
                sender = None
                receiver = context.get_current_host()
                sending_hosts = channel.get_queue_of_sending_hosts(expressions_cnt)
                for sending_host in sending_hosts:
                    traces = self.module.get_channel_message_traces(self.simulator, channel)
                    for trace in traces:
                        if trace.sender == sending_host and not trace.receiver:
                            time_of_sending = self.module.get_current_time(self.simulator, sending_host)
                            time_of_receiving = self.module.get_current_time(self.simulator, receiver)
                            if time_of_sending < time_of_receiving:
                                raise TimeSynchronizationException(
                                    ("Time synchronization error. " +
                                     "Trying to send message from host '%s' at time %s ms " +
                                     "while receiving host '%s' has time %s ms.") %
                                    (unicode(sender), self.module.get_current_time(self.simulator, sender),
                                     unicode(trace.receiver),
                                     self.module.get_current_time(self.simulator, trace.receiver)))
                            # Calculate time of receiving as the maximum of sending and receiving
                            time_of_receiving = max(time_of_sending, time_of_receiving)
                            trace.add_receiver(receiver, time_of_receiving)
                            self.module.set_current_time(self.simulator, receiver, time_of_receiving)

                            
            
        