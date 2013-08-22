from qopml.interpreter import module
from qopml.interpreter.simulator.state import HOOK_TYPE_PRE_INSTRUCTION_EXECUTION,\
    HOOK_TYPE_SIMULATION_FINISHED
from .hook import PreInstructionHook
from .model import TimeTrace
from qopml.interpreter.module.timeanalysis.model import ChannelMessageTrace
from qopml.interpreter.module.timeanalysis.hook import PrintResultsHook
from qopml.interpreter.module.timeanalysis.parser import MetricsParserExtension

class Module(module.Module):
    """
    """
    
    def __init__(self):
        """ """
        self.simulator      = None      # Simulator instance
        self.hooks          = []        # Module's hooks list
        self.timetraces     = []        # Generated timetraces list
        self.current_times  = {}        # Current times of hosts, key - host instance
        
        self.channel_message_traces = []
        self.channel_next_message_id = {} 
    
    def extend_metrics_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(MetricsParserExtension())
        return parser
    
    def install(self, simulator):
        """
        """
        self.simulator = simulator
        
        hook = PreInstructionHook(self)
        self.hooks.append(hook)
        simulator.register_hook(HOOK_TYPE_PRE_INSTRUCTION_EXECUTION, hook)
        
        hook = PrintResultsHook(self)
        self.hooks.append(hook)
        simulator.register_hook(HOOK_TYPE_SIMULATION_FINISHED, hook)
        
        return simulator
    
    def get_context(self):
        """ """
        return self.simulator.context
    
    def add_timetrace(self, host, instruction, started_at, length):
        """ """
        self.timetraces.append(TimeTrace(host, instruction, started_at, length))
        
    def add_channel_message_trace(self, channel, message_index, sender, sent_at, 
                                  receiver=None, received_at=None):
        self.channel_message_traces.append(ChannelMessageTrace(channel, message_index, 
                                                               sender, sent_at, 
                                                               receiver, received_at))
        
    def set_current_time(self, host, time):
        """ """
        self.current_times[host] = time
        
    def get_current_time(self, host):
        """ """
        if host not in self.current_times:
            self.current_times[host] = 0
        return self.current_times[host]
    
    def get_channel_message_traces(self, channel):
        """ """
        if channel not in self.channel_message_traces:
            return []
        return self.channel_message_traces[channel]
    
    def get_channel_next_message_id(self, channel):
        """ """
        if channel not in self.channel_next_message_id:
            self.channel_next_message_id[channel] = 0
        result = self.channel_next_message_id[channel]
        self.channel_next_message_id[channel] += 1
        return result
        