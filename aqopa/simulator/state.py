'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.model import BooleanExpression, IdentifierExpression,\
    CallFunctionExpression, TupleExpression, TupleElementExpression,\
    AssignmentInstruction, CommunicationInstruction, FinishInstruction,\
    ContinueInstruction, CallFunctionInstruction, IfInstruction,\
    WhileInstruction, HostSubprocess, COMMUNICATION_TYPE_OUT,\
    original_name, name_indexes, BreakInstruction

from aqopa.simulator.error import RuntimeException

class Context():
    
    def __init__(self, version):
        
        self.version = version
        
        self.hosts = []                 # List of all hosts in this context
        self.functions = []             # List of all functions in this context
        
        self.expression_populator = None
        self.expression_checker = None
        self.expression_reducer = None

        self.metrics_manager = None
        self.channels_manager = None
        self.algorithms_resolver = None
        
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
    
    def get_progress(self):
        """
        Returs a number between 0 and 1 representing the progress of
        simulation.
        """
        all = 0
        ended = 0
        for h in self.hosts:
            if h.finished():
                ended += 1
            all += 1
        return float(ended)/float(all) if all > 0 else 0
    
    def has_epoch_ended(self):
        """
        Returns True when all hosts finished their epoch. Each host tried to execute an instruction
        in all its instruction contexts.
        Going to the next state is done for one host in next state generation step, so to finish
        the one loop for all hosts' instruction contexts (let N), simulator must call function N times.
        """
        for h in self.hosts:
            if not h.finished():
                if not h.has_epoch_ended():
                    return False
        return True

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
        Sets the state of all hosts to unchanged.
        Used before each next state generation loop.
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
HOOK_TYPE_SIMULATION_FINISHED           = 4

class Hook():
    """
    Hooks are executed in many places of simulation.
    Hooks can be added by modules.
    """
    
    def execute(self, context, **kwargs):
        """
        Method changes the context. 
        
        May return exectution result if used in executors hook.
        """
        raise NotImplementedError()
        
# ----------- Host Process

HOST_STATUS_RUNNING = 1
HOST_STATUS_FINISHED = 2

class Host():
    """
    Simulation equivalent of host
    """
    
    def __init__(self, name, instructions_list, predefined_variables=None):
        self.name = name
        self.instructions_list = instructions_list

        self._variables = {}
        if predefined_variables is not None:
            self._variables = predefined_variables
        
        self._scheduler = None
        self._changed = False
        self._status = HOST_STATUS_RUNNING 
        self._finish_error = None

        self._touches = 0 # How many times the host has been touched.
        # When touches is greater than number of instruction contexts, the epoch end.
        
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
        
    def get_name_index(self):
        """
        Returns repetition index of this host
        """
        elems = self.name.split('.')
        if len(elems) < 2:
            return 0
        return int(elems[1])
        
    def set_scheduler(self, scheduler):
        """Set scheduler"""
        self._scheduler = scheduler
        
    def set_variable(self, name, value):
        """Set hotst's variable"""
        self._variables[name] = value
        
    def get_variable(self, name):
        """ Get host's variable """
        if name not in self._variables:
            raise RuntimeException("Variable '%s' undefined in host '%s'." % (name, self.name))
        return self._variables[name]

    def has_variable(self, name):
        """ Returns True if variable is defined """
        return name in self._variables

    def get_variables(self):
        """ Get variables dict """
        return self._variables

    def touch(self):
        """
        Host is touched before the execution of its instruction.
        It is used to check if all processes were tried to execute - hence whether the epoc has ended.
        Each time is touching is started when the first instruction context is executed.
        """
        # Touches equal to zero means that new epoch has been started.
        # The counter is started when the forst context is executed.
        if self._touches == 0:
            if self._scheduler.get_current_context_index() == 0:
                self._touches += 1
        else:
            self._touches += 1

    def has_epoch_ended(self):
        """
        Returns True when host tried to execute each instructions context in current epoch.
        """
        return self._touches > self._scheduler.get_contexts_number()

    def mark_changed(self):
        """ Marks host changed. Means that host have changes in last state. """
        self._changed = True
        
    def mark_unchanged(self):
        """ Marks host unchanged. Clears changes from last state. """
        self._changed = False
        self._touches = 0
        
    def has_changed(self):
        """ Returns True if host has changed """
        return self._changed
        
    def goto_next_instructions_context(self):
        """
        Moves host to next instructions context.
        """
        self._scheduler.goto_next_instruction_context()
        if self._scheduler.finished() and not self.finished():
            self.finish_successfuly()
        
    def get_current_instructions_context(self):
        """
        Returns the current instructions context retrieved from scheduler.
        """
        return self._scheduler.get_current_context()

    def get_all_instructions_contexts(self):
        """
        Returns all instructions context retrived from scheduler.
        """
        return self._scheduler.get_all_contexts()

    def get_instructions_context_of_instruction(self, instruction):
        """
        Returns instruction context with the instruction from parameter
        as the current instruction
        """
        return self._scheduler.get_instructions_context_of_instruction(instruction)
    
    def get_current_process(self):
        """ """
        return self.get_current_instructions_context().get_process_of_current_list()

    def check_if_finished(self):
        """
        Method checks if host has no more instructions to execute
        and updates host's status.
        """
        if self._scheduler.finished():
            if self._status == HOST_STATUS_RUNNING:
                self._status = HOST_STATUS_FINISHED
                self._finish_error = None

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
        
    def get_finish_error(self):
        """ """
        return self._finish_error
    
    
class Process():
    
    def __init__(self, name, instructions_list):
        self.name = name
        self.instructions_list = instructions_list
    
        self.follower = None
        
    def original_name(self):
        """"""
        return original_name(self.name)
        
    def add_name_index(self, index):
        """
        Add index to the name. 
        Before: name = ch, index = 1. After: name = ch.1
        """
        self.name += ".%d" % index
        
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
    
    def __init__(self, host):
        self.host = host
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
        return self._get_current_list().get_current_instruction() if self._get_current_list() is not None else None
        
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
        # Go to next instruction in current list
        self._get_current_list().goto_next_instruction()
        # While current list is finished but context is not finished
        while not self.finished() and self._get_current_list().finished():
            # Remove current list
            self.stack.pop()
            # If context is still not finished and new current list is not LOOP
            # Go to next instruction in new current list
            if not self.finished():
                if not isinstance(self._get_current_list().get_current_instruction(), WhileInstruction):
                    self._get_current_list().goto_next_instruction()
            # And repeat this process
        # When moving to the next instruction in instructions context is finished
        # update host's status - it may become finished
        self.host.check_if_finished()

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
    
    def execute_instruction(self, context, **kwargs):
        """
        Changes the context according to the execution of current instruction.
        The second parameter `kwargs` keeps variables created be previous executors.
        Returns the result of execution containing information 
        about execution and the next steps: should it omit next executors?,
        does it consume cpu?, does it implement custom index management? etc.
        """
        raise NotImplementedError()
    
class ExecutionResult():
    """
    The result of execution of one instruction by one executor.
    """
    
    def __init__(self, consumes_cpu=False,
                 custom_index_management=False,
                 finish_instruction_execution=False,
                 result_kwargs=None):
        """ """
        self.consumes_cpu = consumes_cpu
        self.custom_index_management = custom_index_management
        self.finish_instruction_execution = finish_instruction_execution
        self.result_kwargs = result_kwargs
    
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
    
    
    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        consumes_cpu = False 
        custom_index_management = False 
        finish_instruction_execution = False

        exec_kwargs = kwargs
        for h in self._hooks:
            result = h.execute(context, **exec_kwargs)
            if result:
                if result.consumes_cpu:
                    consumes_cpu = True
                if result.custom_index_management:
                    custom_index_management = True
                if result.finish_instruction_execution:
                    finish_instruction_execution = True
                if result.result_kwargs is not None:
                    exec_kwargs.update(result.result_kwargs)

                    
        return ExecutionResult(consumes_cpu, custom_index_management, 
                               finish_instruction_execution,
                               result_kwargs=exec_kwargs)
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return True
        
class PrintExecutor(InstructionExecutor):
    """
    Excecutor writes current instruction to the stream.
    """
    
    def __init__(self, f):
        self.file = f       # File to write instruction to
        
        self.result = ExecutionResult()
        
    def execute_instruction(self, context, **kwargs):
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
        
        return self.result
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return True
        
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
        
        if isinstance(expression, IdentifierExpression) or isinstance(expression, CallFunctionExpression) \
                or isinstance(expression, TupleExpression) or isinstance(expression, TupleElementExpression):
            # Population of variables which were previously populated (ie. additional attrs)
            return context.expression_populator.populate(expression, context.get_current_host())

        raise RuntimeException("Expression '%s' cannot be a value of variable.")

    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        instruction = context.get_current_instruction()
        expression = self._compute_current_expression(instruction.expression, context)
        expression = context.expression_reducer.reduce(expression)

        context.get_current_host().set_variable(instruction.variable_name, expression)
        context.get_current_host().mark_changed()
        
        return ExecutionResult(consumes_cpu=True)
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, AssignmentInstruction)
    
class CallFunctionInstructionExecutor(InstructionExecutor):
    """
    Executes call function insructions.
    Dummy executor just to show that call function instruction 
    consumes cpu and changes host.
    """
    
    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        context.get_current_host().mark_changed()
        
        return ExecutionResult(consumes_cpu=True)
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, CallFunctionInstruction)
    
class ProcessInstructionExecutor(InstructionExecutor):
    """
    Executes process insructions.
    """

    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        process_instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()
        instructions_list = process_instruction.instructions_list

        # If process has at least one instruction
        if len(instructions_list) > 0:
            context.get_current_host().get_current_instructions_context().add_instructions_list(instructions_list, current_process)
        else: 
            # Go to next instruction if proces has no instructions
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            
        context.get_current_host().mark_changed()

        return ExecutionResult(custom_index_management=True)
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, Process)
    
class SubprocessInstructionExecutor(InstructionExecutor):
    """
    Executes subprocess insructions.
    """

    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        subprocess_instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()
        instructions_list = subprocess_instruction.instructions_list

        if len(instructions_list) > 0:
            context.get_current_host().get_current_instructions_context().add_instructions_list(instructions_list, current_process)
        else:
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            
        context.get_current_host().mark_changed()

        return ExecutionResult(custom_index_management=True)
                
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, HostSubprocess)
    

class CommunicationInstructionExecutor(InstructionExecutor):
    """
    Executes communication in-out insructions.
    """
    
    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        instruction = context.get_current_instruction()
        channel = context.channels_manager.find_channel_for_current_instruction(context)

        if context.channels_manager.find_channel(instruction.channel_name) is None:
            raise RuntimeException("Channel {0} undefined.".format(instruction.channel_name))

        if not channel:
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            context.get_current_host().mark_changed()
            return ExecutionResult(consumes_cpu=True,
                                   custom_index_management=True)
        
        if instruction.communication_type == COMMUNICATION_TYPE_OUT:
            if kwargs is not None and 'sent_message' in kwargs:
                message = kwargs['sent_message']
            else:
                message = context.channels_manager.build_message(
                    context.get_current_host(),
                    context.get_current_host().get_variable(instruction.variable_name).clone(),
                    context.expression_checker)
                kwargs['sent_message'] = message
            channel.send_message(context.get_current_host(), message, context.channels_manager.get_router())

            # Go to next instruction
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
            context.get_current_host().mark_changed()
            
        else:
            if kwargs is not None and 'messages_request' in kwargs:
                request = kwargs['messages_request']
            else:
                request = context.channels_manager.build_message_request(context.get_current_host(), instruction,
                                                                         context.expression_populator)
                kwargs['messages_request'] = request

            channel.wait_for_message(request)
            
        return ExecutionResult(consumes_cpu=True, 
                               custom_index_management=True,
                               result_kwargs=kwargs)
                
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, CommunicationInstruction)
    
class FinishInstructionExecutor(InstructionExecutor):
    """
    Executes finish (end, stop) insructions.
    """
    
    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        instruction = context.get_current_instruction()
        if instruction.command == "end":
            for h in context.hosts:
                h.finish_successfuly()
        else:
            msg = 'Executed stop instruction in host {0}'.format(context.get_current_host().name)
            for h in context.hosts:
                if h == context.get_current_host():
                    h.finish_failed('Executed stop instruction')
                else:
                    h.finish_failed(msg)
            
        context.get_current_host().mark_changed()
        
        return ExecutionResult(consumes_cpu=True)
        
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, FinishInstruction)
    
class ContinueInstructionExecutor(InstructionExecutor):
    """
    Executes continue insructions.
    """
    
    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        instructions_context = context.get_current_host().get_current_instructions_context()
        instruction = instructions_context.get_current_instruction()
        while instruction and not isinstance(instruction, WhileInstruction):
            instructions_context.stack.pop()
            instruction = instructions_context.get_current_instruction()

        context.get_current_host().mark_changed()

        return ExecutionResult(consumes_cpu=True, 
                               custom_index_management=True)
                
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, ContinueInstruction)

class BreakInstructionExecutor(InstructionExecutor):
    """
    Executes continue insructions.
    """

    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        instructions_context = context.get_current_host().get_current_instructions_context()
        instruction = instructions_context.get_current_instruction()
        while instruction and not isinstance(instruction, WhileInstruction):
            instructions_context.stack.pop()
            instruction = instructions_context.get_current_instruction()
        instructions_context.goto_next_instruction()

        context.get_current_host().mark_changed()

        return ExecutionResult(consumes_cpu=True,
                               custom_index_management=True)

    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, BreakInstruction)
    
class IfInstructionExecutor(InstructionExecutor):
    """
    Executes if-clause insructions.
    """
    
    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()
        
        contidion_result = context.expression_checker.result(instruction.condition, 
                                        context.get_current_host())

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

        return ExecutionResult(consumes_cpu=True, 
                               custom_index_management=True)
                
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, IfInstruction)
    
    
class WhileInstructionExecutor(InstructionExecutor):
    """
    Executes while-clause insructions.
    """
    
    def execute_instruction(self, context, **kwargs):
        """ Overriden """
        instruction = context.get_current_instruction()
        current_process = context.get_current_host().get_current_process()

        contidion_result = context.expression_checker.result(instruction.condition,
                                        context.get_current_host())
        
        if contidion_result:
            instructions_list = instruction.instructions
            
            if len(instructions_list) > 0:
                context.get_current_host().get_current_instructions_context().add_instructions_list(
                                                                                instructions_list, 
                                                                                current_process)
        else:
            context.get_current_host().get_current_instructions_context().goto_next_instruction()
        
        context.get_current_host().mark_changed()

        return ExecutionResult(consumes_cpu=True, 
                               custom_index_management=True)
                
    def can_execute_instruction(self, instruction):
        """ Overriden """
        return isinstance(instruction, WhileInstruction)
    
    
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
        
        execution_result = None
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

            exec_kwargs = {}
            for e in self.executors:
                if e.can_execute_instruction(instr):
                    
                    # Execute current instruction by current executor. 
                    # Executor can change index.
                    execution_result = e.execute_instruction(context, **exec_kwargs)
                    
                    # If executor does not return result
                    # create a default one
                    if not execution_result:
                        execution_result = ExecutionResult()
                    
                    if execution_result.consumes_cpu:
                        cpu_time_consumed = True
                        
                    # Check if executor changes instructions index itself.
                    if execution_result.custom_index_management:
                        custom_instructions_index_change = True

                    if execution_result.result_kwargs is not None:
                        exec_kwargs.update(execution_result.result_kwargs)

                # Omit other executors if the result says that
                if execution_result.finish_instruction_execution:
                    break

            # If index is not changed by executor,
            # method has to change it. 
            if not custom_instructions_index_change:
                context.get_current_host().get_current_instructions_context().goto_next_instruction()
           
            # Finish execution of instruction
            if execution_result and execution_result.finish_instruction_execution:
                break
           
        # Change the index of instructions in current host
        # according to the scheduler algorithm.
        # It moves index to next instructions context.
        context.get_current_host().goto_next_instructions_context()
    