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
# Modified  : 2011-July-18

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

# Import Semantic and Graph Database Python dependencies.

import rdflib
from rdflib import ConjunctiveGraph
from rdflib import BNode
from rdflib import Namespace
from rdflib import URIRef
from rdflib import Literal

# Some AllegroGraphDB Python dependencies. All import modules copied from
# tutorial_examples.py in AllegroGraphDB server installation.

pythonClientPath = '/home/shirshendu/Personal/collection/franz'
sys.path.append(pythonClientPath)

from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
from franz.miniclient import repository
from franz.openrdf.query.query import QueryLanguage
from franz.openrdf.vocabulary.rdf import RDF
from franz.openrdf.vocabulary.rdfs import RDFS
from franz.openrdf.vocabulary.owl import OWL
from franz.openrdf.vocabulary.xmlschema import XMLSchema
from franz.openrdf.query.dataset import Dataset
from franz.openrdf.rio.rdfformat import RDFFormat
from franz.openrdf.rio.rdfwriter import  NTriplesWriter
from franz.openrdf.rio.rdfxmlwriter import RDFXMLWriter

AG_PORT = "8080"
BASE_URI = 'http://www.kast.com/data'

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

# This function gets returns a connection object with a triple store created
# or renewed.

def getServerConnection(accessMode):

  # For remote linux server, using port forwarding from localhost.
  #server = AllegroGraphServer("localhost", port=AG_PORT, user="test", password="xyzzy")

  # For localhost.
  server = AllegroGraphServer("localhost", port=AG_PORT)

  catalog = server.openCatalog('scratch')
  #print "Available repositories in catalog '%s':  %s" % (catalog.getName(), catalog.listRepositories())

  myRepository = catalog.getRepository("agraph_test", accessMode)
  myRepository.initialize()
  connection = myRepository.getConnection()
  #print "Repository %s is up!  It contains %i statements." % (myRepository.getDatabaseName(), connection.size())
  return connection

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

      filename = KastGenericFunctionsLib.extractWebSiteName(page) + '-' + str(round(time.time(), 2))
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

    # Append the name of the file, because it serves as value for product location

    record.append(f.split('/')[-1])

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

# This function converts a log file full of data into N-Triples format.

def table2RDFNTriplesConverter(logFile, predList):

  global sitename

  # Define a namespace, this is constant for all data in our KB/DB

  KAST = Namespace('http://www.kast.com/data/')

  # Define a ConjunctiveGraph, a normal graph also is sufficient but this
  # kind of graph helps us in trivially merging various kinds of sub components.

  g = ConjunctiveGraph()

  # Now read the log file

  f = file(logFile, 'r')
  records = f.readlines()
  f.close()

  # Now loop through all the records and also through predicate list

  for record in records:

    # Define a guid which is the only unique primary key in our entire database.

    guid = 'http://www.kast.com/data/id/'

    # Now split to obtain the url from the record and hash it to obtain a global unique ID

    guid = guid + KAST[record.split(',')[0]].md5_term_hash()

    for p in range(1, len(predList)):

      # Generate the predicate

      pred = KAST[predList[p]]
      dataItem = record.split(',')[p]
      obj = KAST[dataItem]

      # Now add the triples in the defined Conjunctive Graph.

      g.add((guid, pred, obj))
      g.add((obj, KAST['hasvalue']), rdflib.Literal(dataItem))

  # Now after adding all the triples, serialize it to N-Triples format.

  o = file(BASECONTENTDIR + sitename + '.nt', 'w')
  o.write(g.serialize(format="nt"))
  o.close()

  return BASECONTENTDIR + sitename + '.nt'

# This function stores the data file into the AllegroGraphDB instance running on some
# remote server.

def store2db(datafile):

  # First get a connection object to our server.

  connection = getServerConnection(Repository.RENEW)

  # Now load the data.

  connection.clear()

  # Now load the triples.

  connection.add(datafile, base=BASE_URI, format=RDFFormat.NTRIPLES, contexts=None)

  # Now index all the triples added.

  connection.indexTriples(all=True)

# This function kickstarts our crawler program.

def main(targetWebsite, configFile):

  # Set debub true, turn off in production

  pdb.set_trace()

  global unseenUrlList
  global BASELOGDIR
  global BASELOCKFILEDIR
  global BASEFILESTORAGEDIR
  global BASEERRORLOGDIR
  global BASECONTENTDIR
  global contentLogFile

  # Extract website name

  sitename = KastGenericFunctionsLib.extractWebSiteName(targetWebsite)

  # First generate the folder structure if its does not exist.

  BASELOGDIR = KastGenericFunctionsLib.chkmkFolderStructure(BASELOGDIR)
  BASELOCKFILEDIR = KastGenericFunctionsLib.chkmkFolderStructure(BASELOCKFILEDIR)
  BASEFILESTORAGEDIR = KastGenericFunctionsLib.chkmkFolderStructure(BASEFILESTORAGEDIR + sitename + '/')
  BASEERRORLOGDIR = KastGenericFunctionsLib.chkmkFolderStructure(BASEERRORLOGDIR)
  BASECONTENTDIR = KastGenericFunctionsLib.chkmkFolderStructure(BASECONTENTDIR)

  # Now generate the task/target specific filenames.

  lockFile = BASELOCKFILEDIR + sitename + '.lock'
  errorLog = BASEERRORLOGDIR + sitename + '.error'
  contentLogFile = BASECONTENTDIR + sitename + str(round(time.time(), 2))

  # Now check if the lock file exists and proceed with crawling.

  if os.path.exists(lockFile):
    KastGenericFunctionsLib.logException(sitename + ' crawl in progress - Exiting - ' + str(time.time()), BASELOGDIR + sitename + 'exit.log')
    sys.exit(-1)

  # Make a lock file.

  lf = file(lockFile, 'w')
  lf.close()

  # Read the config file into a Dictionary/Hash structure.

  targetWebsiteConfigs = KastParsersLib.kastConfigFileParser(configFile)

  if targetWebsiteConfigs == {}:

    KastGenericFunctionsLib.logException('Target website configs could not extracted - ' + str(time.time()), errorLog)
    sys.exit(-1)

  # Obtain the list of URLs from the above data structure and generate time domain
  # perfect series representation of html content.

  htmlSeries = [KastParsersLib.html2TagSignal(url) for url in targetWebsiteConfigs['SampleURLS']]

  # Calculate the average similarity measure.

  similarityMeasure = KastParsersLib.calculateThresholdDftDistanceScore(htmlSeries)

  # Populate the unseenUrlList

  unseenUrlList = KastParsersLib.populateUnseenUrlList(targetWebsite, unseenUrlList)
  if unseenUrlList == []:
    logException('Seed URL List is malformed. Crawl engine is exiting - ' + str(time.time()), errorLog)
    sys.exit(-1)

  # Start crawling

  crawl(targetWebsite, similarityMeasure)

  # Now apply the Page classification algorithm to preserve only the pages of interest.

  classify(htmlSeries)

  # Apply the CSS rules for scrapping content, this will serve as a simple rule engine template.

  contentExtractionRules = targetWebsiteConfigs['ContentExtractionRules']

  extractContent(contentExtractionRules)

  # Convert the log file into RDF N Triples file

  predicateList = targetWebsiteConfigs['PredicateList']

  nTriplesFile = table2RDFNTriplesConverter(contentLogFile, predicateList)

  # Now log all the information to AllegroGraphDB

  store2db(nTriplesFile)

# Make this as an executable script.

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
    print '# /home/shirshendu/kast_collection/crawler.py http://www.bestbuy.com /home/shirshendu/Personal/collection/bestbuy.config\n'
    print ''

