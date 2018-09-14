#!/usr/bin/env python
import BaseHTTPServer
import threading
import time
import syslog
import gardenTrack
import garden
import os
import sys
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/utils")
import asoundConfig
import upgrade
import soundFile
import player
import json
import gardenSpeak
import config
import host
import pygame
debug=True
screen=None
myFont=None
lineLen=None
noLines=6
lineLen = 25
choke = 0
FontFile = "../fonts/Watchword_bold_demo.otf"
FilterDot = True
FontSize = 90

def jsonStatus(s):
  d = {}
  d['status'] = s
  return json.dumps(d)

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_HEAD(s):
    s.send_response(200)
    s.send_header("Content-type", "text/html")
    s.end_headers()

  def log_message(self, format, *args):
    syslog.syslog("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))

  def do_POST(self):
    # Begin the response
    content_len = int(self.headers.getheader('content-length', 0))
    post_body = self.rfile.read(content_len)
    
    if debug: syslog.syslog("Post:"+str(post_body))
    status = self.server.handleGardenCmd(json.loads(post_body))

    self.send_response(200)
    self.end_headers()
    self.wfile.write(status)
    s = json.loads(status)
    #if debug: syslog.syslog("handle cmd:"+str(s));
    if s['status'] == "poweroff":
      os._exit(3)
    if s['status'] == "reboot":
      os._exit(4)
    if s['status'] == "stop":
      os._exit(5)
    if s['status'] == "restart":
      os._exit(6)
    return

class soundServer(BaseHTTPServer.HTTPServer):
  def __init__(self,client,handler):
    BaseHTTPServer.HTTPServer.__init__(self,client,handler)
    self.test = "test var"
    self.cmds = {
      'Probe'     : self.doProbe
      ,'Sound'    : self.doSound
      ,'Volume'   : self.doVolume
      ,'Phrase'   : self.doPhrase
      ,'Show' : self.doShow
      ,'Threads'  : self.doThreads
      ,'Poweroff' : self.doPoweroff
      ,'Reboot'   : self.doReboot
      ,'Upgrade'  : self.doUpgrade
      ,'Auto'     : self.setPlayMode
      ,'Manual'   : self.setPlayMode
      ,'Refresh'  : self.doRefresh
      ,'Rescan'   : self.doRescan
      ,'SoundList': self.doSoundList
      ,'SoundEnable' : self.doSoundEnable
      ,'CollectionList': self.doCollectionList
      ,'Collection' : self.doCollection
      ,'PhraseScatter' : self.doPhraseScatter
      ,'MaxEvents' : self.doMaxEvents
      ,'SoundVol' :  self.doSoundVol
      ,'Play' : self.doPlay
    }

  def displayText(self,cmd):
    global screen
    global myFont
    global lineLen
    global noLines
    text = cmd['phrase']
    color = "FFFF00"
    if 'color' in cmd.keys():
      color = cmd['color']
    if debug: syslog.syslog("color:"+str(color))
    
    if myFont is None:
      pygame.init()
      screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
      if debug: syslog.syslog("screen h:"+str(screen.get_height())
              + " screen w:" + str(screen.get_width()))
      if screen.get_width() == 800:
        lineLen = 16
        noLines = 4
      if debug: syslog.syslog("line len:"+str(lineLen)+ " lines:"+str(noLines))


    if debug: syslog.syslog("displayText setting FontSize:"+str(FontSize))
    myFont = pygame.font.Font(FontFile, FontSize)

    if FilterDot:
      text=text.replace("."," ")
    text=text.strip()
    words=text.split()
    lines = []
    r = ""
    for w in words:
      if (len(w) + len(r)) < lineLen:
        r += w + " "
      else:
        lines.append(r)
        r = w + " "
    lines.append(r)
    lines = lines[0:noLines]
    i = 0
    screen.fill((0,0,0))
    labels = []
    maxWidth = 0
    maxHeight = 0
    for l in lines:
      r = int(color[0:2],16)
      g = int(color[2:4],16)
      b = int(color[4:6],16)
      if debug: syslog.syslog("r:"+str(r)+" g:"+str(g)+" b:"+str(b))
      label = myFont.render(l, 1, (r,g,b))
      w = label.get_width()
      h = label.get_height()
      maxWidth = max(w,maxWidth)
      maxHeight = max(h,maxHeight)
      labels.append(label)
        
    numLabels = len(labels)
    wordRect = pygame.Surface((maxWidth,(maxHeight*numLabels)-4))

    i = 0
    for l in labels:
      h = l.get_height()
      w = l.get_width()
      offset = (wordRect.get_width() - w)/2
      wordRect.blit(l,(offset,i*h))
      i += 1
    sx = (screen.get_width() - wordRect.get_width()) / 2
    sy = (screen.get_height() - wordRect.get_height()) / 2
    screen.blit(wordRect,(sx,sy))
    pygame.display.flip() 

  def doPlay(self,cmd):
    return jsonStatus(gardenTrack.play(cmd))

  def doSoundVol(self,cmd):
    vol = float(cmd['args'][0]) / 100.0
    gardenTrack.setSoundMaxVolume(vol)
    return jsonStatus("ok")

  def doMaxEvents(self,cmd):
    return soundFile.setMaxEvents(cmd['args'][0])

  def doPhraseScatter(self,cmd):
    return gardenSpeak.setPhraseScatter(cmd['args'][0])

  def doSoundEnable(self,cmd):
    return soundFile.setSoundEnable(cmd['args'][0],cmd['args'][1])
  def doSoundList(self,cmd):
    return soundFile.getSoundList();
  def doSound(self,cmd):
    return gardenTrack.setCurrentSound(cmd)

  def doCollectionList(self,cmd):
    return soundFile.getCollectionList()
  def doCollection(self,cmd):
    syslog.syslog(str(cmd))
    return soundFile.setCurrentCollection(cmd['args'][0])


  def doVolume(self,cmd):
    asoundConfig.setVolume(cmd['args'][0])
    return jsonStatus("ok")

  def doShow(self,cmd):
    self.displayText(cmd['args'])
    return jsonStatus("ok")

  def doPhrase(self,cmd):
    return gardenSpeak.setCurrentPhrase(cmd['args'])

  def doThreads(self,cmd):
    return gardenTrack.changeNumGardenThreads(int(cmd['args'][0]))

  def doPoweroff(self,cmd):
    return jsonStatus("poweroff")

  def doReboot(self,cmd):
    return jsonStatus("reboot")

  def doUpgrade(self,cmd):
    upgrade.upgrade()
    syslog.syslog("returned from upgrade")
    return jsonStatus("ok")

  def setPlayMode(self,cmd):
    rval = jsonStatus("not_master")
    if garden.isMaster():
      player.enable(cmd['cmd'] == "Auto")
      rval = jsonStatus("ok")
    return rval

  def doRefresh(self,cmd):
    rval = jsonStatus("not_master")
    if garden.isMaster():
      soundFile.refresh()
      rval = jsonStatus("ok")
    return rval

  def doRescan(self,cmd):
    rval = jsonStatus("not_master")
    if garden.isMaster():
      soundFile.rescan()
      rval = jsonStatus("ok")
    return rval

  def doProbe(self,cmd):
    state = {}
    state['status'] = "ok"
    state['vol'] = asoundConfig.getVolume()
    state['isMaster'] = garden.isMaster()
    state['sound'] = gardenTrack.getCurrentSound()
    phrase = ""
    phraseArg = gardenSpeak.getCurrentPhrase()
    if 'phrase' in phraseArg:
      phrase = phraseArg['phrase']
      phrase = phrase.replace("-"," ");
    state['phrase'] = phrase
    state['phraseScatter'] = False
    state['threads'] = len(gardenTrack.eventThreads)
    state['speaker'] = asoundConfig.getHw()['SpeakerBrand']
    state['auto'] = player.isEnabled() 
    if garden.isMaster():
      state['collection'] = soundFile.getCurrentCollection()
      state['maxEvents'] = soundFile.maxEvents
    else:
      state['collection'] = ""
      state['maxEvents'] = 0
    state['soundMaxVolume'] = gardenTrack.soundMaxVolume

    for k in config.specs.keys():
      if k == 'soundMaxVol':
          continue
      if k == "hosts":
        for h in config.specs[k]:
          if host.isLocalHost(h['ip']):
            for hk in h.keys():
              if hk == 'ip':
                continue
              state[hk] = h[hk]
      else:
        state[k] = config.specs[k]
    rval = json.dumps(state)
    if debug: syslog.syslog("Probe:"+rval)
    return rval


  def handleGardenCmd(self,cmd):
    if debug: syslog.syslog("handling cmd:"+cmd['cmd']);
    return self.cmds[cmd['cmd']](cmd)

class soundServerThread(threading.Thread):
  def __init__(self,port):
    super(soundServerThread,self).__init__()
    self.port = port
    syslog.syslog("sound server:"+str(self.port))
    #self.server_class = BaseHTTPServer.HTTPServer
    self.server_class = soundServer
    self.httpd = self.server_class(('', self.port), MyHandler)

  def run(self):
    self.httpd.serve_forever()

