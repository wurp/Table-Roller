#!/usr/bin/python

import re
import os
import sys

#following is just example code
#idRE = re.compile(".*/(000[0-9]*)/?$")
#ids = sorted(map(lambda a: idRE.match(a).group(1), animationDirs + factoryDirs))

class Row:
  def __init__(self):
    pass

class Table:
  tables = {}

  def __init__(self):
    pass

  def __setattr__(self, attr, value):
    self.__dict__[attr] = value
    if attr == 'name':
      self.tables[value] = self

  def findRow(self, columnCriteria):
    pass
    #TODO

  @classmethod
  def parseFile(cls, fileName):
    f = open(fileName)
    fiter = iter(f)

    mode = 'T'
    table = None
    for line in fiter:
      line = line.strip()
      if( not line.startswith("#") and line ):
        if mode == 'T' or (mode == 'C' and line.find('|') == -1):
          #read table name
          table = Table()
          table.name = line

          mode = 'H'
        elif mode == 'H':
          #read column header row
          #parse header row
          headers = cls.columns(line)

          #parse header data
          #TODO

          mode = 'C'
        elif mode == 'C':
          #read column data row
          #parse column data row
          cols = cls.columns(line)
          #parse column data
          #TODO

          mode = 'C'
    f.close

  @classmethod
  def columns(cls, line):
    print line + "\n"
    return line.split('|')

  @classmethod
  def get(cls, tableName):
    return cls.tables[tableName]

#look up row that has specified value for given column
      #TODO
#resolve column value
      #TODO

#print out values for all columns
def main(args):
  printColumns(args[0], args[1])

def printColumns(tableFileName, columnCriterion):
  Table.parseFile(tableFileName)
  tableName, columnCrit = columnCriterion.split(':')

  table = Table.get(tableName)
  row = table.findRow(columnCriterion)
  for col in row.cols:
    print col

if __name__=='__main__':
    main(sys.argv[1:])
