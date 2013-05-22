'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

# Hook, Context, Executor

HOOK_TYPE_PRE_HOST_LIST_EXECUTION = 1

class Hook():
    pass

class Context():
    
    def __init__(self):
        self.hosts = []                 # List of all hosts in this context
        self.channels = []              # List of all channels in this context
        self.functions = []             # List of all functions in this context
        
        self.expression_checker = None
        self.expression_reducer = None
    
    def all_hosts_finished(self):
        """
        Returns True if all hosts are in FINISHED state
        and no next states can be generated.
        """
        raise NotImplementedError()
    
    def hosts_loop_ended(self):
        """
        Returns True when all hosts tried to go to next state in current loop.
        Going to the next state is done for one host in next state generation step, so to finish
        the one loop for all (let N) host, simulater must call function N times.
        """
        raise NotImplementedError()
    
    def any_host_changed(self):
        """
        Return True in any host has changed in last next state generation loop performed 
        for all hosts.
        """
        raise NotImplementedError()
    
    def mark_all_hosts_unchanged(self):
        """
        Sets the state of all hosts to unchanged. Used before each next state generation loop.
        """
        raise NotImplementedError()
    
    def goto_next_host(self):
        """
        Context is moved to the next host so that next state generation step is performed for next host.
        """
        raise NotImplementedError()
    
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
        self.hooks = []     # List of hooks
    
    def add_hook(self, hook):
        """ Adds hook to the list """
        self.hooks.append(hook)
        return self
    
    def remove_hook(self, hook):
        """ Removes hook from the list """
        self.hooks.remove(hook)
        return self
    
    def execute_instruction(self, context):
        """
        Executes one instruction of context.
        The executed instruction is get from the current host of the context.
        """
        raise NotImplementedError()
    
class PrintExecutor(InstructionExecutor):
    """
    Excecutor writes current instruction to the stream.
    """
    
    def __init__(self, f):
        self.file = f       # File to write instruction to
        
class AssignmentInstructionExecutor(InstructionExecutor):
    """
    Executes assignment insructions.
    """
    
    def _compute_current_expression(self, expression, context):
        """
        Computes the expression from current assignment instruction.
        """
        raise NotImplementedError()

class ProcessInstructionExecutor(InstructionExecutor):
    """
    Executes process insructions.
    """
    pass

class SubprocessInstructionExecutor(InstructionExecutor):
    """
    Executes subprocess insructions.
    """
    pass

class CommunicationInstructionExecutor(InstructionExecutor):
    """
    Executes communication in-out insructions.
    """
    pass

class FinishInstructionExecutor(InstructionExecutor):
    """
    Executes finish (end, stop) insructions.
    """
    pass

class ContinueInstructionExecutor(InstructionExecutor):
    """
    Executes continue insructions.
    """
    pass
    
class IfInstructionExecutor(InstructionExecutor):
    """
    Executes if-clause insructions.
    """
    pass
    
class WhileInstructionExecutor(InstructionExecutor):
    """
    Executes while-clause insructions.
    """
    pass
    
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
        raise NotImplementedError()


    