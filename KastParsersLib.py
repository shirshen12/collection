#!/usr/bin/python

# This is a non-executable module, which contains all the parsers for the KAST parsers.
# Any parser of content needs to be put in here and needs to be referenced from this
# module.

# Import System Module dependencies.

import os
import urllib2
import lxml
import ast

# This function is a config file to Hash data structure converter

def kastConfigFileParser(configFile):

  # Check if the configuartion file exists.

  if not os.path.exists(config_file):
    return {}
  else:

    # Read the config file and convert it into a continuous string.

    f = file(configFile, 'r')
    rawConfigFileContents = f.read()
    configFileContents = rawConfigFileContents.split('\n')
    configFileContents = ''.join(configFileContents)

    # Now attempt a conversion into a hash.

    configFileHash = ast.literal_eval(configFileContents)

    # Check if we have a Hash data structure.
    h = {}
    if configFileHash.__class__ != h.__class__:
      return {}
    else:
      return configFileHash

# This function populates the first level of URLs that needs to be used by the crawler.

def populateUnseenUrlList(targetWebsiteUrl, unseenUrlList):

  # Hit the target website.

  try:

    # Shirshendu - Begin here.

  except Exception, err:
    print err
    return []

# This function fetches a URL, reads the HTML string in memory and converts into a
# Discrete Fourier Transform Representation, DFT.

def html2dft(url):
  pass

