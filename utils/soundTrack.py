#!/usr/bin/env python
import syslog
import pygame
import sys
import os
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/utils")

import random
import syslog
import time
import threading
import numpy as np

debugSoundTrack=True
eventMin=100
eventMax=10000
backgroundCount=0
eventTimeThresholdIncrement=.1
initialEventTimeThreshold=2.5
eventTimeThreshold=initialEventTimeThreshold
eventTimeMaxThreshold = 50.0
allowBackgroundThreshold=20.0
backgroundThreshold=90.0
backgroundIgnoreCount=8
speedChangeThreshold=20
speedChangeMin = 0.5
speedChangeMax = 2.0
doSpeedX=True

eventMutex=threading.Lock()
eventMaxVol=.7

def speedx(sound, factor):
  rval = None
  try:
    syslog.syslog("speedx factor:"+str(factor))
    sound_array = pygame.sndarray.array(sound)
    """ Multiplies the sound's speed by some `factor` """
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    rval = pygame.sndarray.make_sound(sound_array[ indices.astype(int) ])
  except Exception as e:
    syslog.syslog("speedx:"+str(e))
  return rval

def setup():
  pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
  pygame.init()

def getBusyChannels():
  count = 0
  for i in range(pygame.mixer.get_num_channels()):
    if pygame.mixer.Channel(i).get_busy():
      count +=1
  return count

def isWav(f):
  try:
    ext = f.rindex(".wav")
  except ValueError:
    if debugSoundTrack:
      syslog.syslog(sfile+ ":not wav file")
    return False
  flag = f[ext:]
  if debugSoundTrack:
    syslog.syslog("flag ext = "+flag)
  if flag != ".wav":
    return False
  return True

def makeEventChoice(filenames):
  done = False
  while not done:
    if filenames is None:
      syslog.syslog("eventdir ="+config.specs['eventDir'])
      filenames = next(os.walk( config.specs['eventDir']))[2]
    choice = random.choice(filenames)
    done = isWav(choice)
  return (choice,filenames)


def playSound(sound,l,r):
  eventChan = None
  eventChan=pygame.mixer.find_channel()
  if eventChan is None:
    pygame.mixer.set_num_channels(pygame.mixer.get_num_channels()+1);
    eventChan=pygame.mixer.find_channel()
  syslog.syslog("busy channels:"+str(getBusyChannels()))
  syslog.syslog("l: "+str(l) + " r:"+str(r))
  eventChan.set_volume(l,r)
  eventChan.play(sound)
  eventChan.set_endevent()
  

class playEvent(threading.Thread):
  def run(self):
    global backgroundCount
    global backgroundCount
    global eventTimeThreshold
    global allowBackgroundThreshold
    global backgroundThreshold
    global backgroundIgnoreCount
    global eventTimeThresholdIncrement
    global initialEventTimeThreshold
    global eventTimeMaxThreshold
    global eventMutex
    filenames=None
    syslog.syslog("play event thread")
    while True:
      while True:
        filenames=None
        vars = makeEventChoice(filenames)
        filenames = vars[1]
        choice = config.specs['eventDir']+vars[0]
        syslog.syslog("soundTrack choice:"+choice)
        try:
          sound = pygame.mixer.Sound(file=choice)
          len = sound.get_length()
          syslog.syslog(choice+" len:"+str(len)
                + " allowBackgroundThreshold:"+ str(allowBackgroundThreshold)
                + " eventTimeThreshold:"+str(eventTimeThreshold)
                + " backgroundCount:"+str(backgroundCount))
          if eventTimeThreshold > allowBackgroundThreshold and len > backgroundThreshold:
            if backgroundCount == 0:
              backgroundCount = backgroundIgnoreCount
              syslog.syslog("playing"+choice+" len:"+str(len))
              break
            else:
              syslog.syslog("skipping "+choice+" len:"+str(len))
          elif len < eventTimeThreshold:
            syslog.syslog("playing " + choice + " len:"+str(len)
                  +" threshold:"+str(eventTimeThreshold))
            break
          else:
            syslog.syslog("skipping "+choice+" len:"+str(len)
                  +" threshold:"+str(eventTimeThreshold))

        except Exception as e:
          syslog.syslog("error on Sound file:"+str(e))
      if doSpeedX:
        if sound.get_length() < speedChangeThreshold:
          factor = ((speedChangeMax-speedChangeMin) * random.random()) +speedChangeMin
          nsound = speedx(sound,factor)
          if nsound is not None:
            sound = nsound
      l = random.random() * eventMaxVol
      r = random.random() * eventMaxVol
      playSound(sound,l,r)
      eventMutex.acquire()
      eventTimeThreshold += eventTimeThresholdIncrement
      eventMutex.release()
      if  eventTimeThreshold > eventTimeMaxThreshold :
        eventMutex.acquire()
        eventTimeThreshold = initialEventTimeThreshold
        eventMutex.release()
        syslog.syslog("reseting eventTimeThreshold max:"+str(eventTimeMaxThreshold))

      nt = random.randint(eventMin,eventMax)/1000.0;
      syslog.syslog("next play:"+str(nt))
      time.sleep(nt)
      syslog.syslog("back from sleep")

