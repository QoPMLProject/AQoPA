'''
Created on 31-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class TimeTrace():
    
    def __init__(self, host, instruction, started_at, length):
        """ """
        self.host           = host
        self.instruction    = instruction
        self.started_at     = started_at
        self.length         = length
        
class ChannelMessageTrace():
    
    def __init__(self, channel, message_index, sender, sent_at, 
                 receiver = None, received_at = None):
        """ """
        self.channel        = channel
        self.message_index  = message_index
        self.sender         = sender
        self.sent_at        = sent_at
        self.receiver       = receiver
        self.received_at    = received_at
        
    def add_receiver(self, receiver, received_at):
        """ """
        self.receiver       = receiver
        self.received_at    = received_at
