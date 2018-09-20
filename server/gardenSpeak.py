#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/cli")
import soundTrack
import threading
import pygame
import textSpeaker
import syslog
import time
import random
import soundServer
import gardenTrack
import config

currentPhrase={}
phraseMutex=threading.Lock()
debug=True
phraseMinVol = 0.7
phraseMaxVol = 1.0

def setPhraseScatter(flag):
  global phraseScatter
  return soundServer.jsonStatus("depreciated")

def setFirst(f):
  global currentPhrase
  phraseMutex.acquire()
  currentPhrase['first'] = f
  phraseMutex.release()

def clearCurrentPhrase():
  global currentPhrase
  phraseMutex.acquire()
  currentPhrase={}
  phraseMutex.release()


def setCurrentPhrase(args):
  global currentPhrase
  args['first'] = True
  phraseMutex.acquire()
  currentPhrase=args
  phraseMutex.release()
  syslog.syslog("current phrase:"+str(currentPhrase))
  return soundServer.jsonStatus("ok")

def getCurrentPhrase():
  global currentPhrase
  phraseMutex.acquire()
  rval = currentPhrase
  phraseMutex.release()
  return rval


class gardenSpeakThread(threading.Thread):
  def __init__(self):
    super(gardenSpeakThread,self).__init__()
    self.runState = True
    self.runMutex = threading.Lock()
    self.name = "gardenSpeak"

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
    global currentPhrase
    if debug: syslog.syslog(self.name+": starting")
    dir = config.specs['eventDir']
    oldPhrase = ""
    sound = None
    reps = 0
    vol = phraseMaxVol
    phrase = ""
    scatter = False
    lang = ''
    factor = 1.0
    while self.isRunning():
      try:
        phraseArgs = getCurrentPhrase();
        if not phraseArgs:
          #syslog.syslog("waiting for phrase")
          time.sleep(1)
          continue;

        if phraseArgs['first']:
          phrase = phraseArgs['phrase']
          if 'reps' in phraseArgs:
            reps = phraseArgs['reps']
            if reps == 0:
              reps = -1
          else:
            reps = -1
          if 'scatter' in phraseArgs:
            scatter = phraseArgs['scatter']
          else:
            scatter = False

          if 'lang' in phraseArgs:
            lang = phraseArgs['lang']
          else:
            lang = ''

          if 'factor' in phraseArgs:
            factor = phraseArgs['factor']
          else:
            factor = ''

          if 'vol' in phraseArgs:
            vol = int(phraseArgs['vol']) / 100.0 
          phrase = phraseArgs['phrase']
          oldPhrase = ""
          setFirst(False)

        if debug: syslog.syslog("reps:"+str(reps)+" scatter:"+str(scatter))

        if phrase == "":
          clearCurrentPhrase()
          continue

        if phrase == "--":
          clearCurrentPhrase();
          time.sleep(1)
          continue
        phrase = phrase.replace("-"," ")
        if debug: syslog.syslog("PhraseScatter:"+str(scatter))
        if scatter:
          phrase = random.choice(phrase.split())
        if oldPhrase != phrase:
          oldPhrase = phrase
          path = textSpeaker.makeSpeakFile(phrase,lang)
          if path is None:
            syslog.syslog("conversion of "+phrase+" failed if getting group attr error then google is at fault")
            clearCurrentPhrase()
            time.sleep(1)
            continue
          if debug: syslog.syslog(self.name+": playing "+path)
          sound = pygame.mixer.Sound(file=path)
          if debug: syslog.syslog("factor:"+str(factor))
          nsound = soundTrack.speedx(sound,factor)
          if nsound is not None:
                sound = nsound
          os.unlink(path)

        l = vol
        r = l
        if reps != 0:
          soundTrack.playSound(sound,l,r)
          if reps != -1:
            reps -= 1
      except Exception as e:
        syslog.syslog(self.name+": error on "+str(phrase)+":"+str(e))
      nt = random.randint(soundTrack.eventMin,soundTrack.eventMax)/1000.0;
      syslog.syslog(self.name+": next phrase: "+str(nt)+" reps:"+str(reps))
      if reps == 0:
        clearCurrentPhrase()
      else:
        time.sleep(nt)




