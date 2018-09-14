#!/usr/bin/env python
import syslog
import os
import sys
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden/cli")
from subprocess import CalledProcessError, check_output
home = os.environ['HOME']
sys.path.append(home+"/GitProjects/netGarden")
debug=True

def upgrade():
  try:
    syslog.syslog("DOING UPGRADE")
    os.chdir(config.specs['utilsDir'])
    cmd = ['git','pull','--quiet','origin','master']
    output = check_output(cmd)
    if debug: syslog.syslog(output)
  except Exception, e:
    syslog.syslog("player error: "+repr(e))

if __name__ == '__main__':
  os.chdir(os.path.dirname(sys.argv[0]))
  config.load()
  upgrade()
  #setVolume(sys.argv[1])
