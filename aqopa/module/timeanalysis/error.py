'''
Created on 01-06-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from aqopa.simulator.error import RuntimeException

class TimeSynchronizationException(RuntimeException):
    """
    Error occurs when the current times of hosts are not synchronized
    and they want to exchange messages.
    For example host A tries to send message to host B in time t1, but
    host B is already in time t2 > t1.
    """
    pass
    