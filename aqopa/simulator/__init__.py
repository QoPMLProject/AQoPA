'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.simulator.state import HOOK_TYPE_PRE_HOST_LIST_EXECUTION,\
    HookExecutor, HOOK_TYPE_PRE_INSTRUCTION_EXECUTION,\
    HOOK_TYPE_POST_INSTRUCTION_EXECUTION, HOOK_TYPE_SIMULATION_FINISHED
    
from aqopa.simulator.error import RuntimeException,\
    EnvironmentDefinitionException, InfiniteLoopException

class Simulator():
    """
    Interpreter's Model Simulator
    """
    
    def __init__(self, context):
        self.context = context  # Simulation context (keeps information about current state)
        self._ready = False
        self._hooks = {}
        self._modules = []
        
        self._executor = None
        self._before_instruction_executor = HookExecutor()
        self._after_instruction_executor = HookExecutor()
        
        self._first_loop = True
        self._infinite_loop_error = False
        
    def _execute_hook(self, hook_type):
        """
        Execute all hooks of given type.
        Pre instruction and post instruction hooks 
        cannot be executed manually.
        """
        
        if hook_type not in self._hooks:
            return
        
        if hook_type in [HOOK_TYPE_PRE_INSTRUCTION_EXECUTION, HOOK_TYPE_POST_INSTRUCTION_EXECUTION]:
            raise RuntimeException("Cannot execute pre instruction and post instruction hooks manually.")
        
        for h in self._hooks[hook_type]:
            h.execute(self.context)
    
    def _install_modules(self):
        """
        Method installs registered modules.
        """
        if self._ready:
            raise EnvironmentDefinitionException('Cannot install modules in prepared simulation, they were already installed.')
        
        for m in self._modules:
            m.install(self)
    
    def _internal_goto_next_state(self):
        """
        Internally goes to next state.
        The difference is that it does not check 
        whether simulation is finished.
        """
        if self.context.has_epoch_ended():
            self._execute_hook(HOOK_TYPE_PRE_HOST_LIST_EXECUTION)
            
            if self._first_loop:
                self._first_loop = False
            else:
                # If nothing has changed in this next state generation loop
                if not self.context.any_host_changed():
                    # Throw runtime error if any channel has message to be binded with receiver
                    # or if any channel has dropped a message
                    for ch in self.context.channels_manager.channels:
                        if ch.get_dropped_messages_nb() > 0:
                            raise InfiniteLoopException()
                        
                    for h in self.context.hosts:
                        if not h.finished():
                            h.finish_failed(u'Infinite loop occured on instruction: %s' % 
                                            unicode(h.get_current_instructions_context().get_current_instruction()))
                            
                self.context.mark_all_hosts_unchanged()

        self.context.get_current_host().touch()
        self._executor.execute_instruction(self.context)
        self.context.goto_next_host()
    
    # Public
    
    def get_executor(self):
        """ executor getter """
        return self._executor
    
    def set_executor(self, executor):
        """ executor setter """
        self._executor = executor
        
    def infinite_loop_occured(self):
        """ Returns True if infinite loop occured """
        return self._infinite_loop_error
    
    def register_module(self, module):
        """
        Register module for simulation.
        """
        if self._ready:
            raise EnvironmentDefinitionException('Cannot register module in prepared simulation.')
        self._modules.append(module)
        return self
    
    def prepare(self):
        """
        Prepare simulator to start.
        """
        self._install_modules()
        self._first_loop = True
        self._ready = True
        return self
        
    def register_hook(self, hook_type, hook):
        """
        Registers new hook of particular type
        """
        if hook_type not in self._hooks:
            self._hooks[hook_type] = []
            
        if hook in self._hooks[hook_type]:
            raise EnvironmentDefinitionException(u"Hook '%s' is already registered." % unicode(hook))
        self._hooks[hook_type].append(hook)

        if hook_type == HOOK_TYPE_PRE_INSTRUCTION_EXECUTION:
            self._before_instruction_executor.add_hook(hook)
            
        if hook_type == HOOK_TYPE_POST_INSTRUCTION_EXECUTION:
            self._after_instruction_executor.add_hook(hook)
        
        return self
    
    def is_ready_to_run(self):
        """
        Returns True if simulator is ready to run
        """
        return self._ready
    
    def is_simulation_finished(self):
        """
        Returns True if simulation has ended.
        Simulation can end with success or error (eg. infinite loop occured).
        """
        return self.is_ready_to_run() and (self.context.all_hosts_finished() or self.infinite_loop_occured())
    
    def run(self):
        """
        Runs whole simulation process.
        """
        if not self.is_ready_to_run():
            raise EnvironmentDefinitionException("Simulation is not yet ready to run.")

        self._executor.prepend_instruction_executor(self._before_instruction_executor)
        self._executor.append_instruction_executor(self._after_instruction_executor)
        
        while not self.is_simulation_finished():
            try: 
                self._internal_goto_next_state()
            except InfiniteLoopException:
                self._infinite_loop_error = True

        self._execute_hook(HOOK_TYPE_SIMULATION_FINISHED)
        
