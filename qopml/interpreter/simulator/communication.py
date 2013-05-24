'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
from qopml.interpreter.model import original_name, name_indexes

class Channel():
    """
    Simulation channel.
    """
    
    def __init__(self, name):
        self.name = name
        
        self._connected_hosts        = []
        self._connected_processes    = []
        
    def clone(self):
        return Channel(self.original_name())
        
    def original_name(self):
        """
        Return original name of channel - without indexes.
        """
        return original_name(self.name)
    
    def indexes(self):
        """
        Return name indexes of channel 
        """
        return name_indexes(self.name)
    
    def connect_with_host(self, host):
        """
        Connect channel with host if it is not already connected.
        Make bidirectional connection: If channel was not connected to host, 
        call also function that connects host with channel.
        """
        if host in self._connected_hosts:
            return
        self._connected_hosts.append(host)
        host.connect_with_channel(self)
    
    def connect_with_process(self, process):
        """
        Connect channel with process if it is not already connected.
        Make bidirectional connection: If channel was not connected to process, 
        call also function that connects process with channel.
        """
        if process in self._connected_processes:
            return
        self._connected_hosts.append(process)
        process.connect_with_channel(self)
        
    def add_name_index(self, index):
        """
        Add index to the name of channel. 
        Before: name = ch, index = 1. After: name = ch.1
        """
        self.name += ".%d" % index
    
    def get_queue_of_sending_hosts(self, number):
        """
        Return list of hosts who had sent messages to channel before.
        Works only for asynchronous channels. For synchronous channels always is returned empty array.
        Returns at most number hosts.
        """
        raise NotImplementedError()
    
    def get_number_of_dropped_messages(self):
        """
        Return number of messages dropped on this channel  
        """
        raise NotImplementedError()
    
    def wait_for_message(self, request):
        raise NotImplementedError()
    
    def send_message(self, host, expressions):
        raise NotImplementedError()
    
class Manager():
    """ Channels manager class """
    
    def __init__(self, channels):
        self.channele = channels
        