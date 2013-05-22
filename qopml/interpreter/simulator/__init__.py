'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from qopml.interpreter.simulator.state import HOOK_TYPE_PRE_HOST_LIST_EXECUTION,\
    HookExecutor

class EnvironmentDefinitionException(Exception):
    
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args)
        
        self.errors = []
        if 'errors' in kwargs:
            self.errors = kwargs['errors']
            del kwargs['errors']

class RuntimeException(Exception):
    pass

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
        
    def _execute_hook(self, hoot_type):
        raise NotImplementedError()
    
    def _install_modules(self):
        """
        Method installs registered modules.
        """
        if self._ready:
            raise EnvironmentDefinitionException('Cannot install modules in prepared simulation. They were already installed.')
        
        for m in self._modules:
            m.install(self)
    
    def _internal_goto_next_state(self):
        """
        Internally goes to next state.
        The difference is that it does not check 
        whether simulation is finished.
        """
        
        if self.context.hosts_loop_ended():
            self._execute_hook(HOOK_TYPE_PRE_HOST_LIST_EXECUTION)
            
            if self._first_loop:
                self._first_loop = False
            else:
                # If nothing has changed in this next state generation loop
                if not self.context.any_host_changed():
                    # Throw runtime error if any channel has message to be binded with receiver
                    # or if any channel has dropped a message
                    for ch in self.context.channels:
                        if len(ch.get_queue_of_sending_hosts(1)) > 0 or ch.get_number_of_dropped_messages() > 0:
                            raise RuntimeException(u"Infinite loop occured")
                        
                    for h in self.context.hosts:
                        if not h.is_finished():
                            h.finish_with_error(RuntimeException(u"Infinite loop occured"))
                            
                self.context.mark_all_hosts_unchanged()
                    
        self._executor.execute_instruction(self.context)
        self.context.goto_next_host()
    
    # Public
    
    @property
    def executor(self):
        """ executor getter """
        return self._executor
    
    @executor.setter
    def executor(self, executor):
        """ executor setter """
        self._executor = executor
        self._executor.prepend_instruction_executor()(self._before_instruction_executor)
        self._executor.append_instruction_executor(self._after_instruction_executor)
    
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
            raise EnvironmentDefinitionException(u"Hook '%s' is already registered" % unicode(hook))
        self._hooks[hook_type].append(hook)
        return self
    
    def is_ready_to_run(self):
        """
        Returns True if simulator is ready to run
        """
        return self._ready
    
    def is_simulation_finished(self):
        """
        Returns True if simulation has ended.
        Simulation can end with success or error.
        """
        return self.is_ready_to_run() and self.context.all_hosts_finished()
    
    def run(self):
        """
        Runs whole simulation process.
        """
        if not self.is_ready_to_run():
            raise EnvironmentDefinitionException("Simulation is not yet ready to run")
        
        while not self.is_simulation_finished():
            self._internal_goto_next_state()
        
    def goto_next_state(self):
        """
        Simulation goes to next state.
        """
        if not self.is_ready_to_run():
            raise EnvironmentDefinitionException("Simulation is not yet ready to run")
        
        if not self.is_simulation_finished():
            self._internal_goto_next_state()