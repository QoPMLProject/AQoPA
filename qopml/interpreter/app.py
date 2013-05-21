'''
Created on 07-05-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import threading
from qopml.interpreter.model.parser import ParserException
from qopml.interpreter.model.store import QoPMLModelStore
from qopml.interpreter.model import HostProcess, name_indexes, original_name,\
    HostSubprocess
from qopml.interpreter.simulator import Simulator, EnvironmentDefinitionException,\
    expression, state, equation, metrics, communication, scheduler

class VersionThread(threading.Thread):
    """
    One thread for one version
    """
    
    def __init__(self, simulator, *args, **kwargs):
        super(VersionThread, self).__init__(*args, **kwargs)
        self.simulator = simulator
        
    def run(self):
        pass
    
class Builder():
    """
    Builder that builds environment elements
    """
    
    def build_store(self):
        """
        Builds store - keeps all parsed elements from qopml model
        """
        return QoPMLModelStore()
    
    def _build_functions(self, store):
        """
        Validate and build functions
        """
        functions = []
        errors = []
        
        for f in store.functions:
            err = False
            for ef in functions:
                if ef.name == f.name:
                    errors.append("Function %s redeclared" % f.name)
                    err = True
                    break
            if not err:
                functions.append(f)
                
        if len(errors) > 0:
            raise EnvironmentDefinitionException('Functions redeclaration', errors=errors)
        
        return functions
    
    def _build_equations(self, store, functions):
        """
        Validate, build and return simulation equations build from parsed equations.
        """
        validator = equation.Validator()
        validator.validate(store.equations, functions)
        
        equations = []
        for parsed_equation in store.equations:
            equations.append(equation.Equation(parsed_equation.composite, parsed_equation.simple))
        return equations
    
    def _build_hosts(self, store, version, functions, expression_checker):
        """
        Rebuild hosts - create new instances with updated instructions lists according to version.
        """
        
        def update_process_instructions_list(process, run_process): 
            """
            Update processes instruction lists 
            according to "run process" (repetitions) and follower 
            """
            if run_process.all_subprocesses_active:
                return
            
            instructions_list = []
            
            for instruction in process.instructions_list:
                if isinstance(instruction, HostSubprocess):
                    subprocess = instruction
                    if subprocess.name in run_process.active_subprocesses:
                        instructions_list.append(subprocess.clone())
                else:
                    instructions_list.append(instruction.clone())
            
            process.instructions_list = instructions_list
            
        def update_instructions_list(host, run_host):
            """
            Update host and its processes instruction lists 
            according to "run host" (repetitions) 
            """
            
            def find_process(instructions_list, process_name):
                for instr in instructions_list:
                    if not isinstance(instr, HostProcess):
                        continue
                    if instr.process_name == process_name:
                        return instr
                return None
            
            
            processes_numbers = {}
            instructions_list = []
            
            for run_process in run_host.run_processes:
                # Create process prototype
                process_prototype = find_process(host.instructions_list, run_process.process_name).clone()
                # Update prototype instructions list
                update_process_instructions_list(process_prototype, run_process)
                
                # Define initial process number (if needed)
                if run_process.process_name in processes_numbers:
                    processes_numbers[run_process.process_name] = 0
                
                # If process has follower
                if run_process.follower:
                    # Create processr followe prototype
                    process_follower_prototype = \
                        find_process(host.instructions_list, run_process.follower.process_name).clone()
                    # Update follower prototype instructions list
                    update_process_instructions_list(process_follower_prototype, run_process.follower)
                    
                    # Define initial process number for following process (if needed)
                    if run_process.follower.process_name in processes_numbers:
                        processes_numbers[run_process.follower.process_name] = 0
                    
                for i in range(0, run_process.repetitions):
                    
                    # Get process prototype or create new one 
                    if i == 0:
                        process = process_prototype
                    else:
                        process = process_prototype.clone()
                    
                    # Update process index
                    process_number = processes_numbers[run_process.process_name] + i
                    process.add_name_index(process_number)
                    
                    # Do the same fo the follower 
                    if run_process.follower:
                        if i == 0:
                            follower = process_follower_prototype
                        else:
                            follower = process_follower_prototype.clone()
                            
                        # Update follower index
                        follower_number = processes_numbers[run_process.follower.process_name] + i
                        follower.add_name_index(follower_number)
                        
                        process.follower = follower
                        
                    instructions_list.append(process)
            
            host.instructions_list = instructions_list
            
        
        def set_predefined_variables(host, expression_checker):
            """
            Populate predefined values with expressions 
            and save them as variables in host
            """
            for predefined_value in host.predefined_values:
                host.set_variable(predefined_value.variable_name, 
                                  expression_checker.populate_variables(predefined_value.expression, host.variables))
        
        def set_scheduler(host):
            """
            Build and set host's scheduler
            """
            host.set_scheduler(scheduler.create(host.schedule_algorithm))
        
        built_hosts = []
            
        # Hosts numbers dict keeps the last used number of repeated channel for hosts.
        # For example:
        # run A(*){5} { ... } - will create channels ch1.1, ch1.2, ch1.3, ch1.4 and ch1.5
        # run A(ch1,ch2){2} { ... } - will create channels for next numers which are ch1.6, ch2.6 and ch1.7, ch2.7
        hosts_numbers = {} 
        
        for run_host in version.run_hosts:
            
            if run_host.host_name in hosts_numbers:
                hosts_numbers[run_host.host_name] = 0
            
            # Create prototype host for this "run host"
            host_prototype = store.find_host(run_host.host_name).clone()
            # Update its instructions list
            update_instructions_list(host_prototype, version)
            
            
            for i in range(0, run_host.repetitions):
                # Create next clone for next repetitions
                if i > 0:
                    cloned_host = host_prototype.clone()
                    
                # Set the number of host    
                host_number = hosts_numbers[run_host.host_name] + i
                cloned_host.add_name_index(host_number)
                
                # Save predefined values as variables
                set_predefined_variables(cloned_host, expression_checker)
                # Set scheduler
                set_scheduler(cloned_host)
                built_hosts.append(cloned_host)
                
            hosts_numbers[run_host.host_name] += run_host.repetitions 
            
        return built_hosts
    
    def _build_expression_checker(self):
        """
        Build and return expression checker.
        """
        return expression.Checker()
    
    def _build_expression_reducer(self, equations):
        """
        Build and return expression reducer.
        """
        return expression.Reducer(equations)
    
    def _build_channels(self, store, version, built_hosts):
        """
        Validate, build and return simulation channels build from parsed channels.
        Includes channel repetitions.
        """
        
        def find_channel(channels, name):
            """
            Find channel by name.
            """
            for ch in channels:
                if ch.name == name:
                    return ch
            return None
        
        def find_host(hosts, name):
            """
            Find host by name.
            """
            for h in hosts:
                if h.name == name:
                    return h
            return None
        
        def get_or_create_channel(existing_channels, channel_name):
            """
            Get existing channel by name or create new channel.
            """
            # Find repeated channel with indexes by name 
            channel = find_channel(existing_channels, channel_name)
            # If repeated channel with indexes does not exist
            if channel is None:
                # Find first channel (zero indexes) with original name of repeated channel
                channel = find_channel(existing_channels, original_name(channel_name) + '.0.0')
                channel = channel.clone()
                indexes = name_indexes(channel_name)
                if len(indexes) > 0:
                    channel.add_name_index(indexes[0])
                else:
                    channel.add_name_index(0)
                channel.add_name_index(0)
                
                existing_channels.append(channel)
            return channel
        
        built_channels = []
        original_channels = []
        
        for parsed_channel in store.channels:
            channel = communication.Channel(parsed_channel.name)
            channel.add_name_index(0)
            channel.add_name_index(0)
            built_channels.append(channel)
            original_channels.append(channel)
            
        # Hosts numbers dict keeps the last used number of repeated channel for hosts.
        # For example:
        # run A(*){5} { ... } - will create channels ch1.1, ch1.2, ch1.3, ch1.4 and ch1.5
        # run A(ch1,ch2){2} { ... } - will create channels for next numers which are ch1.6, ch2.6 and ch1.7, ch2.7
        hosts_numbers = {} 
        
        for run_host in version.run_hosts:
            host = store.find_host(run_host.host_name)
            # Load all channels names that host can use
            # Firstly it is checked in version, secondly in parsed host
            # List channel_names contains clean channel names (ch1, ch2) 
            channel_names = []
            if run_host.all_channels_active:
                if host.all_channels_active:
                    channel_names += [ c.original_name for c in original_channels ]
                else:
                    channel_names += [ c for c in host.active_channels ]
            else:
                channel_names += [ c for c in run_host.active_channels ]
            # channel_names - clean names of channels that host can use

            if host.name not in hosts_numbers:
                hosts_numbers[host.name] = 0
                
            host_first_number = hosts_numbers[host.name]
            
            # HOST-CHANNELS ASSIGNATION
            # Algorithm:
            # - For each channel name
            #     - Check if channel is repeated
            #     - Get the name of repeated shannel
            #     - If yes:
            #         - Find channel with repeated name with indexes
            #         - If channel with indexes does not exist: 
            #             - Find channel with original name (zero indexes)
            #             - Clone it and add indexes 
            #             - Add new channel to built channels  
            #     - If no 
            
            for channel_name in channel_names:
                
                # Calculate the name of repeated channel (if it is repeated) 
                # with indexes
                repeated_name = ""
                for repeated_channel in run_host.repeated_channels:
                    repeated_channel_basename = original_name(repeated_channel)
                    if channel_name == repeated_channel_basename:
                        indexes = name_indexes(repeated_channel)
                        if len(indexes) > 0:
                            repeated_name = repeated_channel_basename + '.' + str(indexes[0]) + '.0'
                        else:
                            repeated_name += repeated_channel_basename + '.0.0'
                        break
                    
                # If channel is repeated
                if repeated_name != "":
                    
                    channel = get_or_create_channel(built_channels, repeated_name)
                    
                    # Assign channel to hosts created on the base of this "run host"
                    for i in range(0, run_host.repetitions):
                        host_number = host_first_number + i
                        host_name = run_host.host_name + '.' + str(host_number)
                        built_host = find_host(built_hosts, host_name)
                        built_host.connect_with_channel(channel)
                    
                else: # Channel is not repeated
                    
                    # New channel is created for each channel name
                    # starting from the lately used number (hosts_numbers)
                    
                    for i in range(0, run_host.repetitions):
                        host_number = host_first_number + i
                        host_name = run_host.host_name + '.' + str(host_number)
                        
                        new_channel_name = channel_name + '.' + str(host_number) + '.0'
                        channel = get_or_create_channel(built_channels, new_channel_name)
                        
                        built_host = find_host(built_hosts, host_name)
                        built_host.connect_with_channel(channel)
                        
            # PROCESS-CHANNEL ASSIGNATION
            # Update process-channel assignations in each build host 
            # created on the base of this "run host"
            
            for i in range(0, run_host.repetitions):
                # Process numbers dict keeps the last used number of repeated channel for processes.
                # Works the same like hosts_numbers for hosts.
                processes_numbers = {} 
                
                host_number = host_first_number + i
                host_name = run_host.host_name + '.' + str(host_number)
                built_host = find_host(built_hosts, host_name) 
                
                instruction_index = 0
                for run_process in run_host.run_processes:
                    
                    # Find next process om host's instructions list
                    while instruction_index < len(built_host.instructions_list):
                        if isinstance(built_host.instructions_list[instruction_index], HostProcess):
                            break
                        instruction_index += 1
                        
                    # If no process found raise exception
                    if instruction_index >= len(built_host.instructions_list):
                        raise EnvironmentDefinitionException('Process %s not found in host %s' % (run_process.process_name, ))
        
                    if run_process.process_name not in processes_numbers:
                        processes_numbers[run_process.process_name] = 0
                        
                    # Get number of next channel for this process name 
                    process_first_number = processes_numbers[run_process.process_name]
                    
                    # Get process for this "run process"
                    process = built_host.instructions_list[instruction_index]
                    
                    process_channel_names = []
                    # Get channel names uded by process
                    if process.all_channels_active:
                        process_channel_names = channel_names
                    else:
                        for process_channel_name in process.active_channels:
                            process_channel_names.append(process_channel_name)
                            
                    for process_channel_name in process_channel_names:
                
                        # Calculate the name of repeated channel (if it is repeated) 
                        # with indexes
                        process_channel_repeated_name = "" # Name of repeated channel (may be with indexes)
                        for repeated_channel in run_process.repeated_channels:
                            process_channel_repeated_name_basename = original_name(repeated_channel)
                            if process_channel_name == process_channel_repeated_name_basename:
                                process_channel_repeated_name = repeated_channel
                        
                        # If channel is repeated
                        if process_channel_repeated_name != "":
                            repeated_indexes = name_indexes(process_channel_repeated_name)
                            # If repeated channel is the same, that host is connected with (no indexes)
                            if len(repeated_indexes) == 0:
                                channel = host.find_channel(process_channel_repeated_name)
                                # If host does not have channel with this name
                                if  channel is None:
                                    # Generate channel name for this process
                                    ch_name = original_name(process_channel_repeated_name) + '.' +\
                                                str(host_number) + '.' + str(process_first_number)
                                    channel = get_or_create_channel(built_channels, ch_name)
                                    
                            elif len(repeated_indexes) == 1:
                                # Repeated index is the process index in channels (second index)
                                #
                                # Repeated channel has defined numer of channel from channels of current host 
                                # (for different copies of hosts, these are different channels)
                                # For example: Repeated channel name ch1.1 in host A.5 means that all messages
                                # from all copies of process will be sent through channel ch1.x.1 
                                # (where x is the number of channel ch1 in hist A.5 - firstly it would be propably 5)
                                
                                channel = host.find_channel(original_name(process_channel_repeated_name))
                                
                                if channel:
                                    # Host has channel with this original name
                                    # Lets check if its second index (process index) is the same 
                                    # with repeated index
                                    
                                    ch_indexes = channel.indexes
                                    # If channel proces index (2nd) is different from repeated index
                                    if ch_indexes[1] != repeated_indexes[0]:
                                        ch_name = original_name(process_channel_repeated_name) + '.' +\
                                                    str(ch_indexes[0]) + '.' + str(repeated_indexes[0])
                                        channel = get_or_create_channel(built_channels, ch_name)
                                
                                else:
                                    # Channel is not connected with host
                                    # Generate channel name for this process and host
                                    ch_name = original_name(process_channel_repeated_name) + '.' +\
                                                str(host_number) + '.' + str(process_first_number)
                                    channel = get_or_create_channel(built_channels, ch_name)
                                 
                            elif len(repeated_indexes) == 2:
                                    ch_name = process_channel_repeated_name
                                    channel = get_or_create_channel(built_channels, ch_name)
                                    
                            else:
                                raise EnvironmentDefinitionException(
                                        'Invalid repeated channel definition %s in process %s (host %s)'\
                                        % (process_channel_repeated_name, run_process.process_name, host.name))
                            
                            # Connect repeated channel with all repeated processes
                            # Repeated processes are found as list of next instructions in host's instructions list
                            for i in range(0, run_process.repetitions):
                                process = built_host.instructions_list[instruction_index+i]
                                if not isinstance(process, HostProcess):
                                    raise EnvironmentDefinitionException(
                                        'Isntruction nr %d of host %s expected to be process.'\
                                        % (instruction_index+i, host.name))
                                process.connect_with_channel(channel) 
                        
                        else: # Channel is not repeated
                            
                                current_host_channel_index = host_number
                                
                                # Check if host is connected with any channel of this original name
                                channel = host.find_channel(original_name(process_channel_name))
                                if channel:
                                    # Get current host channel index 
                                    # from the second index of found channel indexes
                                    ch_indexes = channel.indexes
                                    current_host_channel_index = ch_indexes[0]
                                    
                                for i in range(0, run_process.repetitions):
                                    # Generate the channel name for all repetitions
                                    process_number = process_first_number + i
                                    
                                    # Search for channel with generated name or create one
                                    ch_name = original_name(process_channel_name) + '.' +\
                                            str(current_host_channel_index) + '.' + str(process_number)
                                    channel = get_or_create_channel(built_channels, ch_name)
                                    
                                    # Connect channel with process  
                                    process = built_host.instructions_list[instruction_index+i]
                                    if not isinstance(process, HostProcess):
                                        raise EnvironmentDefinitionException(
                                            'Isntruction nr %d of host %s expected to be process.'\
                                            % (instruction_index+i, host.name))
                                    process.connect_with_channel(channel)
                    
                    # Update process numbers dict
                    processes_numbers[run_process.process_name] += run_process.repetitions
                    instruction_index += run_process.repetitions
        
            # Update hosts numbers dict
            hosts_numbers[run_host.host_name] += run_host.repetitions
                                
        return built_channels
        
    def _build_metrics_manager(self, store):
        """
        Build and return metrics manager.
        """
        return metrics.Manager()
    
    def _build_context(self, store, version):
        """
        Builds context with initial state.
        """
        functions = self._build_functions(store)
        equations = self._build_equations(store, functions)
        expression_reducer = self._build_expression_reducer(equations)
        expression_checker = self._build_expression_checker()
        hosts = self._build_hosts(store, version)
        channels = self._build_channels(store, version)
        metrics_manager = self._build_metrics_manager(store);

        c = state.Context()
        
        return c
    
    def build_simulator(self, store, version):
        """
        Creates simulator for particular version.
        """
        return Simulator(self._build_context(store, version))
    
    def build_parser(self, store, modules):
        """
        Builder parser that parses model written in QoPML
        and populates the store.
        """
        from qopml.interpreter.model.parser.lex_yacc import LexYaccParser
        from qopml.interpreter.model.parser.lex_yacc.grammar import main,\
                functions, channels, equations, expressions, instructions, versions,\
                hosts, metrics
        
        parser = LexYaccParser()
        parser.set_store(store) \
                .add_extension(main.ParserExtension()) \
                .add_extension(functions.ParserExtension()) \
                .add_extension(channels.ParserExtension()) \
                .add_extension(equations.ParserExtension()) \
                .add_extension(expressions.ParserExtension()) \
                .add_extension(instructions.ParserExtension()) \
                .add_extension(versions.ParserExtension()) \
                .add_extension(hosts.ParserExtension()) \
                .add_extension(metrics.ParserExtension())
                
        for m in modules:
            parser = m.extend_parser(parser)
                
        return parser.build()
    
class Interpreter():
    """
    Interpreter is responsible for parsing the model,
    creating the environment for simulations,
    manipulating selected models.
    """
    
    def __init__(self, builder=None, model_as_text=""):
        self.builder = builder if builder is not None else Builder()
        self.model_as_text = model_as_text
        
        self.store = self.builder.build_store()
        self.threads = []
        
        self.modules = []
        
    def set_qopml_model(self, model_as_text):
        """
        Set qopml model that will be interpreted.
        """
        self.model_as_text = model_as_text
        return self
    
    def register_qopml_module(self, qopml_module):
        """
        Registers new module
        """
        if qopml_module in self._modules:
            raise EnvironmentDefinitionException(u"QoPML Module '%s' is already registered" % unicode(qopml_module))
        self._modules.append(qopml_module)
        return self
        
    def _parse(self):
        """
        Parses the model from model_as_text field and populates the store.
        """
        
        if len(self.model_as_text) == 0:
            raise EnvironmentDefinitionException("QoPML Model not provided")
    
        parser = self.builder.build_parser(self.store, self.modules)
        parser.parse(self.model_as_text)
        
        if len(parser.get_syntax_errors()) > 0:
            raise ParserException('Invalid syntax', syntax_errors=parser.get_syntax_errors())
        
    def run(self):
        self._parse()
        
        for version in self.store.versions:
            simulator = self.builder.build_simulator(version)
            thr = VersionThread(simulator)
            
            thr.run()
        
