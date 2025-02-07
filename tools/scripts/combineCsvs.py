#!/usr/bin/env python3.7.4
##############################################################################
# Author:
#   Mauricio Marulanda
##############################################################################

##############################################################################
# Argument Parsing
##############################################################################
import argparse, os, sys, re, csv
argparser = argparse.ArgumentParser(description='Combines all CSV with same headers')
argparser.add_argument(dest='csvFiles', nargs='+', help='csv file(s)')
argparser.add_argument('-extract', dest='extract', type=str, help='Extract the value of filename')
args = argparser.parse_args()
##############################################################################
# Main Begins
##############################################################################
sys.path.append(os.path.expanduser('~jmarulan/work_area/utils/environment/myPython/lib/python'))
import csvUtils

## run for each csv specified 
headers = list(csvUtils.dFrame(args.csvFiles[0]).keys())
fLst = []; fileHeader = 'fileName'; exts=[]; vals=[]
for iiCsvFile in args.csvFiles: 
  csvDF = csvUtils.dFrame(iiCsvFile,text=True)
  fName = iiCsvFile.rstrip('_QC.csv'); 
  if args.extract:
    test = re.search(r''+args.extract,fName)    
    if test and test.groups(): 
      dt = test.groupdict(); exts = []; vals = []
      for kk,val in list(dt.items()):
        exts.append(kk); vals.append(val)
  for ll in range(len(csvDF[headers[0]])):
    line = ','.join(vals+[csvDF[hh][ll] for hh in headers]+[fName])
    fLst.append(line)
exts =  ((','.join(exts))+',') if exts else ''
# print them all    
print(exts+(','.join(headers))+','+fileHeader)
print('\n'.join(fLst))
exit()  
