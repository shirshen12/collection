#!/usr/bin/python

# This is a non-executable module, which contains all the parsers for the KAST parsers.
# Any parser of content needs to be put in here and needs to be referenced from this
# module.

# Import System Module dependencies.

import os # OS module to avail os system calls independent code.
import sys # System module to write platform independent code
import time # Time module for time operations.
import random # Random module for random number generation and operations.

# HTTP library

import urllib2
from urllib2 import urlopen

# Extremely fast HTML/XML Parser

import lxml
from lxml import etree

# String/Literal conversion module

import ast

# CSS Rule engine on the lines of jQuery Javascript library.

import pyquery
from pyquery import PyQuery as pq

# String Module for specialized string operations.

import string

# Global User Agent String

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.20 Safari/535.1'

# This is a helper function to clean HTML content, of all the whitespace.

def cleanHtml(c):

  for whitespace_char in string.whitespace:
    if whitespace_char != ' ':
      c = c.split(whitespace_char)
      c = ''.join(c)

  return c

# This function extracts all the hyperlinks out of a clean HTML string.

def extractHyperlinks(listOfHyperlinks):

  extractedHyperlinks = []

  for l in listOfHyperlinks:
    attr = l.items()
    for m in attr:
      if m[0] == 'href':
        extractedHyperlinks.append(m[1])

  return extractedHyperlinks

# This function canonicalizes relative/absolute URLs to absolute URLs

def convert2AbsoluteHyperlinks(listOfHyperlinks, targetWebsiteUrl):

  r2a = []

  for i in listOfHyperlinks:
    if i.startswith('http://'):
      r2a.append(i)
    elif not i.startswith('http://') and i.startswith('/'):
      r2a.append(targetWebsiteUrl + i)
    elif not i.startswith('http://') and not i.startswith('/'):
      r2a.append(targetWebsiteUrl + '/' + i)

  return r2a

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

  try:

    # Hit the target website.

    req = urllib2.Request(targetWebsiteUrl)
    req.add_header('User-Agent', USER_AGENT)
    res = urllib2.urlopen(req)
    r = res.read()
    res.close()

    # Clean and canonicalize the HTML content. Since dynamic generation engines
    # contruct/reconstruct the HTML template, we dont need to use Tidy/Beautiful
    # Soup parser libraries.

    r = cleanHtml(r)

    # Code to extract all the <a> or hyperlink elements from the content.

    # Convert html --> DOM object for extracting hyperlinks

    d = pq(r)
    ele_a = d('a')

    # Extract the hyperlinks

    links_a = extractHyperlinks(ele_a)

    # Convert to absolute links.

    unseenUrlList = convert2AbsoluteHyperlinks(links_a, targetWebsiteUrl)

    return unseenUrlList

  except Exception, err:
    print err
    return []

# This function fetches a URL, reads the HTML string in memory and converts into a
# Discrete Fourier Transform Representation, DFT.

def html2dft(url):
  pass

