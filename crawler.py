#!/usr/bin/python

# This script contains the generic crawler, which will be used to crawl targetted websites.
# By generic, we mean that by specifying:
#
# 1. The FULLY QUALIFIED DOMAIN NAME, henceforth FQDN, like "http://www.bestbuy.com/"
# 2. A list of URLs (probably 10 or more) which will act a training data set for our
#    crawler to perform structural evaluation of pages, so that it can dynamically and
#    download only those pages that are of interest to the user.
# 3. A list of CSS rules, to extract only those parts of the page which are of interest
#    to the user, as expressed by the CSS rules.
#
# we can crawl any website of interest.
#
# Program flow:
#
# 1. Download the 10 sample URLs and generate Discrete Fourier Transform
#    representations based on HTML structure.
# 2. The crawler then starts crawling the web site, performs structural evaluation
#    of the pages at real-time based on sample URL representations and downloads
#    the pages and stores them in a compressed format, with timestamp and URL of
#    the page as its filename.
# 3. Finally, apply the CSS rules, and extract content and log all that info in a
#    a log file
#
# At every step of the job completion, notifications will be sent the system admin group.

# Programmer: Shirshendu Chakrabarti
# Created at: 2011-June-13
# Modified  : 2011-July-08

# Import System module dependencies here.

import os # Provides OS system calls interface.
import sys # Provides general system calls interface
import time # Provides time operations
import random # Provides random number generation
import urllib2 # HTTP client library
import pdb # Debug Module

# CSS Rule engine on the lines of jQuery Javascript library.

import pyquery
from pyquery import PyQuery as pq

# gzip module

import gzip

# Import Internal modules dependencies here.

import KastParsersLib # Custom parsing module with specific parsing functions.
import KastGenericFunctionsLib # Custom module for handy generic functions.

# Global constants

BASELOGDIR = '/kast/log/'
BASELOCKFILEDIR = '/kast/lock/'
BASEFILESTORAGEDIR = '/kast/'
BASEERRORLOGDIR = '/kast/errorlog/'
BASECONTENTDIR = '/kast/content/'

# List of absolute filenames that need to be globally accessible.

lockFile = ''
errorLog = ''
sitename = ''
contentLogFile = ''

# Global list of absolute URLs of a particular website that has to be crawled yet.

unseenUrlList = []

# Global list of absolute URLs of a particular website that has been crawled.

vistedUrlList = []

# This function downloads the pages in a BFS manner.

def crawl(targetWebsite):

  global sitename
  global errorLog
  global unseenUrlList
  global vistedUrlList
  global BASEFILESTORAGEDIR

  # Now start the crawling rountine.

  while (1):

    if unseenUrlList != []:

      # Choose a page randomly

      page = random.choice(unseenUrlList)

      # Fetch the content.

      r = KastParsersLib.fetchURL(page)

      # Clean the content.

      r = KastParsersLib.cleanHtml(r)

      # Write the content to a file, in the designated folder.

      filename = sitename + '-' + round(time.time(), 2)
      f = gzip.open(BASEFILESTORAGEDIR + filename + '.gz', 'wb')
      f.write(r)
      f.close()

      # Convert to DOM and apply the CSS rule engine

      d = pq(r)
      ele_a = d('a')

      # Extract the hyperlinks

      links_a = KastParsersLib.extractHyperlinks(ele_a)

      # Convert to absolute links.

      unseenUrlListTmp = KastParsersLib.convert2AbsoluteHyperlinks(links_a, targetWebsite)

      # Now check how many of these links exist in Visited URL list.

      for link in unseenUrlListTmp:
        if not vistedUrlList.__contains__(link):
          unseenUrlList.append(link)

      # Now append this page processed to visited URLs list.

      visitedUrlList.append(page)

      # Now remove the same link from unseenUrlList.

      unseenUrlList.remove(page)

      # Condition to end the crawl.

      if unseenUrlList == []:
        return

# This function is our classifier, it applies the DFT distance algorithm and
# preserves those html pages which are of interest. It moves the files which
# are not of interest to a folder.

def classify(htmlSeries, sm):

  global BASEFILESTORAGEDIR

  # Make the useless folder page.

  uselessPagesFolder = chkmkFolderStructure(BASEFILESTORAGEDIR + '/useless/')

  # List all the files, in the folder.

  listOfFiles = os.listdir(BASEFILESTORAGEDIR)
  listOfFiles = [BASEFILESTORAGEDIR + p for p in listOfFiles]

  # Now start the loop and process every file

  for l in range(0, len(listOfFiles)):

    # Choose a file randomly.

    page = random.choice(listOfFiles)

    # Extract the content of the file

    c = gzip.open(page, 'rb')
    contents = c.read()
    c.close()

    # Write to a tmp file.

    tmpFilename = '/tmp/' + page.split('/')[-1]
    f = file(tmpFilename, 'w')
    f.write(contents)
    f.close()

    # Generate html series of this file, tphs --> testPageHtmlSeries

    tphsUrl = 'file://' + tmpFilename
    tphs = KastParsersLib.html2TagSignal(tphsUrl)

    # dftDistance scoreboard

    dftDistanceScoreboard = []

    for d in htmlSeries:

      # Now calculate the score and append them to an array.

      dftDistanceScoreboard.append(KastParsersLib.dftDistance(tphs, d))

    # Now calculate average.

    s = KastGenericFunctionsLib.calcAvg(dftDistanceScoreboard)

    # Score is less than mean similarity measure, move it to the useless folder.

    if s < sm:
      os.system(page, uselessPagesFolder)

# This is the function which will extract the content from the pages of interest
# and will log it into a file.

def extractContent(rules):

  global contentLogFile

  # Now obtain a list of all the files from the content folder.

  listOfFiles = os.listdir(BASEFILESTORAGEDIR)
  listOfFiles = [BASEFILESTORAGEDIR + l for l in listOfFiles]

  records = []

  # Now loop through the files and apply the rules

  for f in listOfFiles:

    # Read the gzipped file

    g = gzip.open(f, 'rb')
    c = g.read()
    g.close()

    record = []

    # Now apply the rules serially and extract content.

    for r in rules:

      # Get a jQuery type $ object for this html page.

      d = pq(c)

      # Apply the CSS selector

      ele = d(r)

      # Store the obtained text in an array.

      record.append(ele.text)

    # Now append the record to records.

    records.append(record)

  # Now write all the records to a designated content log file.

  KastGenericFunctionsLib.writeToDisk(contentLogFile, records)

# This function kickstarts our crawler program.

def main(targetWebsite, configFile):

  global unseenUrlList
  global BASELOGDIR
  global BASELOCKFILEDIR
  global BASEFILESTORAGEDIR
  global BASEERRORLOGDIR
  global BASECONTENTDIR
  global contentLogFile

  # Extract website name

  sitename = extractWebSiteName(targetWebsite)

  # First generate the folder structure if its does not exist.

  BASELOGDIR = chkmkFolderStructure(BASELOGDIR)
  BASELOCKFILEDIR = chkmkFolderStructure(BASELOCKFILEDIR)
  BASEFILESTORAGEDIR = chkmkFolderStructure(BASEFILESTORAGEDIR + sitename + '/')
  BASEERRORLOGDIR = chkmkFolderStructure(BASEERRORLOGDIR)
  BASECONTENTDIR = chkmkFolderStructure(BASECONTENTDIR)

  # Now generate the task/target specific filenames.

  lockFile = BASELOCKFILEDIR + sitename + '.lock'
  errorLog = BASEERRORLOGDIR + sitename + '.error'
  contentLogFile = BASECONTENTDIR + sitename + str(round(time.time(), 2))

  # Now check if the lock file exists and proceed with crawling.

  if os.path.exists(lockFile):
    logException(sitename + ' crawl in progress - Exiting - ' + str(time.time()), BASELOGDIR + sitename + 'exit.log')
    sys.exit(-1)

  # Make a lock file.

  lf = f(lockFile, 'w')
  lf.close()

  # Read the config file into a Dictionary/Hash structure.

  targetWebsiteConfigs = KastParsersLib.kastConfigFileParser(configFile)

  if targetWebsiteConfigs == {}:

    logException('Target website configs could not extracted - ' + str(time.time()), errorLog)
    sys.exit(-1)

  # Obtain the list of URLs from the above data structure and generate time domain
  # perfect series representation of html content.

  htmlSeries = [KastParsersLib.html2TagSignal(url) for url in targetWebsiteConfigs['SampleURLS']]

  # Calculate the average similarity measure.

  similarityMeasure = KastParsersLib.calculateThresholdDftDistanceScore(htmlSeries)

  # Populate the unseenUrlList

  unseenUrlList = populateUnseenUrlList(targetWebsite, unseenUrlList)
  if unseenUrlList == []:
    logException('Seed URL List is malformed. Crawl engine is exiting - ' + str(time.time()), errorLog)
    sys.exit(-1)

  # Start crawling

  crawl(targetWebsite, similarityMeasure)

  # Now apply the Page classification algorithm to preserve only the pages of interest.

  classify(htmlSeries)

  # Apply the CSS rules for scrapping content, this will serve as a simple rule engine template.

  contentExtractionRules = [rule for rule in targetWebsiteConfigs['ContentExtractionRules']][0]

  extractContent(contentExtractionRules)

  # Convert the log file into RDF N Triples file

  # Now log all the information to AllegroGraphDB

if __name__ == '__main__':

  # Check arguments being passed. We need 3 arguments:
  #
  # 1. Fully qualified name of the website to be crawled.
  # 2. A .json format file which has the sample list URLs
  #    which act the training dataset for the crawler and
  #    CSS rules, which will extract content from the fetched
  #    pages of interest.

  if len(sys.argv) == 3:
    main(sys.argv[1], sys.argv[2])
  else:
    print ''
    print 'Usage: # <BASE_DIR>/crawler.py <FQDN of website to be crawled> <Absolute filename containing list of URLs and CSS rules>\n'
    print '# /home/shirshendu/kast_collection/crawler.py http://www.bestbuy.com /home/shirshendu/bestbuy.json\n'
    print ''

