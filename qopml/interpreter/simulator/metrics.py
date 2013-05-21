'''
Created on 14-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class HostMetrics():
    """
    Whole metrics configuration for particular hosts.
    Configuration includes the name, the device configuration params,
    three types of metrics: normal, plus and star.
    """
    def __init__(self, name):
        self.name = name
        self.configurations = []
        
        self.normal_blocks = []
        self.plus_blocks = []
        self.star_blocks = []
        
        self.connected_hosts = []

class Block():
    """
    Block of metrics containing all metrics with the same params 
    and service params definition.
    """
    def __init__(self, params, service_params):
        self.params = params
        self.service_params = service_params
        self.metrics = []

class Metric():
    """
    One metrics row with defined: call arguments and service arguments.
    Call arguments are used for metric lookup and service arguments are used
    to define new state or by modules to calculate some informations.
    """
    def __init__(self, function_name, arguments, service_arguments):
        self.function_name = function_name
        self.arguments = arguments
        self.service_arguments = service_arguments    

class Manager():
    """
    Metrics manager. 
    Class used for operations on metrics: searching, etc.
    """
    def __init__(self, host_metrics):
        self.host_metrics = host_metrics