#!/usr/bin/env python
import sys
import os
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/utils")
import config
import textChecker
import pygame
import sys
import syslog
import time
import os
import wave
import audioop
import re
import host
from gtts import gTTS
from pydub import AudioSegment
debug = True

def convertSampleRate(fname):
  spf = wave.open(fname, 'rb')
  channels = spf.getnchannels()
  width = spf.getsampwidth()
  rate=spf.getframerate()
  signal = spf.readframes(-1)

  #if debug: syslog.syslog("convertSampleRate"
  #  + " rate:"+str(rate)
  #  + " channels:"+str(channels)
  #  + " width:"+str(width)
  #  )

  converted = audioop.ratecv(signal,2,1,rate,44100,None)
  wf = wave.open(fname, 'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(width)
  wf.setframerate(44100)
  wf.writeframes(converted[0])
  wf.close()

def doEspeak(fnameRoot, line):
  syslog.syslog("speak: using espeak");
  fname = fnameRoot + ".wav"
  if debug: syslog.syslog("speak:"+fname)
  os.system("espeak -w "+fname+" '"+line+"'")
  rval = fname
  return rval

def makeSpeakFile(line,language=''):
  rval = None 
  if language == '':
    language  = 'en-us'
  if debug: syslog.syslog("make speak file:"+line+" lang:"+str(language))
  fnameRoot = ""
  try:
    if host.getLocalAttr('hasAudio') is False:
      #if debug: syslog.syslog("speak: no audio");
      return rval
    fnameRoot = "../tmp/" + re.sub('\W+','_',line)
    if config.internetOn() and language != "es":
      if debug: syslog.syslog("speak: internet on using gTTS");
      if debug: syslog.syslog("playText line:"+line)
      fname = fnameRoot + ".mp3"
      #if debug: syslog.syslog("speak:"+fname)
      tts1=gTTS(text=line,lang=language)
      tts1.save(fname)
      #if debug: syslog.syslog("speak:"+fname)
      sound = AudioSegment.from_mp3(fname)
      os.unlink(fname)
      fname = fnameRoot + ".wav"
      #if debug: syslog.syslog("speak:"+fname)
      sound.export(fname, format="wav")
      rval = fname
    else:
      rval = doEspeak(fnameRoot,line)
  except Exception as e:
    syslog.syslog("speak error: "+ str(e))
    rval = doEspeak(fnameRoot,line)
  convertSampleRate(rval)
  return rval


