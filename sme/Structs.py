#!/usr/bin/env python
  
#Lists
categoryList = []
factList = []
caseList = []
saList = []
ruleList = []
erList = []
foList = []
evalList = []

#Operations  
AND = " AND "
OR = " OR "
NEG = " NEG "
IMPLY = " IMPLY "
EQUALS = " EQUALS "
LESSER = " LESSER "
GREATER = " GREATER "
  
#Classes
class Category(object):
    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

class Fact(object):
    def __init__(self, name=None, category=None, description=None, value=None):
        self.name = name
        self.category = category
        self.description = description
        self.value = value
          
class SecurityAttribute(object):
    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description
          
class Rule(object): 
    def __init__(self, elements=[]):
        self.elements = elements #facts + operators
        
          
class EvaluationRule(object):
    def __init__(self, elements=None, influence=None, security_attribute=None):
        self.elements = elements #facts + operators
        self.influence = influence #influence value
        self.security_attribute = security_attribute
          
class FactsOrder(object):
    def __init__(self, elements=[], security_attribute=None):
        self.elements = elements
        self.security_attribute = security_attribute
        
class Case(object):
    def __init__(self, casename=None, facts=None, description=None):
        self.casename = casename
        self.facts = facts
        self.description = description
        
class Evaluation(object):
    def __init__(self, elements=[], description=None, results_name=[], results_value=[]):
        self.elements = elements
        self.description = description
        self.results = results #dictionary - sec_att: value