from aqopa import module
from aqopa.simulator.state import HOOK_TYPE_PRE_INSTRUCTION_EXECUTION,\
    HOOK_TYPE_SIMULATION_FINISHED
from .parser import MetricsParserExtension
from .hook import PreInstructionHook
from .model import TimeTrace, ChannelMessageTrace
from .gui import ModuleGui
from .console import PrintResultsHook

class Module(module.Module):
    """
    """
    
    def __init__(self):
        """ """
        self.timetraces     = {}        # Generated timetraces list for each simulator
        self.current_times  = {}        # Current times of hosts, key - host instance divided by simulators 
        
        self.guis           = {}        # Divided by simulators - the reason for dict
        
        self.channel_message_traces = {}  # Divided by simulators - the reason for dict
        self.channel_next_message_id = {} # Divided by simulators - the reason for dict

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)
    
    def extend_metrics_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(MetricsParserExtension())
        return parser
    
    def _install(self, simulator):
        """
        """
        hook = PreInstructionHook(self, simulator)
        simulator.register_hook(HOOK_TYPE_PRE_INSTRUCTION_EXECUTION, hook)
        
        return simulator
    
    def install_console(self, simulator):
        """ Install module for console simulation """
        self._install(simulator)
        
        hook = PrintResultsHook(self, simulator)
        simulator.register_hook(HOOK_TYPE_SIMULATION_FINISHED, hook)
        
        return simulator
        
    def install_gui(self, simulator):
        """ Install module for gui simulation """
        self._install(simulator)
        return simulator
    
    def add_timetrace(self, simulator, host, instruction, started_at, length):
        """ """
        if simulator not in self.timetraces:
            self.timetraces[simulator] = []
        tt = self.timetraces[simulator]
        tt.append(TimeTrace(host, instruction, started_at, length))
        
    def add_channel_message_trace(self, simulator, channel, message_index, sender, sent_at, 
                                  receiver=None, received_at=None):
        if simulator not in self.channel_message_traces:
            self.channel_message_traces[simulator] = []
        cmt = self.channel_message_traces[simulator]
        cmt.append(ChannelMessageTrace(channel, message_index, 
                                                               sender, sent_at, 
                                                               receiver, received_at))
        
    def set_current_time(self, simulator, host, time):
        """ """
        if simulator not in self.current_times:
            self.current_times[simulator] = {}
        self.current_times[simulator][host] = time
        
    def get_current_time(self, simulator, host):
        """ """
        if simulator not in self.current_times:
            self.current_times[simulator] = {}
        if host not in self.current_times[simulator]:
            self.current_times[simulator][host] = 0
        return self.current_times[simulator][host]
    
    def get_channel_message_traces(self, simulator, channel):
        """ """
        if simulator not in self.channel_message_traces:
            return []
        if channel not in self.channel_message_traces[simulator]:
            return []
        return self.channel_message_traces[simulator][channel]
    
    def get_channel_next_message_id(self, simulator, channel):
        """ """
        if simulator not in self.channel_next_message_id:
            self.channel_next_message_id[simulator] = {}
        if channel not in self.channel_next_message_id[simulator]:
            self.channel_next_message_id[simulator][channel] = 0
        result = self.channel_next_message_id[simulator][channel]
        self.channel_next_message_id[simulator][channel] += 1
        return result
        