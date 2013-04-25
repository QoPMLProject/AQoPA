'''
Created on 22-04-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

class LexYaccBuilder():
    
    def build(self, cls, token):
        raise NotImplementedError()
    
class LexYaccBuilderManager():
    
    def __init__(self):
        self.builders = []      # objects that extend builder (instances of LexYaccBuilderExtension)
    
    def add_builder(self, b):
        self.builders.append(b)
        return self
    
    def build(self, cls, token):
        for b in self.builders:
            obj = b.build(cls, token)
            if obj:
                return obj
        return None

def create():
    from grammar import functions, channels
    
    builder = LexYaccBuilderManager()
    builder.add_builder(functions.Builder())
    builder.add_builder(channels.Builder())
    
    return builder

