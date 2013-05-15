'''
Created on 15-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class Scheduler():
    pass

class FifoScheduler(Scheduler):
    pass

class RoundRobinScheduler(Scheduler):
    pass

        
SCHEDULE_ALGORITHM_ROUND_ROBIN  = 'rr'
SCHEDULE_ALGORITHM_FIFO         = 'fifo'

def create(algorithm):
    if algorithm == SCHEDULE_ALGORITHM_FIFO:
        return FifoScheduler()
    elif  algorithm == SCHEDULE_ALGORITHM_ROUND_ROBIN:
        return RoundRobinScheduler()
    