'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class QoPMLModelStore():
    
    def __init__(self):
        """ """
        self.functions   = []
        self.channels    = []
        self.equations   = []
        self.versions    = []
        self.hosts       = []
        self.metrics_configurations  = []
        self.metrics_datas           = []
        self.init_version_number     = []
    
    
    def find_host(self, name):
        for h in self.hosts:
            if h.name == name:
                return h
        return None

