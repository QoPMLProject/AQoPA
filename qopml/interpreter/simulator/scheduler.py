'''
Created on 15-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class Scheduler():
    
    def __init__(self, host):
        raise NotImplementedError()
    
    def finished(self):
        """
        Returns True if host is finished.
        """
        raise NotImplementedError()
    
    def get_current_context(self):
        """
        Returns instructions context executed in current state.
        """
        raise NotImplementedError()
    
    def goto_next_instruction_context(self):
        """
        Move hosts state to next instructions list.
        """
        raise NotImplementedError()

class FifoScheduler(Scheduler):
    
    def _build_context(self):
        pass
    
    def __init__(self, host):
        """ """
        self.host = host
        

class RoundRobinScheduler(Scheduler):
    pass

        
SCHEDULE_ALGORITHM_ROUND_ROBIN  = 'rr'
SCHEDULE_ALGORITHM_FIFO         = 'fifo'

def create(algorithm):
    if algorithm == SCHEDULE_ALGORITHM_FIFO:
        return FifoScheduler()
    elif  algorithm == SCHEDULE_ALGORITHM_ROUND_ROBIN:
        return RoundRobinScheduler()
    