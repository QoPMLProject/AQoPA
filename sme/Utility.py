#!/usr/bin/env python
  
import Structs
import pickle
import wx
  

#Read from and write to a file
  
def readFile(filename):
    filename = "files\\"+filename
    f = open(filename)
    lines = [line.strip() for line in f]
    f.close()
    return lines

  
#First clears then writes
def writeFile(filename, thelist):
    filename = "files\\"+filename
    f = open(filename, 'w')
    for item in thelist:
        f.write("%s\n" % item)
    f.close()
  
  
#picklingMethods
def saveCategories(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.categoryList, handle)
  
def loadCategories(path):
    with open(path, 'rb') as handle:
        Structs.categoryList = pickle.load(handle) 
        
def saveFacts(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.factList, handle)
  
def loadFacts(path):
    with open(path, 'rb') as handle:
        Structs.factList = pickle.load(handle)
        
def saveSA(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.saList, handle)
  
def loadSA(path):
    with open(path, 'rb') as handle:
        Structs.saList = pickle.load(handle)
        
def saveRules(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.ruleList, handle)
  
def loadRules(path):
    with open(path, 'rb') as handle:
        Structs.ruleList = pickle.load(handle)
        
def saveFOs(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.foList, handle)
  
def loadFOs(path):
    with open(path, 'rb') as handle:
        Structs.foList = pickle.load(handle)
        
def saveERs(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.erList, handle)
  
def loadERs(path):
    with open(path, 'rb') as handle:
        Structs.erList = pickle.load(handle)
  
def saveCases(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.caseList, handle)
  
def loadCases(path):
    with open(path, 'rb') as handle:
        Structs.caseList = pickle.load(handle) 
        
def saveEvaluations(path):
    with open(path, 'wb') as handle:
        pickle.dump(Structs.evalList, handle)
  
def loadEvaluations(path):
    with open(path, 'rb') as handle:
        Structs.evalList = pickle.load(handle) 
        