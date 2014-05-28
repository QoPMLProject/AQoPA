'''
Created on 31-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''


class TimeTrace():
    
    def __init__(self, host, process, instruction, expressions_details, started_at, length):
        """ """
        self.host = host
        self.process = process
        self.instruction = instruction
        self.expressions_details = expressions_details
        self.started_at = started_at
        self.length = length


class ChannelMessageTrace():
    
    def __init__(self, channel, message,
                 sender, sent_at, sending_time,
                 receiver, started_waiting_at,
                 started_receiving_at, receiving_time):
        """ """
        self.channel = channel
        self.message = message
        self.sender = sender
        self.sent_at = sent_at
        self.sending_time = sending_time
        self.receiver = receiver
        self.started_waiting_at = started_waiting_at
        self.received_at = started_receiving_at
        self.receiving_time = receiving_time
        
