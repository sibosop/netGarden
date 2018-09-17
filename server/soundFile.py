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
  if debug: print("setMaxEvents maxEvents:"+str(maxEvents))
  status = { 'status' : 'ok' }
  rval = json.dumps(status)
  return rval 

def getCurrentCollection():
  global currentCollection
  if debug: print ("getCurrentCollection")
  getFileCollections()
  return currentCollection

def getFileCollections():
  global fileCollections
  global currentCollection
  if debug: print ("getFileCollections")
  if fileCollections == None:
    fileCollections = {}
    collFiles = glob.glob(getCdir()+"/*.json")
    if debug: print("collFiles:"+str(collFiles))
    for cf in collFiles:
      n = cf.split("/")[-1]
      if debug: print("collection file:"+n)
      try:
        if debug: print("reading:"+cf)
        specs = None
        with open(cf) as f:
          fileCollections[n] = json.load(f)
          #if debug: print ("n="+str(fileCollections[n]))
      except IOError: 
        print("can't open:"+cf);
    for k in fileCollections.keys():
      if debug: print("collection: %s"%(fileCollections[k]['desc']))
      
  if currentCollection == None:
    currentCollection = fileCollections[defaultKey]

def getCollectionList():
  global fileList
  global fileCollections
  if debug: print("getCollectionList")
  getFileCollections()
  collections = []
  for k in sorted(fileCollections.keys()):
    if debug: print("found collection:"+str(k))
    collections.append(k)
  status = { 'status' : 'ok' , 'collections' : collections }
  rval = json.dumps(status)
  #if debug: print("getSoundList():"+rval)
  return rval 

def setCurrentCollection(col):
  global currentCollection
  global filecollections
  getFileCollections()
  print("setting current collection to:"+col);
  status = { 'status' : 'ok' }
  if col in fileCollections.keys():
    currentCollection = fileCollections[col]
  else:
    status['status'] = "fail"
  rval = json.dumps(status)
  if debug: print("setCurrentCollection():"+rval)
  return rval 

def getRatios(tunings,name):
  if debug: print("get tuning: %s"%(name))
  rval = None
  if name in tunings:
    rval = []
    for t in tunings[name]:
      rval.append(eval(t))
  return rval


def getSoundEntry():
  global fileList
  global defaultKey
  global currentCollection
  global fileCollections
  global eventFile
  getFileCollections()
  edir = getEdir()
  cc = currentCollection
  sounds = cc['sounds']
  if debug: print("current collection:"+cc['desc']+" number of sounds:"+str(len(sounds)))
  done = False
  choice = 0
  numChoices = random.randint(1,maxEvents)
  if debug: print("current collection:"+cc['desc']+" number of choices:"+str(numChoices)+" max Events:"+str(maxEvents))
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
      if k == 'tunings' or k == 'octaves':
        continue
      if k not in sound:
        if k == 'tuning':
          t = getRatios(cc['tunings'],cc['tuning'])
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
        t = getRatios(cc['tunings'],sound['tuning'])
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
    if debug: print ("len(rval) %d numChoices %d" % (len(rval),numChoices))
  if debug: print("collection rval:"+str(rval))
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

