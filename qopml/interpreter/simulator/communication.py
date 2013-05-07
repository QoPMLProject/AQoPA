'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''


class Channel():
    
    def get_queue_of_sending_hosts(self, number):
        """
        Returns list of hosts who had sent messages to channel before.
        Works only for asynchronous channels. For synchronous channels always is returned empty array.
        Returns at most number hosts.
        """
        pass
    
    def get_number_of_dropped_messages(self):
        """
        Returns number of messages dropped on this channel  
        """
        pass