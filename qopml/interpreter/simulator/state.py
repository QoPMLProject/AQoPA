'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from qopml.interpreter.model import BooleanExpression, IdentifierExpression,\
    CallFunctionExpression, TupleExpression, TupleElementExpression,\
    AssignmentInstruction, CommunicationInstruction, FinishInstruction,\
    ContinueInstruction, CallFunctionInstruction, IfInstruction,\
    WhileInstruction, HostSubprocess, COMMUNICATION_TYPE_OUT,\
    original_name, name_indexes
    
from qopml.interpreter.simulator.error import RuntimeException

class Context():
    
    def __init__(self):
        self.hosts = []                 # List of all hosts in this context
        self.functions = []             # List of all functions in this context
        
        self.expression_checker = None
        self.expression_reducer = None

        self.metrics_manager = None
        self.channels_manager = None
        
        self._current_host_index = 0
        self._previous_host_index = -1
    
    def get_current_host(self):
        """
        Return host being executed at this step.
        """
        return self.hosts[self._current_host_index]
    
    def get_current_instruction(self):
        """
        Return instruction being executed at this step.
        """
        return self.get_current_host().get_current_instructions_context().get_current_instruction()
    
    def all_hosts_finished(self):
        """
        Returns True if all hosts are in FINISHED state
        and no next states can be generated.
        """
        for h in self.hosts:
            if not h.finished():
                return False
        return True
    
    def hosts_loop_ended(self):
        """
        Returns True when all hosts tried to go to next state in current loop.
        Going to the next state is done for one host in next state generation step, so to finish
        the one loop for all (let N) host, simulater must call function N times.
        """
        return self._previous_host_index < 0 or self._previous_host_index >= self._current_host_index
    
    def any_host_changed(self):
        """
        Return True in any host has changed in last next state generation loop performed 
        for all hosts.
        """
        for h in self.hosts:
            if h.has_changed():
                return True
        return False
    
    def mark_all_hosts_unchanged(self):
        """
        Sets the state of all hosts to unchanged. Used before each next state generation loop.
        """
        for h in self.hosts:
            h.mark_unchanged()
    
    def goto_next_host(self):
        """
        Context is moved to the next host so that next state generation step is performed for next host.
        """
        self._previous_host_index = self._current_host_index
        
        self._current_host_index = (self._current_host_index + 1) % len(self.hosts)
        
        # Go to next host until current host is not finihed
        while self._current_host_index != self._previous_host_index and self.get_current_host().finished():
            self._current_host_index = (self._current_host_index + 1) % len(self.hosts)
    
# ----------- Hook

HOOK_TYPE_PRE_HOST_LIST_EXECUTION       = 1
HOOK_TYPE_PRE_INSTRUCTION_EXECUTION     = 2
HOOK_TYPE_POST_INSTRUCTION_EXECUTION    = 3

class Hook():
    """
    Hooks are executed in many places of simulation.
    Hooks can be added by modules.
    """
    
    def execute(self, context):
        """
        Method changes the context. 
        """
        raise NotImplementedError()
        
# ----------- Host Process

HOST_STATUS_RUNNING = 1
HOST_STATUS_FINISHED = 2

class Host():
    """
    Simulation equivalent of host
    """
    
    def __init__(self, name, instructions_list, predefined_variables={}):
        self.name = name
        self.instructions_list = instructions_list
        self._variables = predefined_variables
        
        self._scheduler = None
        self._channels_map = {}
        self._changed = False
        self._status = HOST_STATUS_RUNNING 
        self._finish_error = None
        
    def __unicode__(self):
        return u"host %s" % unicode(self.name)
        
    def original_name(self):
        """"""
        return original_name(self.name)
        
    def add_name_index(self, index):
        """
        Add index to the name. 
        Before: name = ch, index = 1. After: name = ch.1
        """
        self.name += ".%d" % index
        
    def set_scheduler(self, scheduler):
        """Set scheduler"""
        self._scheduler = scheduler
        
    def set_variable(self, name, value):
        """Set hotst's variable"""
        self._variables[name] = value
        
    def get_variable(self, name):
        """ Get host's variable """
        if name not in self._variables:
            raise RuntimeException("Variable '%s' undefined in host '%s'" % (name, self.name))
        return self._variables[name]
    
    def get_variables(self):
        """ Get variables dict """
        return self._variables
        
    def mark_changed(self):
        """ Marks host changed. Means that host have changes in last state. """
        self._changed = True
        
    def mark_unchanged(self):
        """ Marks host unchanged. Clears changes from last state. """
        self._changed = False
        
    def has_changed(self):
        """ Returns True if host has changed """
        return self._changed
        
    def connect_with_channel(self, channel):
        """
        Assigns channel to this host.
        """
        if channel.original_name() not in self._channels_map:
            self._channels_map[channel.original_name()] = []
        if channel in self._channels_map[channel.original_name()]:
            return
        self._channels_map[channel.original_name()].append(channel)
        channel.connect_with_host(self)
    
    def find_channel(self, name):
        """
        Search for and retuen assigned channel by name (including indexes)
        """
        original_channel_name = original_name(name)
        indexes = name_indexes(name)

        if original_channel_name not in self._channels_map:
            return None
        channels = self._channels_map[original_channel_name]
        if len(channels) == 0:
            return None
        
        for ch in channels:
            # Check if channels has the same original name
            if ch.original_name() == name:
                i = 0
                #Check if channels have the same indexes
                ch_indexes = ch.indexes()
                while i < len(indexes):
                    if indexes[i] != ch_indexes[i]:
                        break
                    i += 1
                # If while loop was broken
                if i < len(indexes):
                    continue
                else:
                    # All indexes were the same
                    return ch
        return None
        
    def goto_next_instructions_context(self):
        """
        Moves host to next instructions context.
        """
        self._scheduler.goto_next_instruction_context()
        if self._scheduler.finished():
            self.finish_successfuly()
        
    def get_current_instructions_context(self):
        """ 
        Returns the currnt instructions context retrived from scheduler.
        """
        return self._scheduler.get_current_context()
    
    def get_current_process(self):
        """ """
        return self.get_current_instructions_context().get_process_of_current_list()
    
    def finished(self):
        """ 
        Returns True when host is finished
        """
        return self._status == HOST_STATUS_FINISHED
    
    def finish_successfuly(self):
        """
        Finish host execution without error
        """
        self._status = HOST_STATUS_FINISHED
        self._finish_error = None
    
    def finish_failed(self, error):
        """
        Finish host execution with error
        """
        self._status = HOST_STATUS_FINISHED
        self._finish_error = error
    
    
class Process():
    
    def __init__(self, name, instructions_list):
        self.name = name
        self.instructions_list = instructions_list
    
        self.follower = None
        self._channels_map = {}
        
    def original_name(self):
        """"""
        return original_name(self.name)
        
    def add_name_index(self, index):
        """
        Add index to the name. 
        Before: name = ch, index = 1. After: name = ch.1
        """
        self.name += ".%d" % index
        
    def connect_with_channel(self, channel):
        """
        Assigns channel to this host.
        """
        if channel.original_name() not in self._channels_map:
            self._channels_map[channel.original_name()] = []
        if channel in self._channels_map[channel.original_name()]:
            return
        self._channels_map[channel.original_name()].append(channel)
        channel.connect_with_process(self)
    
    def find_channel(self, name):
        """
        Search for and retuen assigned channel by name (including indexes)
        """
        original_channel_name = original_name(name)
        indexes = name_indexes(name)

        if original_channel_name not in self._channels_map:
            return None
        channels = self._channels_map[original_channel_name]
        if len(channels) == 0:
            return None
        
        for ch in channels:
            # Check if channels has the same original name
            if ch.original_name() == name:
                i = 0
                #Check if channels have the same indexes
                ch_indexes = ch.indexes()
                while i < len(indexes):
                    if indexes[i] != ch_indexes[i]:
                        break
                    i += 1
                # If while loop was broken
                if i < len(indexes):
                    continue
                else:
                    # All indexes were the same
                    return ch
        return None
        
    def __unicode__(self):
        return u"process %s" % unicode(self.name)
        
# ----------- Instructions Context

class InstructionsList:
    
    def __init__(self, instructions_list, process=None):
        self.process = process 
        self.instructions_list = instructions_list
        self._current_instruction_index = 0
        
    def get_current_instruction(self):
        """ """
        return self.instructions_list[self._current_instruction_index]
    
    def goto_next_instruction(self):
        """ """
        self._current_instruction_index += 1
        
    def finished(self):
        """
        Returns True if list is finished. 
        """
        return self._current_instruction_index >= len(self.instructions_list)

class InstructionsContext:
    
    def __init__(self):
        self.stack = []        # Stack of instructions list
        
    def _get_current_list(self):
        """
        Returns currently executed list of instructions.
        """
        if len(self.stack) == 0:
            return None
        return self.stack[len(self.stack)-1]
        
    def get_current_instruction(self):
        """
        Returns currently executed instruction.
        """
        return self._get_current_list().get_current_instruction()
        
    def get_process_of_current_list(self):
        """
        Returns the process that current list is in.
        """
        return self._get_current_list().process
        
    def add_instructions_list(self, instructions_list, process=None):
        """
        Add instructions list to the stack.
        """
        l = InstructionsList(instructions_list, process)
        self.stack.append(l)
        
    def goto_next_instruction(self):
        """
        Moves context to the next instruction.
        """
        self._get_current_list().goto_next_instruction()
        while not self.finished() and self._get_current_list().finished():
            self.stack.pop()
            
            if not self.finished():
                if self._get_current_list().get_current_instruction().is_loop():
                    self._get_current_list().goto_next_instruction()
        
    def finished(self):
        """
        Returns True if context is finished.
        """
        if len(self.stack) == 0:
            return True
        
        if len(self.stack) == 1 and self._get_current_list().finished():
            return True
        
        return False
        
        
# ----------- Executor
    
class InstructionExecutor():
    """
    Abstract class of executor from the chain of responsibility.
    """
    
    def can_execute_instruction(self, instruction):
        """
        Returns True if instruction can be executed by executor.
        """
        raise NotImplementedError()
    
    def execute_instruction(self, context):
        """
        Changes the context according to the execution 
        of current instruction.
        """
        raise NotImplementedError()
    
    def custom_instruction_index_change(self):
        """
        Returns True if executor changes the index of instruction manually
        and it should not be changed by simulator.
        """
        raise NotImplementedError()
    
    def consumes_cpu_time(self):
        """
        Returns True if execution uses cpu time - used for scheduling.
        """
        raise NotImplementedError()
    
class HookExecutor(InstructionExecutor):
    """
    Class executes hooks.
    """
    
    def __init__(self):
        self._hooks = []     # List of hooks
    
    def add_hook(self, hook):
        """ Adds hook to the list """
        self._hooks.append(hook)
        return self
    
    def remove_hook(self, hook):
        """ Removes hook from the list """
        self._hooks.remove(hook)
        return self
    
    
    def execute_instruction(self, context):
        """ Overriden """
        for h in self._hooks:
            h.execute(context)
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return True
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return False
    
    def consumes_cpu_time(self):
        """ Overriden """
        return False
    
class PrintExecutor(InstructionExecutor):
    """
    Excecutor writes current instruction to the stream.
    """
    
    def __init__(self, f):
        self.file = f       # File to write instruction to
        
    def execute_instruction(self, context):
        """ Overriden """
        self.file.write("Host: %s \t" % context.get_current_host().name)
        
        instruction = context.get_current_instruction()
        
        simples = [AssignmentInstruction, CommunicationInstruction, FinishInstruction, ContinueInstruction]
        for s in simples:
            if isinstance(instruction, s):
                self.file.write(unicode(instruction))
                
        if isinstance(instruction, CallFunctionInstruction):
            self.file.write(instruction.function_name + '(...)')
            
        if isinstance(instruction, IfInstruction):
            self.file.write('if (%s) ...' % unicode(instruction.condition))
            
        if isinstance(instruction, WhileInstruction):
            self.file.write('while (%s) ...' % unicode(instruction.condition))
            
        if isinstance(instruction, Process):
            self.file.write('process %s ...' % unicode(instruction.name))
            
        if isinstance(instruction, HostSubprocess):
            self.file.write('subprocess %s ...' % unicode(instruction.name))
                
        self.file.write("\n") 
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return True
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return False
    
    def consumes_cpu_time(self):
        """ Overriden """
        return False
        
class AssignmentInstructionExecutor(InstructionExecutor):
    """
    Executes assignment insructions.
    """
    
    def _compute_current_expression(self, expression, context):
        """
        Computes the expression from current assignment instruction.
        """
        if isinstance(expression, BooleanExpression):
            return expression.clone()
        
        if isinstance(expression, IdentifierExpression):
            return context.expression_checker.populate_variables(expression, context.get_current_host().get_variables())
        
        if isinstance(expression, CallFunctionExpression):
            return context.expression_checker.populate_variables(expression, context.get_current_host().get_variables())
            
        if isinstance(expression, TupleExpression):
            return context.expression_checker.populate_variables(expression, context.get_current_host().get_variables())
            
        if isinstance(expression, TupleElementExpression):
            
            # Clone variable expression
            tuple_expression = context.get_current_host().get_variable(expression.variable_name).clone()
            
            # If not tuple expression, try to reduce. Maybe the result will be a tuple.
            if not isinstance(tuple_expression, TupleExpression):
                tuple_expression = context.expression_reducer.reduce(tuple_expression)
                
            if not isinstance(tuple_expression, TupleExpression):
                raise RuntimeException("Variable '%s' not tuple and cannot get its element %d" 
                                        % (expression.variable_name, expression.index))
                
            if expression.index >= len(tuple_expression.elements):
                raise RuntimeException("Tuple '%s' not tuple and cannot get its element %d" 
                                        % (expression.variable_name, expression.index))
            
            return context.expression_checker.populate_variables(
                            tuple_expression.elements[expression.index],
                            context.get_current_host().get_variables())
            
        raise RuntimeException("Expression '%s' cannot be a value of variable.")

    def execute_instruction(self, context):
        """ Overriden """
        instruction = context.get_current_instruction()
        expression = self._compute_current_expression(instruction.expression, context)
        context.get_current_host().set_variable(instruction.variable_name, expression)
        
        context.get_current_host().mark_changed()
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, AssignmentInstruction)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return False
    
    def consumes_cpu_time(self):
        """ Overriden """
        return True

class ProcessInstructionExecutor(InstructionExecutor):
    """
    Executes process insructions.
    """

    def execute_instruction(self, context):
        """ Overriden """
        process_instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()
        instructions_list = process_instruction.intructions_list

        # If process has at least one instruction
        if len(instructions_list) > 0:
            context.get_current_host().get_current_instructions_context().add_instructions_list(instructions_list, current_process)
        else: 
            # Go to next instruction if proces has no instructions
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            
        context.get_current_host().mark_changed()
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, Process)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return True
    
    def consumes_cpu_time(self):
        """ Overriden """
        return False

class SubprocessInstructionExecutor(InstructionExecutor):
    """
    Executes subprocess insructions.
    """

    def execute_instruction(self, context):
        """ Overriden """
        subprocess_instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()
        instructions_list = subprocess_instruction.instructions_list

        if len(instructions_list) > 0:
            context.get_current_host().get_current_instructions_context().add_instructions_list(instructions_list, current_process)
        else:
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            
        context.get_current_host().mark_changed()
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, HostSubprocess)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return True
    
    def consumes_cpu_time(self):
        """ Overriden """
        return False

class CommunicationInstructionExecutor(InstructionExecutor):
    """
    Executes communication in-out insructions.
    """
    
    def execute_instruction(self, context):
        """ Overriden """
        instruction = context.get_current_instruction()
        channel = context.channels_manager.find_channel_for_current_instruction(context)
        
        if not channel:
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            context.get_current_host().mark_changed()
            return
        
        if instruction.communication_type == COMMUNICATION_TYPE_OUT:
            params = instruction.variables_names
            expressions = []
            for p in params:
                expressions.append(context.get_current_host().get_variable(p).clone())
                
            channel.send_message(context.get_current_host(), expressions)
            
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            context.get_current_host().mark_changed()
            
        else:
            request = context.channels_manager.build_message_request(context.get_current_host(), instruction)
            channel.wait_for_message(request)
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, CommunicationInstruction)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return True
    
    def consumes_cpu_time(self):
        """ Overriden """
        return True

class FinishInstructionExecutor(InstructionExecutor):
    """
    Executes finish (end, stop) insructions.
    """
    
    def execute_instruction(self, context):
        """ Overriden """
        command = context.get_current_instruction()
        
        if command == "end":
            context.get_current_host().finish_successfuly()
        else: # command == "stop"
            context.get_current_host().finish_failed('Executed stop instruction')
            
        context.get_current_host().mark_changed()
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, FinishInstruction)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return False
    
    def consumes_cpu_time(self):
        """ Overriden """
        return True

class ContinueInstructionExecutor(InstructionExecutor):
    """
    Executes continue insructions.
    """
    
    def execute_instruction(self, context):
        """ Overriden """
        instructions_context = context.get_current_host().get_current_instructions_context()
        instructions_context.stack.pop()
        instructions_context.goto_next_instruction()
        
        context.get_current_host().mark_changed()
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, ContinueInstruction)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return True
    
    def consumes_cpu_time(self):
        """ Overriden """
        return True
    
class IfInstructionExecutor(InstructionExecutor):
    """
    Executes if-clause insructions.
    """
    
    def execute_instruction(self, context):
        """ Overriden """
        instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()
        
        contidion_result = context.expression_checker.result(instruction.condition, 
                                        context.get_current_host().get_variables(),
                                        context.functions)
        
        instructions_list = []
        if contidion_result:
            instructions_list = instruction.true_instructions
        else:
            instructions_list = instruction.false_instructions
            
        if len(instructions_list) > 0:
            context.get_current_host().get_current_instructions_context().add_instructions_list(
                                                                            instructions_list, 
                                                                            current_process)
        else:
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
        
        context.get_current_host().mark_changed()
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, IfInstruction)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return True
    
    def consumes_cpu_time(self):
        """ Overriden """
        return True
    
class WhileInstructionExecutor(InstructionExecutor):
    """
    Executes while-clause insructions.
    """
    
    def execute_instruction(self, context):
        """ Overriden """
        instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()
        
        contidion_result = context.expression_checker.result(instruction.condition, 
                                        context.get_current_host().get_variables(),
                                        context.functions)
        
        if contidion_result:
            instructions_list = instruction.instructons_list
            
            if len(instructions_list) > 0:
                context.get_current_host().get_current_instructions_context().add_instructions_list(
                                                                                instructions_list, 
                                                                                current_process)
        else:
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
        
        context.get_current_host().mark_changed()
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, WhileInstruction)
    
    def custom_instruction_index_change(self):
        """ Overriden """
        return True
    
    def consumes_cpu_time(self):
        """ Overriden """
        return True
    
class Executor():
    """
    Class executes instructions to move simulation to the nest state.
    """
    
    def __init__(self):
        self.executors = []     # List of instruction executors
    
    def prepend_instruction_executor(self, instruction_executor):
        """
        Adds instruction executor at the beginning of the executors list.
        """
        self.executors.insert(0, instruction_executor)
    
    def append_instruction_executor(self, instruction_executor):
        """
        Adds instruction executor to the end of the executors list.
        """
        self.executors.append(instruction_executor)
    
    def execute_instruction(self, context):
        """
        Executes one instruction of context which is equal to going to the next state.
        The executed instruction is get from the current host of the context.
        """
        cpu_time_consumed = False
        # Execute instructions in one instructions context until 
        # instruction that consumes cpu time is executes.
        # Method also checks whether the host was not stopped or ended meanwhile
        # and whether the context is not finished 
        # (fe. when there is only information about instructions printed)
        while not cpu_time_consumed and not context.get_current_host().finished() \
                and not context.get_current_host().get_current_instructions_context().finished():
            
            instr = context.get_current_instruction()
            custom_instructions_index_change = False
            
            for e in self.executors:
                if e.can_execute_instruction(instr):
                    
                    # Execute current instruction by current executor. 
                    # Executor can change index.
                    e.execute_instruction(context)
                    if e.consumes_cpu_time():
                        cpu_time_consumed = True
                        
                    # Check if executor changes instructions index itself.
                    if e.custom_instruction_index_change():
                        custom_instructions_index_change = True

            # If index is not changed by executor,
            # method has to change it. 
            if not custom_instructions_index_change:
                context.get_current_host().get_current_instructions_context().goto_next_instruction()
           
        # Change the index of instructions in current host.
        # It for example moves index to enxt instructions context.
        # (Uses scheduler)     
        context.get_current_host().goto_next_instructions_context()
    