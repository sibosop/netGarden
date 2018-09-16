#!/usr/bin/env python
import os
import sys
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/cli")

import threading
import time
import syslog
import subprocess
import glob
import random
import urllib2
import soundFile
import json
import gardenTrack
import host
import config


debug = True
enabled = True

playerMutex=threading.Lock()

def enable(val):
  global enabled
  playerMutex.acquire()
  enabled = val
  playerMutex.release()
  if debug: syslog.syslog("player enabled:"+str(enabled))

def isEnabled():
  global enabled
  playerMutex.acquire()
  rval = enabled
  playerMutex.release()
  return rval

class playerThread(threading.Thread):
  def run(self):
    edir = config.specs['eventDir']
    first = True
    while True:
      try:
        if isEnabled() is False:
          if first:
            first = False
            if debug: syslog.syslog("PLAYER: DISABLING AUTO PLAYER")
          time.sleep(2)
          continue
        first = True
        e = soundFile.getSoundEntry()
        if debug: syslog.syslog("player choosing "+str(e))
        for h in host.getHosts():
          choice = random.choice(e)
          ip = h['ip']
          if not h['hasMusic']:
            if debug: syslog.syslog("skipping :"+ip)
            continue
          if host.isLocalHost(ip):
            if debug: syslog.syslog("sending "+choice+" request to localhost("+ip+")")
            gardenTrack.setCurrentSound(choice)
          else:
            if debug: syslog.syslog("sending "+choice+" request to "+ip)
            try:
              url = "http://"+ip+":8080"
              if debug: syslog.syslog("url:"+url)
              cmd = { 'cmd' : "Sound" ,'args' : choice }
              req = urllib2.Request(url
                      ,json.dumps(cmd),{'Content-Type': 'application/json'})
              timeout = 4
              f = urllib2.urlopen(req,None,timeout)
              test = f.read()
              if debug: syslog.syslog("got response:"+test)
            except Exception,u:
              syslog.syslog("skipping on error on url "+str(url)+":"+str(u))
              continue
        stime = random.randint(15,40)
        if debug: syslog.syslog("next change:"+str(stime))
        time.sleep(stime)
      except Exception, e:
        syslog.syslog("player error: "+repr(e))
