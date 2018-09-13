#!/usr/bin/env python

import os
import time
import syslog
import sys
debug = False


      
textExt = ".lkp"
def getText():
  filenames = next(os.walk( config.specs[imageDir]))[2]
  for f in filenames:
    if debug:
      syslog.syslog( "filename:"+f )
    try:
      ext = f.rindex(textExt)
    except ValueError:
      if debug:
        syslog.syslog( "not lookup text file" )
      continue
    flag = f[ext:]
    if flag == textExt:  
      if debug:
          syslog.syslog("found text file:"+f)
      path =  config.specs['imageDir'] + "/" + f
      lines = open(path).read().split('\n')
      if len(lines) > 1:
        config.mutex.acquire()
        os.unlink(path)
        config.mutex.release()
        return lines
      
  return None

def textChecker():
  count=0
  syslog.syslog("text checker started successfully")
  while True:
    if debug:
      count += 1
      syslog.syslog( "checking for text. count:"+str(count))
    text = getText();
    if text == None:
      if debug:
        syslog.syslog("no text")
    else:
      if debug:
        syslog.syslog("found text"+str(text))
      panel.printText(text)
    time.sleep(5)
    
if __name__ == '__main__':
  textChecker()
