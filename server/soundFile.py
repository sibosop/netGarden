#!/usr/bin/env python
import collections
import csv
import os
import sys
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/collections")
import glob
import random
import syslog
import copy
import threading
import json
import soundServer
import shutil
import config
import copy

debug=True
listMutex=threading.Lock()
maxEvents = 2

fileCollections = None
tunings = None

Gedir = ""
defaultKey = "full.json"
currentCollection = None
eventFile = ""

def getEdir():
  global Gedir
  if Gedir == "":
    Gedir = config.specs['eventDir']
  return Gedir
  
Gcdir = ""
def getCdir():
  global Gcdir
  if Gcdir == "":
    Gcdir = config.specs['collDir']
  return Gcdir

def setMaxEvents(m):
  global maxEvents
  test = int(m)
  if test > 0:
    maxEvents = test
  if debug: syslog.syslog("setMaxEvents maxEvents:"+str(maxEvents))
  status = { 'status' : 'ok' }
  rval = json.dumps(status)
  return rval 

def getCurrentCollection():
  global currentCollection
  if debug: syslog.syslog ("getCurrentCollection")
  getFileCollections()
  return currentCollection

def getFileCollections():
  global fileCollections
  global currentCollection
  global tunings
  if debug: syslog.syslog ("getFileCollections")
  if fileCollections == None:
    fileCollections = {}
    collFiles = glob.glob(getCdir()+"/*.json")
    if debug: syslog.syslog("collFiles:"+str(collFiles))
    for cf in collFiles:
      n = cf.split("/")[-1]
      if debug: syslog.syslog("collection file:"+n)
      try:
        if debug: syslog.syslog("reading:"+cf)
        specs = None
        with open(cf) as f:
          if n == config.specs['tunings']:
            tunings = json.load(f)
          else:
            fileCollections[n] = json.load(f)
          #if debug: syslog.syslog ("n="+str(fileCollections[n]))
      except IOError: 
        syslog.syslog("can't open:"+cf);
    for k in fileCollections.keys():
      if debug: syslog.syslog("collection: %s"%(fileCollections[k]['desc']))
      
  if currentCollection == None:
    if "collection" in config.specs:
      currentCollection = fileCollections[config.specs['collection']]
    else:
      currentCollection = fileCollections[defaultKey]
      
      

def getCollectionList():
  global fileList
  global fileCollections
  if debug: syslog.syslog("getCollectionList")
  getFileCollections()
  collections = []
  for k in sorted(fileCollections.keys()):
    if debug: syslog.syslog("found collection:"+str(k))
    collections.append(k)
  status = { 'status' : 'ok' , 'collections' : collections }
  rval = json.dumps(status)
  #if debug: syslog.syslog("getSoundList():"+rval)
  return rval 

def setCurrentCollection(col):
  global currentCollection
  global filecollections
  getFileCollections()
  syslog.syslog("setting current collection to:"+col);
  status = { 'status' : 'ok' }
  if col in fileCollections.keys():
    currentCollection = fileCollections[col]
  else:
    status['status'] = "fail"
  rval = json.dumps(status)
  if debug: syslog.syslog("setCurrentCollection():"+rval)
  return rval 
  
  
etmps = {}
def makeEtmp(c):
  global etmps
  if str(c) in etmps.keys():
    return etmps[str(c)]
    
  if debug: syslog.syslog("makeEtmp:%d"%(c))
  rval = []
  for i in range(c): 
    r = pow(2,float(i)/float(c))
    if debug: syslog.syslog("makeEtmp r:%f"%(r))
    rval.append(r)
    etmps[str(c)] = rval
  return rval

def getRatios(tunings,name):
  if debug: syslog.syslog("get tuning: %s"%(name))
  rval = None
  if name in tunings:
    rval = []
    spec = tunings[name]
    if 'type' in spec:
      if spec['type'] == "ratio":
        for t in spec['data']:
          rval.append(eval(t))
      elif spec['type'] == "etmp":
        rval = makeEtmp(spec['data'])
  return rval


def getSoundEntry():
  global fileList
  global defaultKey
  global currentCollection
  global fileCollections
  global eventFile
  global tunings
  getFileCollections()
  edir = getEdir()
  cc = currentCollection
  sounds = cc['sounds']
  if debug: syslog.syslog("current collection:"+cc['desc']+" number of sounds:"+str(len(sounds)))
  done = False
  choice = 0
  numChoices = random.randint(1,maxEvents)
  if debug: syslog.syslog("current collection:"+cc['desc']+" number of choices:"+str(numChoices)+" max Events:"+str(maxEvents))
  rval = []
  choiceList=[]
  while len(rval) < numChoices:
    choice = random.randint(0,len(sounds)-1)
    if choice in choiceList:
      continue
    choiceList.append(choice)
    sound = copy.deepcopy(sounds[choice])
    for k in cc.keys():
      if k == 'sounds':
        continue
      if k == 'octaves':
        continue
      if k not in sound:
        if k == 'tuning':
          t = getRatios(tunings,cc['tuning'])
          if t is not None:
            sound[k] = t
        if k == 'octave':
          t = getRatios(cc['octaves'],cc['octave'])
          if t is not None:
            sound[k] = t
        else:
          sound[k] = cc[k]
    for k in sound.keys():
      if k == 'tuning':
        t = getRatios(tunings,sound['tuning'])
        if t is None:
          del sound[k]
        else:
          sound[k] = t
        if k == 'octave':
          t = getRatios(cc['octaves'],sound['octave'])
          if t is None:
            del sound[k]
          else:
            sound[k] = t
    rval.append(sound)
    if debug: syslog.syslog ("len(rval) %d numChoices %d" % (len(rval),numChoices))
  if debug: syslog.syslog("collection rval:"+str(rval))
  return rval
  


if __name__ == '__main__':
  config.load()
  print "currentCollection: %s"%(getCurrentCollection()['desc'])
  for x in range(0,4):
    print "choice %d"%(x)
    entry = getSoundEntry()
    print entry
    print
    print
  setCurrentCollection("joyclouds.json")
  print "currentCollection: %s"%(getCurrentCollection()['desc'])
  for x in range(0,4):
    print "choice %d"%(x)
    entry = getSoundEntry()
    print entry
    print
    print

