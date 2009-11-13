#!/usr/bin/python -w

import re
import os
import sys

#following is just example code
#idRE = re.compile(".*/(000[0-9]*)/?$")
#ids = sorted(map(lambda a: idRE.match(a).group(1), animationDirs + factoryDirs))

def parseTableFile(tableFileName):
  f = open(tableFileName)
  fiter = iter(f)
  for line in fiter:
    line = line.strip()
    if( !line.startsWith("#") ):
      #TODO
      #read table name
      #read column header row
      #parse header row
      #parse header data
      #read column data row
      #parse column data row
      #parse column data

#look up row that has specified value for given column
      #TODO
#resolve column value
      #TODO

#print out values for all columns
def main(tableFileName, columnCriterion):
  table = parseTableFile(tableFileName)
  row = table.findRow(columnCriterion)
  for col in row.cols:
    print col

if __name__=='__main__':
    main(sys.argv[1:])
