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


# BeautifulSoup module to tidy the HTML.

import BeautifulSoup
from BeautifulSoup import BeautifulSoup

# Debug module

import pdb

# Global User Agent String

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.20 Safari/535.1'

# This is a helper function which fetches url

def fetchURL(url):

  try:

    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    res = urllib2.urlopen(req)
    r = res.read()
    res.close()

    return r

  except Exception, err:

    print str(err)
    return ''

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

# This function strips the content off HTML pages and returns a tag set.

def getTagSet(r):

  # Define a variable for temporary storage of tags encountered.
  # Flag to signify if we are in a tag or not.
  # Finally an array of tuples which signify the position of this tag
  # in the HTML page.

  tmp_tag = ''
  html_array = []
  flag = 0
  count = 0

  for i in r:
    if i == '<':
      flag = 1
      tmp_tag = tmp_tag + i
    elif flag == 1 and i == '>':
      tmp_tag = tmp_tag + i
      count = count + 1
      html_array.append((count, tmp_tag))
      flag = 0
      tmp_tag = ''
    elif flag == 1 and i == '<':
      tmp_tag = ''
      tmp_tag = tmp_tag + i
    elif flag == 1:
      tmp_tag = tmp_tag + i

  return html_array

# Convert short hand tags to full legitimate tags.

def convertShortHandTags(lt):

  # This code converts tags as outlined in the function header.

  pdb.set_trace()

  convertedTagSet = []

  for i in lt:
    tbct = i[1]
    converted_tag = tbct.split('/>')[0].strip() + '>' + '</' + tbct.split('/>')[0].strip().split('<')[1].strip() + '>
    convertedTagSet.append(converted_tag)

  # Now, again convert the malformed HTML string. This is just to be precise.

  r = ''.join(convertedTagSet) # Get the HTML string
  r = BeautifulSoup(r).prettify() # Eliminate malformed HTML string.
  r = cleanHtml(r) # Clean the HTML string.
  r_tags = getTagSet(r)# Generate tag Set for next stage.

  return r_tags

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

    # Hit the target website and fetch the HTML.

    r = fetchURL(targetWebsiteUrl)

    # Clean and canonicalize the HTML content. Since dynamic generation engines
    # contruct/reconstruct the HTML template, we dont need to use Tidy/Beautiful
    # Soup parser libraries.

    r = cleanHtml(r)

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

# This algorithm for web page classification has been adapted from:
# 1. Exploiting Structural Similarity for Effective Web Information Extraction by Flesca et al.,
# 2. Fast detection of XML structural similarity by Flesca et al.,

# The algorithm flow is as follows:
# 1. Fetch the target URL
# 2. Clean the HTML content, strip it of all whitespaces.
# 3. Generate the tag list, maintain the order in which they occur in the HTML page.

# Commit -m "Added comments. Basicallt dont commit Shir"
def html2dft(url):

  # First fetch the url.

  r = fetchURL(url)

  # Clean the HTML content.

  r = cleanHtml(r)

  # Get a well-formed HTML using BeautifulSoup.

  r = BeautifulSoup(r).prettify()

  # Clean the HTML if any whitespace has been introduced.

  r = cleanHtml(r)

  # Strip the html page of any content and get a tupleof tags
  # <p>Hi!</p> --> [(1, p)]

  r_tags = getTagSet(r)

  # Convert all short hand tags which end with < /> to full tag set features
  # <br /> --> <br></br>

  r_tags = convertShortHandTags(r_tags)

