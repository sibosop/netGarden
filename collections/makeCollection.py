#!/usr/bin/env python
import os
home = os.environ['HOME']
import sys
import datetime
import time
import argparse
import glob
import json

defaultWavDir = home+"/sibosopLocal/music/Music20161008/Clips/schlubFull"
defaultOutFile = "tmpCollection"

if __name__ == '__main__':
  pname = sys.argv[0]
  print(pname+" at "+datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
  os.chdir(os.path.dirname(sys.argv[0]))
  parser = argparse.ArgumentParser() 
  parser.add_argument('-d','--debug', action = 'store_true',help='set debug')
  parser.add_argument('-w','--wavs',nargs=1,type=str,default=[defaultWavDir],help='specify different wav directory')
  parser.add_argument('-o','--outFile',nargs=1,type=str,default=[defaultOutFile],help='specify different out file')
  args = parser.parse_args()
  path = args.wavs[0]+"/*.wav"
  print "path:",path
  print "out:",args.outFile[0]
  collFiles = glob.glob(args.wavs[0]+"/*.wav")
  out = {}
  out['sounds'] = []
  for c in collFiles:
    n = c.split("/")[-1]
    print("collection file:"+n)
    e = {}
    e['file'] = n
    out['sounds'].append(e)
  with open(args.outFile[0], 'w') as outfile:
      json.dump(out, outfile)
    