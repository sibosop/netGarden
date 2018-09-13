#!/usr/bin/env python
import syslog
import os
import sys
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/config")
sys.path.append(home+"/GitProjects/netGarden/utils")
from subprocess import CalledProcessError, check_output
home = os.environ['HOME']
import config
debug=True
micKey="MIC_CARD"
speakerKey="SPEAKER_CARD"

usbMic="USB-Audio - USB PnP Sound Device"

defaultSpeaker = {'search' : "bcm2835 - bcm2835 ALSA", 'name' : "MINI" }

speakerLookup = [ 
  {'search' : "USB-Audio - USB2.0 Device", 'name' : "HONK" }
  ,{'search' : "USB-Audio - USB Audio Device", 'name' : "JLAB" }
]


def getCardNum(line,key):
  rval=""
  if line.find(key) != -1:
    if debug: syslog.syslog("found "+key+":"+line)
    rval = line.split()[0].strip()
  return rval

hwInit = False
hw={}
def setSpeakerInfo(hw):
  if debug: syslog.syslog("set speak info:"+str(hw['Speaker'])+" " + hw['SpeakerBrand'])
  cmdHdr = ["amixer", "-c",hw['Speaker']]
  try:
    cmd = cmdHdr[:]
    output = check_output(cmd)
    lines = output.split("\n");
    for l in lines:
      n = l.find("Limits: Playback") 
      if n != -1:
        vars = l.split()
        hw['min'] = vars[2]
        hw['max'] = vars[4]

  except CalledProcessError as e:
    syslog.syslog(e.output)



def getHw():
  global hwInit
  global hw
  if hwInit is False:
    hw['Mic']="0"
    hw['Speaker']=-1
    cardPath = "/proc/asound/cards"
    with open(cardPath) as f:
      for line in f:
        t = getCardNum(line,usbMic)
        if t != "":
          hw['Mic'] = t
        for s in speakerLookup:
          t = getCardNum(line,s['search'])
          if t != "":
            hw['Speaker'] = t
            hw['SpeakerBrand']= s['name']

    if hw['Speaker'] == -1:
      with open(cardPath) as f:
        for line in f:
          t = getCardNum(line,defaultSpeaker['search'])
          if t != "":
            hw['Speaker'] = t
            hw['SpeakerBrand'] = defaultSpeaker['name']

    #retrieve info about speaker
    setSpeakerInfo(hw)
    hwInit = True
  return hw 
  

def makeRc():
  path = config.specs['utilsDir']+"/asoundrc.template"
  rcPath = home+"/.asoundrc"
  try:
    rc = open(rcPath,"w")
    hw = getHw()
    with open(path) as f:
      for line in f:
        if line.find(micKey) != -1:
          line = line.replace(micKey,hw['Mic'])
        elif line.find(speakerKey) != -1:
          line = line.replace(speakerKey,hw['Speaker'])
        if debug: syslog.syslog("writing line:"+line);
        rc.write(line)
  except Exception, e:
    syslog.syslog("player error: "+repr(e))

# amixer -c 2 cset numid=3,name='PCM Playback Volume' 100
def setVolume(vol):
  if int(vol) >= 100 :
    vol = "100"
  hw=getHw()
  syslog.syslog("max volume:"+hw['max'])
  volRat = int(hw['max'])/100.0
  setVol = float(vol) * volRat
  setVol = int(round(setVol))
  syslog.syslog("max volume:"
    +hw['max']
    +" Rat:"
    +str(volRat)
    +" Vol:"
    +str(vol)
    +" SetVol:"
    +str(setVol)
    )
  cmdHdr = ["amixer", "-c",hw['Speaker']]
  try:
    cmd = cmdHdr[:]
    cmd.append("controls")
    output = check_output(cmd)
    lines = output.split("\n");
    for l in lines:
      if l.find("Volume") != -1:
        vars = l.split(",")
        cmd = cmdHdr[:]
        cmd.append("cset")  
        cmd.append(vars[0]+","+vars[2])
        cmd.append(str(setVol)) 
        if debug: syslog.syslog("vol:"+str(cmd))
        output = check_output(cmd)

  except CalledProcessError as e:
    syslog.syslog(e.output)

def getVolume():
  vol = 666
  hw=getHw()
  syslog.syslog("max volume:"+hw['max'])
  volRat = float(hw['max'])/100.0
  syslog.syslog("max volume:"
    +hw['max']
    +" Rat:"
    +str(volRat)
    )
  cmdHdr = ["amixer", "-c",hw['Speaker'],"cget","numid=3"]
  try:
    cmd = cmdHdr[:]
    output = check_output(cmd)
    lines = output.split("\n");
    for l in lines:
      if l.find(": values=") != -1: 
        var = l.split("=")
        var = var[1].split(",")
        vol=int(round(float(var[0])/volRat))

  except CalledProcessError as e:
    syslog.syslog(e.output)

  return vol

if __name__ == '__main__':
  os.chdir(os.path.dirname(sys.argv[0]))
  config.load()
  makeRc()
  #setVolume(sys.argv[1])
  #print getVolume()

