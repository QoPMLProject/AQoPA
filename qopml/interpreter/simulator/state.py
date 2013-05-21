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
        pass
    
    def hosts_loop_ended(self):
        """
        Returns True when all hosts tried to go to next state in current loop.
        Going to the next state is done for one host in next state generation step, so to finish
        the one loop for all (let N) host, simulater must call function N times.
        """
        pass
    
    def any_host_changed(self):
        """
        Return True in any host has changed in last next state generation loop performed 
        for all hosts.
        """
        pass
    
    def mark_all_hosts_unchanged(self):
        """
        Sets the state of all hosts to unchanged. Used before each next state generation loop.
        """
        pass
    
    def goto_next_host(self):
        """
        Context is moved to the next host so that next state generation step is performed for next host.
        """
        pass
    
class Executor():
    
    def execute_instruction(self, context):
        """
        Executes one instruction of context which is equal to going to the next state.
        The executed instruction is get from the current host of the context.
        """
        pass



    