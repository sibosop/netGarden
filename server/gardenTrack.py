#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/cli")
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/utils")
import sys
import soundTrack
import threading
import pygame
import syslog
import random
import time
import soundServer
import config

debug = False
currentSound = {'file':""}
soundMinVol = 0.1
speedChangeMax = 4.0
speedChangeMin = .25
volLock = threading.Lock()
soundMaxVolume=.4

def play(cmd):
  rval = "ok"
  try:
    path=cmd['args']['path']
    if debug: syslog.syslog("Path Play: playing:"+path);
    sound = pygame.mixer.Sound(file=path)
    l = soundMaxVolume;
    r = l
    soundTrack.playSound(sound,l,r)
  except Exception as e:
    syslog.syslog(Play+": error on "+path+":"+str(e))
    rval = "Fail"
  return "rval"


def setSoundMaxVolume(vol):
  global soundMaxVolume
  syslog.syslog("setting vol to;"+str(vol))
  volLock.acquire()
  soundMaxVolume = vol
  volLock.release()
  

def findSoundFile(file):
  dir = config.specs['eventDir']
  path = dir+"/"+file
  rval = ""
  if os.path.isfile(path):
    rval = path
  return rval

def setCurrentSound(cmd):
  global currentSound
  rval = "fail"
  if debug: syslog.syslog("cmd:" + str(cmd))

  if findSoundFile(cmd['file']) != "":
    if debug: syslog.syslog("mutex")
    soundTrack.eventMutex.acquire()
    currentSound=cmd
    if debug: syslog.syslog("currentSound:" + str(currentSound))
    soundTrack.eventMutex.release()
    rval = "ok"
  return soundServer.jsonStatus(rval)

def getCurrentSound():
  global currentSound
  soundTrack.eventMutex.acquire()
  rval = currentSound['file']
  n = currentSound['file'].rfind(".")
  soundTrack.eventMutex.release()
  return rval[0:n]

def doJpent():
  rval = ((speedChangeMax-speedChangeMin) 
                        * random.random()) + speedChangeMin
  syslog.syslog("doJpent")
  return rval

tunings = {
  'jpent' : [1.0,32.0/27.0,4.0/3.0,3.0/2.0,16.0/9.0]
  ,'bfarabi' : [1.0,9.0/8.0,45.0/32.0,131.0/90.0,3.0/2.0,15.0/8.0,31.0/16.0]
  ,'sheng' : [1.0,8.0/7.0,6.0/5.0,5.0/4.0,3.0/2.0,5.0/3.0]
  ,'joy' : [1.0,9.0/8.0,5.0/4.0,3.0/2.0,5.0/3.0,15.0/8.0]
}

octaves = [0.25,0.5,1.0,2.0,4.0]

def getFactor(path):
  rval = 1.0
  try:
    pos = path.find("__");
    if pos == -1:
      raise NameError
    epos = path.find(".",pos)
    if pos == -1:
      raise NameError

    tuning = path[pos+2:epos]
    syslog.syslog("tuning:"+tuning);
    if tuning not in tunings:
      syslog.syslog("bad tuning:"+tuning)
      raise NameError
    rval = random.choice(tunings[tuning]) * random.choice(octaves)
  except NameError as exp:
    syslog.syslog("default tuning for path:"+path)
    rval = ((speedChangeMax-speedChangeMin) * random.random()) + speedChangeMin
  syslog.syslog("factor:"+str(rval))
  return rval


class gardenTrack(threading.Thread):
  def __init__(self,name):
    super(gardenTrack,self).__init__()
    self.runState = True
    self.name = name
    self.runMutex = threading.Lock()


  def isRunning(self):
    self.runMutex.acquire()
    rval = self.runState
    self.runMutex.release()
    return rval

  def stop(self):
    self.runMutex.acquire()
    self.runState = False
    self.runMutex.release()
    
  def run(self):
    global currentSound
    global soundMaxVolume
    syslog.syslog("Garden Track:"+self.name)
    dir = config.specs['eventDir']
    soundMaxVolume = config.specs['soundMaxVol']
    while self.isRunning():
      path=""
      nt = random.randint(soundTrack.eventMin,soundTrack.eventMax)/1000.0;
      try:
        file=""
        soundTrack.eventMutex.acquire()
        file = currentSound['file']
        soundTrack.eventMutex.release()
        if file == "":
          if debug: syslog.syslog(self.name+": waiting for currentSoundFile");
          time.sleep(2)
          continue
        path = dir+"/"+file
        if debug: syslog.syslog(self.name+": playing:"+path);
        sound = pygame.mixer.Sound(file=path)
	
        factor = getFactor(path);
        nsound = soundTrack.speedx(sound,factor)
        if nsound is not None:
          sound = nsound
        volLock.acquire()
        l = soundMaxVolume;
        volLock.release()
        r = l
        soundTrack.playSound(sound,l,r)
      except Exception as e:
        syslog.syslog(self.name+": error on "+path+":"+str(e))

      if debug: syslog.syslog(self.name+": next play:"+str(nt))
      time.sleep(nt)
      if debug: syslog.syslog(self.name+":back from sleep")
    syslog.syslog("garden thread " + self.name + " exiting")

ecount = 0
eventThreads=[]
def startEventThread():
  if debug: syslog.syslog("startEventThread")
  global eventThreads
  global ecount
  ecount += 1
  t=gardenTrack(str(ecount))
  eventThreads.append(t)
  eventThreads[-1].setDaemon(True)
  eventThreads[-1].start()

def stopEventThread():
  global eventThreads
  if debug: syslog.syslog("stopEventThread")
  if len(eventThreads) != 0:
    t = eventThreads.pop()
    t.stop()
  else:
    syslog.syslog("trying to stop thread when list is empty")



def changeNumGardenThreads(n):
  global eventThreads
  syslog.syslog("changing number of threads from "
                    +str(len(eventThreads))+ " to "+str(n))
  while len(eventThreads) != n:
    if len(eventThreads) < n:
      startEventThread()
    elif len(eventThreads) > n:
      stopEventThread()
  return soundServer.jsonStatus("ok")
