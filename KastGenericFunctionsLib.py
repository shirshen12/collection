# This is a generic functions module for all Kast based scripts.
# Mainly collection specific routines will be present, but as the
# project matures, more functions will be added.

# Programmer   :   Shirshendu Chakrabarti
# Created      :   2011-July-08
# Modified     :   2011-July-08

import os
import sys
import time

# This function is a generic log fucntion which records exception events.

def logException(event, fileName):

  # Convert to string, just for safety.

  event = str(event)

  # File operations.

  f = file(fileName, 'a') # Use append mode and absolute filename
  f.write(event + '\n')
  f.close()

# This function check if a particular folder structure exists or not.
# It will make it if it is non-existant, else leave it as it is.

def chkmkFolderStructure(folderStruct):

  if not os.path.exists(folderStruct):
    os.makedirs(folderStruct)

  return folderStruct

# This function extracts the website name from FQDN

def extractWebSiteName(targetWebsite):

  websiteName = targetWebsite.split('http://')[1]

  return websiteName

# This function calculates the average of a mumnerical array.

def calcAvg(aList):

  sumOfListMembers = sum(aList)
  lengthOfList = len(aList)

  return float(sumOfListMembers)/float(lengthOfList)

# This function writes an array of records to the disk.

def writeToDisk(logFile, records):

  for record in records:

    f = file(logFile, 'a')

    record = str(record)

    record = record.split(']')[0]
    record = record.split('[')[1]

    f.write(record + '\n')

    f.close()

