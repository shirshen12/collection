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

# numpy module to calculate the dft using the fft representation.

import numpy
from numpy import *
from numpy import fft
from numpy.fft import *

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

  c = c.strip()

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

  convertedTagSet = []

  for i in lt:

    # Check if its a shorthand tag, e.g., <br />

    if not i[1].endswith('/>'):

      # If its not, its a normal tag (start or end) and just append to tag set.

      convertedTagSet.append(i[1])
    elif i[1].endswith('/>'):

      # If it is, then process it such that it is converted from <br /> --> <br></br>

      tbct = i[1].split('/>')
      convertedStartTag = tbct[0].strip() + '>'
      convertedTagSet.append(convertedStartTag)

      # Since start tags can have attributes as well <img src='' />, we need to be careful
      # in converting them, since end tags have no attributes.
      # So, <img src='example.png' /> --> <img src='example.png'></img>

      endTag = tbct[0].split('<')[1].strip()
      endTag = endTag.split(' ')[0]
      convertedEndTag = '</' + endTag + '>'
      convertedTagSet.append(convertedEndTag)

  # Now, again convert the malformed HTML string. This is just to be precise.

  r = ''.join(convertedTagSet) # Get the HTML string
  r = cleanHtml(r) # Clean the HTML string.
  r_tags = getTagSet(r)# Generate tag Set for next stage.

  return r_tags

# This function converts the attributes in tags.

def convertAttributes2Tag(r_tags):

  attrTagList = []

  for t in r_tags:
    if t[1].startswith('</'):
      attrTagList.append(t[1])
    elif t[1].startswith('<!'):
      attrTagList.append(t[1])
    else:
      y = t[1].split(' ')
      for i in y:
        if i.startswith('<'):
          attrTagList.append(i.strip() + '>')
        elif i.endswith('>'):
          tmp = i.split('>')[0].strip()
          if tmp.__contains__('='):
            tmp_tagname = tmp.split('=')[0].strip()
            tmp_start = '<ATTRIB@' + tmp_tagname + '>'
            attrTagList.append(tmp_start)
            tmp_end = '</ATTRIB@' + tmp_tagname + '>'
            attrTagList.append(tmp_end)
        elif i.__contains__('='):
          tmp_tagname = i.split('=')[0].strip()
          tmp_start = '<ATTRIB@' + tmp_tagname + '>'
          attrTagList.append(tmp_start)
          tmp_end = '</ATTRIB@' + tmp_tagname + '>'
          attrTagList.append(tmp_end)

  r = ''.join(attrTagList) # Get the HTML string
  r = cleanHtml(r) # Clean the HTML string.
  r_tags = getTagSet(r)# Generate tag Set for next stage.

  return r_tags

# This function is used to identify start tags, end tags and comment tags.

def tagIdentifier(tl):

  tagMarkedArray = []

  for t in tl:
    if t[1].startswith('</'):
      tagMarkedArray.append((t[0], t[1], 'ele'))
    elif t[1].startswith('<!'):
      tagMarkedArray.append((t[0], t[1], 'elc'))
    else:
      tagMarkedArray.append((t[0], t[1], 'els'))

  return tagMarkedArray

# This function returns the position hash, which is used in tag encoding.

def getTagSetPositionStructure(tt):

  tagHash = {}

  posn = 0

  for i in tt:
    if i[2] == 'elc' or i[2] == 'ele':
      continue
    elif not tagHash.has_key(i[1]):
      posn = posn + 1
      tagHash[i[1]] = posn

  return tagHash

# This function performs the tag encoding of the html series. The encoding is based on
# linear random assignment of numbers, all natural numbers.

def tagEncoder(rt):

  # First obtain a dictionary of tagnames and their positions. This will help in
  # assigning amplitudes as values.

  tnamesHash = getTagSetPositionStructure(rt)

  # Now get the series, an array of numbers.

  tagEncodedHtmlSeries = []

  for i in rt:
    if i[2] == 'elc':
      tagEncodedHtmlSeries.append(0)
    elif i[2] == 'ele':
      tagEncodedHtmlSeries.append(0)
    elif i[2] == 'els':
      tagEncodedHtmlSeries.append(int(tnamesHash[i[1]]))

  return tagEncodedHtmlSeries

# This function deals with html script tags so that html series generation is not done in
# a bad manner.

def sanitizeScriptTags(rt):

  # Collect the tags which have are correct.

  sanitizedTags = []
  insideScriptTagContent = 0

  for i in rt:
    if i[1].startswith('<script') and i[1].endswith('/>'):
      sanitizedTags.append(i[1])
    elif i[1].startswith('<script') and not i[1].endswith('/>'):
      # Skip all the elements in between.
      sanitizedTags.append(i[1])
      insideScriptTagContent = 1
    elif i[1].startswith('</script') and insideScriptTagContent == 1:
      sanitizedTags.append(i[1])
      insideScriptTagContent = 0
    elif insideScriptTagContent == 0:
      sanitizedTags.append(i[1])

  # Now obtain the tagset again.

  r = ''.join(sanitizedTags) # Get the HTML string
  r = cleanHtml(r) # Clean the HTML string.
  r_tags = getTagSet(r)# Generate tag Set for next stage.
  return r_tags

# This function removes all the useless comment tags not required in the tag series.

def removeCommentTags(rt):

  tagSeries = []

  for i in rt:
    if i[2] == 'elc':
      continue
    else:
      tagSeries.append(i)

  return tagSeries

# Get the unique tag set for two documents to be compared.

def getUniqueTagSet(rt1, rt2):

  listOfTags = []

  for i in rt1:
    if i[2] == 'els':
      listOfTags.append(i[1])

  for j in rt2:
    if j[2] == 'els':
      listOfHyperlinks.append(i[1])

  # Now convert them into a set

  setOfTags = list(set(listOfTags))

  return setOfTags

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
def html2TagSignal(url):

  # First fetch the url.

  r = fetchURL(url)

  # Clean the HTML content.

  r = cleanHtml(r)

  # Strip the html page of any content and get a tupleof tags
  # <p>Hi!</p> --> [(1, p)]

  r_tags = getTagSet(r)

  # Deal with <script> tags separately, so that we dont have to deal with malformed
  # html

  r_tags = sanitizeScriptTags(r_tags)

  # Convert all short hand tags which end with < /> to full tag set features
  # <br /> --> <br></br>

  r_tags = convertShortHandTags(r_tags)

  # Convert the attributes also into tags <a href="/"> --> <a>, <ATTRIB@href>,
  # </ATTRIB@href>

  r_tags = convertAttributes2Tag(r_tags)

  # Now process for tag marking, identify start tags, end tags and comment tags.
  # <html> --> els, </html> --> ele, <!-- comment --> --> elc

  r_tags = tagIdentifier(r_tags)

  # Now remove the comment tags, they dont contribute to the html series and distort
  # the score.

  r_tags = removeCommentTags(r_tags)

  return r_tags

# This function calculates the dft distance between two html documents and returns a score
# of similarity.

def dftDistance(rt1, rt2):

  # Calculate the unique tname set for both the documents

  tnames = getUniqueTagSet(rt1, rt2)

  # First we interpolate the signal in time domain and then zero pad for signals of
  # unequal length.

  d1_l = len(d1)
  d2_l = len(d2)

  # Now get the 'M' value, the combined value of the length of both the signals.

  M = 0
  if d1_l == d2_l:
    M = d1_l
  else:
    M = (d1_l + d2_l) - 1

    # Also do zero padding at the same time.

    # Calculate the extent of padding to be done, for both the series.

    fsl = M - d1_l
    ssl = M - d2_l

    # Now pad first series.

    for i in range(0, fsl):
      d1.append(0)

    # Now pad second series.

    for j in range(0, ssl):
      d2.append(0)

  # Now calculate dft for both the series.

  d1_dft = fft(array(d1))
  d2_dft = fft(array(d2))

  # Convert from numpy array object to normal python array

  d1_dft = list(d1_dft)
  d2_dft = list(d2_dft)

  # Scale the dft's by sqrt(M)

  d1_dft = [float(i)/math.sqrt(M) for i in d1_dft]
  d2_dft = [float(j)/math.sqrt(M) for j in d1_dft]


  # Now calculate the energy difference between two html signals.

  e_diff = 0
  for k in range(0, M):
    etemp = (abs(d1_dft[k] - d2_dft[k]))**2
    e_diff = e_diff + etemp

  htmlDistance = math.sqrt(abs(e_diff))

  # Now calculate the similarity measure.

  similarityMeasure = 1/(1 + htmlDistance)

  return similarityMeasure

