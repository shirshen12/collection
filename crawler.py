#!/usr/bin/python

# This script contains the generic crawler, which will be used to crawl targetted websites.
# By generic, we mean that by specifying:
#
# 1. The FULLY QUALIFIED DOMAIN NAME, henceforth FQDN, like "http://www.bestbuy.com/"
# 2. A list of URLs (probably 10) which will act a training data set for our crawler
#    to perform structural evaluation of pages, so that it can dynamically focus and
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
# 2. The crawler then starts crawling the web site, does structural evaluation
#    of the pages at real-time based on sample URL representations and downloads
#    the pages and stores them in a compressed format, with timestamp and URL of
#    the page as its filename.
# 3. Finally, apply the CSS rules, and extract content and log all that info in a
#    a log file (http://www.bestbuy.com/crawlresults/<date>/<begin_processing_timestamp>)
#
# At every step of the program flow, a mail to indicate the job completion step will be sent
# the system admin group.

# Programmer: Shirshendu Chakrabarti
# Created at: 2011-June-13
# Modified  : 2011-June-14

# Import System module dependencies here.

import os
import sys
import time
import random
import urllib2
import pdb

# Import Internal modules dependencies written by in-house software developers here.

# Custom parsing module with specific parsing functions.

import KastParsersLib

# Handy module with date and time processing functions.

import KastTimeLib

# Global lists of unseen and seen URLs list.

BASE_DIR = '/kast/'
CRAWL_COPIES_LIMIT = 10
unseenUrlList = []
seenUrlList = []
crawlSuccessFlag = []

# This function kickstarts our crawler program.

def main(targetWebsite, configFile):

  # List all global variables so that they can be modified and be thread safe

  # First read the config file into a Dictionary/Hash structure.

  targetWebsiteConfigs = KastParsersLib.kastConfigFileParser(configFile)

  # Obtain the list of URLs from the above data structure and generate DFTs for all of them.

  dftRepresentations = [KastParsersLib.html2dft(url) for url in targetWebsiteConfigs['SampleURLS']]

  # Populate the unseenUrlList

  populateUnseenUrlList(targetWebsite)

  # Start crawling routine, which is multi process routine. So we will first fork 'x' copies of the crawl.

  crawlerCopies = int(targetWebsiteConfigs['CrawlerCopies'])
  child_pids = [os.fork() for i in range(0, crawlerCopies) if crawlerCopies <= CRAWL_COPIES_LIMIT]
  child_pids = [i for i in child_pids if i == 0]

  # Start a crawl process for all succesfull forks. In this

  for copy in range(0, len(child_pids)):

    crawlSuccessFlag.append(crawl(dftRepresentations), BASE_DIR)

  # Apply the CSS rules for scrapping content, this will serve as a simple rule engine template.

  # Convert the log file into RDF N Triples file

  # Now log all the information to AllegroGraphDB


if __name__ == '__main__':

  # Check arguments being passed. We need 3 arguments:
  #
  # 1. Fully qualified name of the website to be crawled.
  # 2. A .json format file which has the sample list URLs
  #    which act the training dataset for the crawler.
  # 3. CSS rules, which will extract content from the downloaded
  #    pages of interest.

  if len(sys.argv) == 3:
    main(sys.argv[1], sys.argv[2])
  else:
    print ''
    print 'Usage: # <BASE_DIR>/crawler.py <FQDN of website to be crawled> <Absolute filename containing list of URLs and CSS rules>\n'
    print '# /home/shirshendu/kast_collection/crawler.py http://www.bestbuy.com /home/shirshendu/bestbuy.json\n'
    print ''

