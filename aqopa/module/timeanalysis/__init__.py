from aqopa import module
from aqopa.module.timeanalysis.parser import ConfigParserExtension, ModelParserExtension
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
                                        # (divided by simulators - the reason for dict)
        self.current_times  = {}        # Current times of hosts, key - host instance divided by simulators
        
        self.guis           = {}        # Divided by simulators - the reason for dict
        
        self.channel_request_times = {}  # Times when a request has been created
                                         # (divided by simulators - the reason for dict)
        self.channel_message_times = {}  # Times when a message has been sent
                                         # (divided by simulators - the reason for dict)
        self.channel_message_sending_times = {}  # The time of sending a message
                                         # (divided by simulators - the reason for dict)
        self.channel_message_traces = {}  # Time traces for communication steps
                                          # (divided by simulators - the reason for dict)

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)
    
    def extend_model_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(ModelParserExtension())
        return parser

    def extend_metrics_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(MetricsParserExtension())
        return parser

    def extend_config_parser(self, parser):
        """
        Overriden
        """
        parser.add_extension(ConfigParserExtension())
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
    
    def add_timetrace(self, simulator, host, process, instruction, expressions_details, started_at, length):
        """ """
        if simulator not in self.timetraces:
            self.timetraces[simulator] = []
        tt = self.timetraces[simulator]
        tt.append(TimeTrace(host, process, instruction, expressions_details, started_at, length))

    def get_timetraces(self, simulator):
        """ """
        if simulator not in self.timetraces:
            return []
        return self.timetraces[simulator]

    def add_channel_message_trace(self, simulator, channel, message,
                                  sender, sent_at, sending_time,
                                  receiver, started_waiting_at,
                                  started_receiving_at, receiving_time):
        if simulator not in self.channel_message_traces:
            self.channel_message_traces[simulator] = {}
        if channel not in self.channel_message_traces[simulator]:
            self.channel_message_traces[simulator][channel] = []
        cmt = self.channel_message_traces[simulator][channel]
        cmt.append(ChannelMessageTrace(channel, message,
                                       sender, sent_at, sending_time,
                                       receiver, started_waiting_at,
                                       started_receiving_at, receiving_time))

    def get_channel_message_traces(self, simulator, channel):
        """ """
        if simulator not in self.channel_message_traces:
            return []
        if channel not in self.channel_message_traces[simulator]:
            return []
        return self.channel_message_traces[simulator][channel]

    def get_all_channel_message_traces(self, simulator):
        """ """
        if simulator not in self.channel_message_traces:
            return []
        return self.channel_message_traces[simulator]
        
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

    def add_message_sent_time(self, simulator, message, time):
        """ """
        if simulator not in self.channel_message_times:
            self.channel_message_times[simulator] = {}
        self.channel_message_times[simulator][message] = time

    def get_message_sent_time(self, simulator, message):
        if simulator not in self.channel_message_times:
            return None
        if message not in self.channel_message_times[simulator]:
            return None
        return self.channel_message_times[simulator][message]

    def add_message_sending_time(self, simulator, message, time):
        """ """
        if simulator not in self.channel_message_sending_times:
            self.channel_message_sending_times[simulator] = {}
        self.channel_message_sending_times[simulator][message] = time

    def get_message_sending_time(self, simulator, message):
        if simulator not in self.channel_message_sending_times:
            return None
        if message not in self.channel_message_sending_times[simulator]:
            return None
        return self.channel_message_sending_times[simulator][message]

    def add_request_created_time(self, simulator, request, time):
        """ """
        if simulator not in self.channel_request_times:
            self.channel_request_times[simulator] = {}
        self.channel_request_times[simulator][request] = time

    def get_request_created_time(self, simulator, request):
        if simulator not in self.channel_request_times:
            return None
        if request not in self.channel_request_times[simulator]:
            return None
        return self.channel_request_times[simulator][request]

