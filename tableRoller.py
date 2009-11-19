#!/usr/bin/python

import re
import os
import sys
import glob
import random

DEBUG=False
#DEBUG=True

aliasRE = re.compile('^\s*alias\s+(.*)$')

strRE = re.compile('^"([^"]*)"$')
chanceRE = re.compile('^([0-9]+)\s*%\s*(.*)$')
dieRE = re.compile('^([0-9]*)\s*d\s*([0-9]+)$')
multRE = re.compile('^(.*?)\s*\*\s*(.*)$')
plusRE = re.compile('^(.*?)\s*\+\s*(.*)$')
numRE = re.compile('^([0-9]*)$')
tableSelectRE = re.compile('^\[\s*(.*?)\s*\]$')
rangeRE = re.compile('^([0-9]*)\s*->\s*([0-9]+)$')
tableNameRE = re.compile('^(.*?)\s*\(\s*(.*)\s*\)$')
altStrRE = re.compile('^[A-Za-ce-z]')
evalRE = re.compile('^(.*){\s*([^}]+?)\s*}(.*)$')
listRE = re.compile('^(.*)&(.*)$')

headerRE = re.compile("^\s*\**\s*(.*?)\s*\**\s*$")

def die(sides):
  return random.randint(1, sides)

def expressionObject(objStr):
  objStr = objStr.strip()
  m = evalRE.match(objStr)
  if( m ): return expressionObject(m.group(1) + str(expressionObject(m.group(2)).resolve()) + m.group(3))

  m = strRE.match(objStr)
  if( m ): return ConstExpr(m.group(1))

  m = altStrRE.match(objStr)
  if( m ): return ConstExpr(objStr)

  if( objStr == '-' ) : return ConstExpr(None)

  if( objStr.strip() == '' ) : return ConstExpr('')
  
  m = numRE.match(objStr)
  if( m ): return ConstExpr(int(m.group(1)))
  
  m = listRE.match(objStr)
  if( m ): return ListExpr([expressionObject(m.group(1)), expressionObject(m.group(2))])
  
  m = chanceRE.match(objStr)
  if( m ): return ChanceExpr(m.group(1), expressionObject(m.group(2)))

  m = dieRE.match(objStr)
  if( m ): return DieRollExpr(m.group(1), m.group(2))

  m = plusRE.match(objStr)
  if( m ): return expressionObject(m.group(1)).plus(expressionObject(m.group(2)))

  m = multRE.match(objStr)
  if( m ): return expressionObject(m.group(1)).mult(expressionObject(m.group(2)))

  m = tableSelectRE.match(objStr)
  if( m ): return TableSelectExpr(m.group(1))

  m = rangeRE.match(objStr)
  if( m ): return RangeExpr(m.group(1), m.group(2))

  raise Exception("Could not understand expression: " + repr(objStr))

class Expr:
  def __init__(self):
    pass

  def resolve(self):
    return None

  def plus(self, rhs):
    return PlusExpr(self, rhs)

  def mult(self, rhs):
    return MultiplyExpr(self, rhs)

  def match(self, objStr):
    return self.resolve() == objStr

class ListExpr(Expr):
  def __init__(self, exprList):
    self.exprList = exprList

  def resolve(self):
    retval = []
    for expr in self.exprList:
      val = expr.resolve()
      if( isinstance(val, list) ):
        retval.extend(val)
      else:
        retval.append(val)
    return retval

class RangeExpr(Expr):
  def __init__(self, minval, maxval):
    if( minval == '' ):
      self.minval = -sys.maxint-1
    else:
      self.minval = int(minval)
    self.maxval = int(maxval)

  def __repr__(self): return self.resolve()

  def resolve(self):
    if( self.minval == -sys.maxint-1 ): return ".." + repr(self.maxval)
    return repr(self.minval) + ".." + repr(self.maxval)

  def match(self, val):
    val = int(val)
    retval = val >= self.minval and val <= self.maxval
    debug("Checking for " + repr(val) + " in range " + str(self.minval) + " - " + str(self.maxval) + ": " + str(retval))
    return retval

class DieRollExpr(Expr):
  def __init__(self, numDice, dieSides):
    if( numDice == None or numDice == ''): numDice = 1
    self.numDice = numDice
    self.dieSides = dieSides

  def resolve(self):
    tot = 0
    for i in range(int(self.numDice)):
      tot = tot + die(int(self.dieSides))
    return tot

class ChanceExpr(Expr):
  def __init__(self, chance, expr):
    self.chance = int(chance)
    self.expr = expr

  def resolve(self):
    roll = die(100)
    if( roll <= self.chance ):
      debug("Chance " + repr(self.chance) + " passed with " + repr(roll))
      return self.expr.resolve()
    debug("Chance " + repr(self.chance) + " failed with " + repr(roll))
    return None

class ConstExpr(Expr):
  def __init__(self, val):
    self.val = val

  def resolve(self):
    return self.val

  def __repr__(self):
    return repr(self.val)

class RepeatExpr(Expr):
  def __init__(self, repeatExpr, numTimesExpr):
    self.numTimesExpr = numTimesExpr
    self.repeatExpr = repeatExpr

  def resolve(self):
    retval = []
    for i in range(self.numTimesExpr.resolve()):
      retval.append(self.repeatExpr.resolve())
    return retval

  def mult(self, rhs):
    return RepeatExpr(self, rhs)

class TableSelectExpr(Expr):
  def __init__(self, tableCriterion):
    self.tableCriterion = tableCriterion

  def resolve(self):
    tableCriterion, colName = self.tableCriterion, None
    if( self.tableCriterion.find("/") != -1 ):
      tableCriterion, colName = self.tableCriterion.split("/")
    table, row = Table.getRow(tableCriterion)
    if( colName ): return table.getRowExpr(row, colName).resolve()
    return row

  def mult(self, rhs):
    return RepeatExpr(self, rhs)

class MultiplyExpr(Expr):
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

  def resolve(self):
    debug("lhs: " + repr(self.lhs))
    num = None
    if( isinstance(self.lhs, ConstExpr) and isinstance(self.rhs, ChanceExpr) ):
      num = self.lhs
      other = self.rhs
    if( isinstance(self.rhs, ConstExpr) and isinstance(self.lhs, ChanceExpr) ):
      num = self.rhs
      other = self.lhs

    if( num ):
      retval = []
      for i in range(num.resolve()):
        retval.append(other.resolve())
      return retval
    else:
      return int(self.lhs.resolve()) * int(self.rhs.resolve())

class PlusExpr(Expr):
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs

  def resolve(self):
    debug("lhs: " + repr(self.lhs))
    lhsval = self.lhs.resolve()

    if( isinstance(lhsval, basestring) ): return lhsval + str(self.rhs.resolve())
    if( isinstance(lhsval, Row) ): return str(lhsval) + str(self.rhs.resolve())
    return int(lhsval) + int(self.rhs.resolve())

class Row:
  def __init__(self, table, cols):
    self.cols = cols
    self.table = table

  def __repr__(self):
    retval = "["
    join = ""
    for hdr in self.table.headers:
      if( not hdr in self.table.invisibleHeaders ):
        debug("header idx:" + str(self.table.headerIdx[hdr]))
        debug("col expr:" + str(self.cols[self.table.headerIdx[hdr]]))
        retval += join + hdr + ": " + str(self.cols[self.table.headerIdx[hdr]].resolve())
        join = "/"
    return retval + "]"

def debug(msg):
  if DEBUG: print msg

class Table:
  tables = {}

  def __init__(self):
    self.rows = []
    self.invisibleHeaders = []

  def __setattr__(self, attr, value):
    if attr == 'name':
      m = tableNameRE.match(value)
      if( m ):
        value = m.group(1)
        self.defaultCriteria = m.group(2)
        debug("Creating table " + repr(value) + " default criterion " + self.defaultCriteria) 
      debug("Creating table " + repr(value)) 
      self.tables[value] = self
    elif attr == 'headers':
      headers = []
      self.headerIdx = {}
      idx = 0
      for hdr in value:
        m = headerRE.match(hdr)
        #headers with no '*' are not displayed in row display
        if( hdr.find("*") == -1 ): self.invisibleHeaders.append(m.group(1))
        hdr = m.group(1)

        headers.append(hdr)
        self.headerIdx[hdr] = idx
        idx = idx + 1

        debug(hdr + ": " + repr(idx))
      value = headers
    self.__dict__[attr] = value

  def getRowExpr(self, row, headerName):
    if( not headerName in self.headerIdx ):
      raise Exception("No such column " + str(headerName) + " in " + str(self.name))
    return row.cols[self.headerIdx[headerName]]

  #look up row that has specified value for given column
  def findRow(self, columnCriteria):
    debug(columnCriteria)

    if( columnCriteria == None ): columnCriteria = self.defaultCriteria

    debug(columnCriteria)
    if( columnCriteria.find('=') == -1 ): raise Exception("No = found in criteria: " + columnCriteria)
    colName, colVal = columnCriteria.split('=')
    debug("raw value to find " + repr(colVal))
    colVal = expressionObject(colVal).resolve()
    debug("resolved value to find " + repr(colVal))
    for row in self.rows:
      debug( colName + "=" + repr(self.getRowExpr(row, colName) ))
      if( self.getRowExpr(row, colName).match(colVal) ):
        return row

    print("No row found for " + str(colVal))
    return None

  def addRow(self, cols):
    row = Row(self, cols)
    self.rows.append(row)

  def parseColumn(self, colString):
    return expressionObject(colString)

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
          m = aliasRE.match(line)
          if( m ):
            Table.tables[m.group(1)] = table
          else:
            #read column header row
            #parse header row
            headers = cls.columns(line)

            #parse header data (for now, no parsing)
            table.headers = headers

            mode = 'C'
        elif mode == 'C':
          #read column data row
          #parse column data row
          colStrings = cls.columns(line)

          #parse column data
          cols = []
          for colString in colStrings:
            cols.append(table.parseColumn(colString))

          table.addRow(cols)

          mode = 'C'
    f.close

  @classmethod
  def columns(cls, line):
    debug(line)
    return line.split('|')[1:-1]

  @classmethod
  def get(cls, tableName):
    return cls.tables[tableName]

  @classmethod
  def getRow(cls, columnCriterion):
    if( columnCriterion.find(":") != -1 ):
      tableName, columnCrit = columnCriterion.split(':')
    else:
      tableName = columnCriterion
      columnCrit = None

    table = Table.get(tableName)
    row = table.findRow(columnCrit)

    return table, row


#print out values for all columns
def main(args):
  printColumns(args[1:], args[0])

def printColumns(tableFileNames, columnCriterion):
  for fileName in tableFileNames:
    if( os.path.isdir(fileName) ):
      dirFileNames = glob.glob(fileName+"/*.txt")
      for dirFileName in dirFileNames:
        if( os.path.isfile(dirFileName) ):
          Table.parseFile(dirFileName)
    else:
      Table.parseFile(fileName)
  table, row = Table.getRow(columnCriterion)
  for hdr in table.headers:
    val = table.getRowExpr(row, hdr).resolve()
    if( isinstance(val, list) ):
      hdrPrinted = False
      for valElem in val:
        if( not valElem is None ):
          if( not hdrPrinted ):
            hdrPrinted = True
            print(hdr)
          print("  " + repr(valElem) + "\n")
    else:
      if( not val is None ): print hdr + ": " + repr(val)

if __name__=='__main__':
    main(sys.argv[1:])
