'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class QoPMLModelStore():
    
    functions   = []
    channels    = []
    equations   = []
    versions    = []
    hosts       = []
    metrics_configurations  = []
    metrics_datas           = []
    init_version_number     = []
    
    
    def find_host(self, name):
        for h in self.hosts:
            if h.name == name:
                return h
        return None

