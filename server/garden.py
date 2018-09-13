#!/usr/bin/env python
import os
home = os.environ['HOME']
import sys
import syslog
import soundServer
import player
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/utils")
import syslog
import datetime
import time
import gardenTrack
import soundTrack
import gardenSpeak
import config
import argparse
import host
import subprocess

debug = True
numGardenThreads=1
gardenExit = 0

masterFlag = None
def isMaster():
  global masterFlag
  if masterFlag is None:
    masterFlag = False
    ip = subprocess.check_output(["hostname","-I"]).strip()
    for h in config.specs['hosts']:
      if debug: syslog.syslog("host:"+str(h)+" ip:"+ip)
      if ip == h['ip']:
        masterFlag = h['isMaster']
        break
  if debug: syslog.syslog("isMaster:"+str(masterFlag)) 
  return masterFlag 
eventThreads=[]
def startEventThread(t):
  global eventThreads
  eventThreads.append(t)
  eventThreads[-1].setDaemon(True)
  eventThreads[-1].start()

if __name__ == '__main__':
  try:
    config.hasAudio = True
    pname = sys.argv[0]
    syslog.syslog(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    os.environ['DISPLAY']=":0.0"
    os.chdir(os.path.dirname(sys.argv[0]))
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--slp', action='store_true', help='use slp instead of config') 
    parser.add_argument('-d','--debug', action = 'store_true',help='set debug')
    parser.add_argument('-c','--config',nargs=1,type=str,default=[config.defaultSpecPath],help='specify different config file')
    args = parser.parse_args()
    if debug: syslog.syslog("config path"+args.config[0])
    config.load(args.config[0])
  except Exception, e:
    syslog.syslog("config error:"+str(e))
    exit(5)
  im =isMaster()
  sst = soundServer.soundServerThread(8080)
  sst.setDaemon(True)
  sst.start()
  soundTrack.setup()
  gardenTrack.changeNumGardenThreads(numGardenThreads)
  speakThread = gardenSpeak.gardenSpeakThread()
  speakThread.setDaemon(True)
  speakThread.start()
  if im:
    syslog.syslog("starting player")
    pt = player.playerThread()
    pt.setDaemon(True)
    pt.start()
  while gardenExit == 0:
    try:
      time.sleep(5)
    except KeyboardInterrupt:
      syslog.syslog(pname+": keyboard interrupt")
      gardenExit = 5
      break
    except Exception as e:
      syslog.syslog(pname+":"+str(e))
      break

  syslog.syslog(pname+" exiting")
  exit(gardenExit)

