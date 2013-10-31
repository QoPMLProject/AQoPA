'''
Created on 30-10-2013

@author: damian
'''

import optparse
import sys
import os

from aqopa import VERSION
from aqopa.bin import console, gui


def gui_command():
    
    app = gui.AqopaApp(False)
    app.MainLoop()

def console_command():
    parser = optparse.OptionParser()
    parser.usage = "%prog [options]"
    parser.add_option("-f", "--model-file", dest="model_file",  metavar="FILE",
                      help="specifies model file")
    parser.add_option("-m", "--metrics-file", dest="metrics_file",  metavar="FILE",
                      help="specifies file with metrics")
    parser.add_option("-c", "--config-file", dest="config_file",  metavar="FILE",
                      help="specifies file with modules configuration")
    parser.add_option("-s", "--states", dest="save_states", action="store_true", default=False,
                      help="save states flow in a file")
    parser.add_option("-p", '--progressbar', dest="show_progressbar", action="store_true", default=False,
                      help="show the progressbar of the simulation")
    parser.add_option("-V", '--version', dest="show_version", action="store_true", default=False,
                      help="show version of AQoPA")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="DEBUG mode")
    
    (options, args) = parser.parse_args()
    
    if options.show_version:
        print "AQoPA (version %s)" % VERSION
        sys.exit(0)
    
    if not options.model_file:
        parser.error("no qopml model file specified")
    if not os.path.exists(options.model_file):
        parser.error("qopml model file '%s' does not exist" % options.model_file)
        
    if not options.metrics_file:
        parser.error("no metrics file specified")
    if not os.path.exists(options.metrics_file):
        parser.error("metrics file '%s' does not exist" % options.metrics_file)
        
    if not options.config_file:
        parser.error("no configuration file specified")
    if not os.path.exists(options.config_file):
        parser.error("configuration file '%s' does not exist" % options.config_file)
    
    
    f = open(options.model_file, 'r')
    qopml_model = f.read()
    f.close()
    f = open(options.metrics_file, 'r')
    qopml_metrics = f.read()
    f.close()
    f = open(options.config_file, 'r')
    qopml_config = f.read()
    f.close()

    console.run(qopml_model, qopml_metrics, qopml_config, 
         save_states=options.save_states, debug=options.debug,
         show_progressbar=options.show_progressbar)
    