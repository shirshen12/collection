#!/usr/bin/python

# This is a non-executable module, which contains all the parsers for the KAST parsers.
# Any parser of content needs to be put in here and needs to be referenced from this
# module.

# Import System Module dependencies.

import urllib2
import lxml
import ast

# This function is a config file to Hash data structure converter

def kastConfigFileParser(configFile):
  
  # Check if the configuartion file exists.

  configFileExistenceFlag = checkConfigFileExistence(config_file)

  if not configFileExistenceFlag:
    return -1
  else:
    
    # Read the config file and convert it into a continuous string.

    f = file(configFile, 'r')
    rawConfigFileContents = f.read()
    configFileContents = rawConfigFileContents.split('\n')
    configFileContents = ''.join(configFileContents)

    # Now attempt a conversion into a hash.

    configFileHash = ast.literal_eval(configFileContents)

    # Check if we have a Hash data structure.

    if type(configFileHash) != 'dict':
      return -1
    else:
      return configFileHash

# This function fetches a URL, reads the HTML string in memory and converts into a 
# Discrete Fourier Transform Representation, DFT.

def html2dft(url):
  pass

    

    
