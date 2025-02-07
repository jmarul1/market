#!/usr/bin/env python2.7
##############################################################################
# Intel Top Secret                                                           #
##############################################################################
# Copyright (C) 2013, Intel Corporation.  All rights reserved.               #
#                                                                            #
# This is the property of Intel Corporation and may only be utilized         #
# pursuant to a written Restricted Use Nondisclosure Agreement               #
# with Intel Corporation.  It may not be used, reproduced, or                #
# disclosed to others except in accordance with the terms and                #
# conditions of such agreement.                                              #
#                                                                            #
# All products, processes, computer systems, dates, and figures              #
# specified are preliminary based on current expectations, and are           #
# subject to change without notice.                                          #
##############################################################################
# Author:
#   Mauricio Marulanda
# Description:
#   Type >> calculateQLSp.py -h 
##############################################################################

def plotData(xArray,plotArgs,mode,figName):
  import plotUtils, pylab as pl
  if 'losses' in plotArgs.keys():
    [plotArgs.update({ii[0]:ii[1]}) for ii in plotArgs['losses'].items()]; del plotArgs['losses']
  modelList = [mode] if mode else ['diff','se']; 
  markerList = dict(se='-b',diff='-k')  
  [Figs,Layouts] = plotUtils.layoutPlt(len(plotArgs)); 
  for ii,iiKey in enumerate(plotArgs):
    iiAx = Layouts[ii]; iiAx.hold(True)
    if iiKey in ['L','Q','R']: 
      for qq in modelList:
        iiAx.plot(xArray,plotArgs[iiKey][qq],markerList[qq],label=iiKey+qq)
      iiAx.set_ylim(0,iiAx.get_ylim()[1]);      iiAx.legend(loc='best')
    else: 
      iiAx.plot(xArray,plotArgs[iiKey])      
    iiAx.set_ylabel(plotUtils.getPltKeys(iiKey)[1]);
    iiAx.set_xlabel('Frequency(GHz)');   
    iiAx.hold(False)
  for iiFig in Figs: iiFig.tight_layout(); iiFig.canvas.set_window_title(figName)

  pl.show()

##############################################################################
# Argument Parsing
##############################################################################
import argparse, os
argparser = argparse.ArgumentParser(description='This program calculates the inductances, quality factors, transfer losses of an inductor sparameter file.')
argparser.add_argument(dest='spFiles', nargs='+', help='sparameter file(s)')
argparser.add_argument('-csv', dest='csvFile', action='store_true', help='store results in a csv file: "spfile"_QL.csv')
argparser.add_argument('-plot', dest='plotme', nargs='*', choices=['Q','L','R','losses','all'], help='displays a plot picture for the sparameter.')
argparser.add_argument('-mode', dest='mode', choices=['diff','se'], help='specify to limit calculation to only single ended or differential')
args = argparser.parse_args()
##############################################################################
# Main Begins
##############################################################################
import sys, re, math
sys.path.append('/p/fdk/gwa/jmarulan/environment/myPython/lib/python')
import sparameter as sp

## run for each sparameter specified 
for iiSpFile in args.spFiles:

## Get real path of the file and decide for how many ports
  if os.path.exists(iiSpFile) and re.search(r'\.s\d+p$',os.path.splitext(iiSpFile)[1],flags=re.I):
    spFile = os.path.realpath(iiSpFile); spFileName = os.path.splitext(os.path.basename(spFile))[0]
    sparam = sp.read(spFile)
  else: print('Sparameter file '+iiSpFile+' either does not exists or is not an sparameter file'); continue

## Get the differential and single ended and losses
  Q=dict(diff=[],se=[]); L=dict(diff=[],se=[]); R=dict(diff=[],se=[])
  Q['diff'],L['diff'],Q['se'],L['se'],R['diff'],R['se'] = sparam.getQLR()
  if sparam.portNum != 1: losses = sparam.getTransferFns() #exclude 1 port sparameter
  else: losses = None
# decide what to print based on the inputs, diff or se or both
  if sparam.portNum == 1: #if one port
    results = 'Freq(GHz),Qse,Lse(nH),Rse(Ohms)\n'
    for ii in range(len(sparam.freq)): results += ','.join([str(sparam.freq[ii]),str(Q['se'][ii]),str(L['se'][ii]),str(R['se'][ii])]) + '\n'   
  elif args.mode: #if single or diff specified
    mode = args.mode
    results = 'Freq(GHz),Qdiff,Ldiff(nH),Rdiff(Ohms),Insertion Loss(db),In Return Loss(db),Out Return Loss(db),Insertion Phase(rad)\n' if args.mode == 'diff' else 'Freq(GHz),Qse,Lse(nH),Insertion Loss(db), In Return Loss(db), Out Return Loss(db), Insertion Phase(rad)\n'
    for ii in range(len(sparam.freq)):
      results += ','.join([str(sparam.freq[ii]),str(Q[mode][ii]),str(L[mode][ii]),str(R[mode][ii])])
      results += ',' + ','.join([str(losses['insertion'][ii]),str(losses['inReturn'][ii]),str(losses['outReturn'][ii]),str(losses['insertionPh'][ii])]) + '\n' 
  else:
    results = 'Freq(GHz),Qdiff,Ldiff(nH),Qse,Lse(nH),Rdiff(Ohms),Rse(Ohms),Insertion Loss(db),In Return Loss(db),Out Return Loss(db),Insertion Phase(rad)\n'
    for ii in range(len(sparam.freq)):
      results += ','.join([str(sparam.freq[ii]),str(Q['diff'][ii]),str(L['diff'][ii]),str(Q['se'][ii]),str(L['se'][ii]),str(R['diff'][ii]),str(R['se'][ii])])
      results += ',' + ','.join([str(losses['insertion'][ii]),str(losses['inReturn'][ii]),str(losses['outReturn'][ii]),str(losses['insertionPh'][ii])]) + '\n'

## if csv enable print values in csv file ## else print to the prompt
  if args.csvFile:
    with open(spFileName+'_QL.csv','w') as fout:
      fout.write(results)
  else: print(results)

## show the plot if requested
  if type(args.plotme) == list:
    getPlotArg = lambda ff: {'Q':Q,'L':L,'R':R,'losses':losses}.get(ff)
    if any(args.plotme):
      if args.plotme[0] == 'all': plotArgs = {'Q':Q,'L':L,'R':R,'losses':losses} #if all is asked for
      else:
        plotArgs = {}
        for ii in set(args.plotme): plotArgs.update({ii:getPlotArg(ii)}) 
    else: plotArgs = {'Q':Q,'L':L}
    plotData(sparam.freq,plotArgs,args.mode,spFileName)
exit(0)
