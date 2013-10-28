'''
Created on 31-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import random
from aqopa.simulator.state import Hook, ExecutionResult
from aqopa.model import AssignmentInstruction,\
    CallFunctionInstruction, IfInstruction, WhileInstruction,\
    CommunicationInstruction, CallFunctionExpression, TupleExpression
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
            
        time = self._get_time_for_expression(context, expression)
        
        if time > 0:
            host = context.get_current_host()
            self.module.add_timetrace(self.simulator, host, instruction, 
                                      self.module.get_current_time(self.simulator, host), time)
            self.module.set_current_time(self.simulator, host, self.module.get_current_time(self.simulator, host) + time)
            
    def _get_time_for_expression(self, context, expression):
        """
        Returns calculated time that execution of expression takes.
        """
        if isinstance(expression, TupleExpression):
            return self._calculate_time_for_tuple_expression(context, expression)
        elif isinstance(expression, CallFunctionExpression):
            return self._calculate_time_for_expression(context, expression)
        return 0

    def _calculate_time_for_tuple_expression(self, context, expression):
        """
        Calculate execution time for tuple expression. 
        """
        time = 0
        for i in range(0, len(expression.elements)):
            time += self._get_time_for_expression(context, expression.elements[i])
        return time
    
    def _calculate_time_for_expression(self, context, expression):
        """
        Calculate time for expression.
        """
        time = 0
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
                            raise RuntimeException('Metric unit is set as %s, but call parameter to get size of is not set.' 
                                                   % metric_unit)
                        
                        size = 0
                        call_params_indexes = mparts[1].split(',')
                        for index in call_params_indexes:
                            
                            populated_expression = context.expression_populator.populate(
                                                        expression.arguments[index],
                                                        context.get_current_host().get_variables(),
                                                        context.expression_reducer)
                            
                            size += context.metrics_manager.get_expression_size(
                                                                populated_expression,
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
                

        for expr in expression.arguments:
            time += self._get_time_for_expression(context, expr)
            
        return time
                
    def _execute_communication_instruction(self, context):
        """ """
        channel = context.channels_manager.find_channel_for_current_instruction(context)
        if not channel:
            return None
        
        instruction = context.get_current_instruction()
        expressions_cnt = len(instruction.variables_names)
        
        # Check if other hosts should send their message 
        # through this channel before
        current_host_time = self.module.get_current_time(self.simulator, context.get_current_host())
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
            
            # Omit hosts that are waiting for the message on current channel
            current_instruction = h.get_current_instructions_context()\
                                    .get_current_instruction()
            if isinstance(current_instruction, CommunicationInstruction):
                
                ch = None
                if instruction.is_out(): # OUT instruction
                    if not current_instruction.is_out(): # IN instruction
                        ch = context.channels_manager.find_channel_for_host_instruction(
                                                        context, h, current_instruction)
                else: # IN instruction
                    if current_instruction.is_out(): # OUT instruction
                        ch = context.channels_manager.find_channel_for_host_instruction(
                                                        context, h, current_instruction)
                if ch == channel:
                    continue
            
            if self.module.get_current_time(self.simulator, h) < current_host_time:
                delay_communication_execution = True
                
        # Delay execution of this instruction 
        # if needed according to previous check      
#        if delay_communication_execution:
#            return ExecutionResult(custom_index_management=True, 
#                                   finish_instruction_execution=True)
                
                
        if instruction.is_out():
            sender = context.get_current_host()
              
            
            receivers_list = channel.get_queue_of_receiving_hosts(expressions_cnt)
            for i in range(0, len(receivers_list)):
                if not receivers_list[i]: # No receiver for message
                    self.module.add_channel_message_trace(self.simulator, channel, 
                                                          self.module.get_channel_next_message_id(self.simulator, channel),
                                                          sender,
                                                          self.module.get_current_time(self.simulator, sender))
                else:
                    if self.module.get_current_time(self.simulator, sender) < self.module.get_current_time(self.simulator, receivers_list[i]):
                        
                        raise TimeSynchronizationException("Time synchronization error. Trying to send message from host '%s' at time %s ms while receiving host '%s' has time %s ms." % 
                                                           (unicode(sender),
                                                            self.module.get_current_time(self.simulator, sender),
                                                            unicode(receivers_list[i]),
                                                            self.module.get_current_time(self.simulator, receivers_list[i])))
                    
                    self.module.add_channel_message_trace(self.simulator, channel,
                                                          self.module.get_channel_next_message_id(self.simulator, channel),
                                                          sender,
                                                          self.module.get_current_time(self.simulator, sender),
                                                          receivers_list[i],
                                                          self.module.get_current_time(self.simulator, receivers_list[i]))
                    self.module.set_current_time(self.simulator, receivers_list[i], self.module.get_current_time(self.simulator, sender))
                
         
        else: # IN communication step
            sender = None
            receiver = context.get_current_host()
            
            sending_hosts = channel.get_queue_of_sending_hosts(expressions_cnt)
            for i in range(0, len(sending_hosts)):
                
                traces = self.module.get_channel_message_traces(self.simulator, channel)
                if len(traces):
                    for j in range(0, len(traces)):
                        if traces[j].sender == sending_hosts[i] and not traces[j].receiver:
                            
                            if self.module.get_current_time(self.simulator, sending_hosts[i]) < self.module.get_current_time(self.simulator, receiver):
                                raise TimeSynchronizationException("Time synchronization error. " + \
                                                           "Trying to send message from host '%s' at time %s ms " + \
                                                           "while receiving host '%s' has time %s ms." % 
                                                           (unicode(sender),
                                                            self.module.get_current_time(self.simulator, sender),
                                                            unicode(receivers_list[i]),
                                                            self.module.get_current_time(self.simulator, receivers_list[i])))
                                
                            traces[j].add_receiver(receiver, self.module.get_current_time(self.simulator, receiver))
                            
            
        