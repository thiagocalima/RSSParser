#! /usr/bin/python

import sys
import feedparser
import socket
import urllib2
import os
import opml
import string
import hashlib
from time import sleep

class ParsedArticle:
	filePath = None,
	feedTitle = None,
	articleTitle = None,
	articleLink = None

	def __init__(self, filePath, feedTitle, articleTitle, articleLink):
		self.filePath = filePath
		self.feedTitle = feedTitle
		self.articleTitle = articleTitle
		self.articleLink = articleLink


class Feed:
	text = None,
	title = None,
	xmlUrl = None

	def __init__(self, text, title, xmlUrl):
		self.text = text
		self.title = title
		self.xmlUrl = xmlUrl


class OPML:
	f = None,
	feeds = []
	
	def __init__(self, f):
		listx = []
		with open(f, "r") as opmlfile:
			outline = opml.parse(opmlfile)
			for i in range(0, len(outline)):
				feed = Feed(outline[i].text, outline[i].title, outline[i].xmlUrl)
				listx.append(feed)
		
		self.feeds = list(listx)

	def getFeedLen(self):
		return len(self.feeds)

	def getFeedX(self, i):
		return self.feeds[i]

	def getFeedList(self):
		return self.feeds


class Sender:
	filePath = None,
	user = " -u thiagocalima@gmail.com"
	password = " -p aqcetfpxlecwoirw"
	server = " -r smtp.gmail.com"
	port = " --port 587"
	sender = " thiagocalima@gmail.com"
	recipient = " thiagocalima@free.kindle.com"
	
	def __init__(self, filePath):
		self.filePath = filePath
		os.system("calibre-smtp -a '" + self.filePath + ".mobi'" + self.user + self.password + self.server + self.port + self.sender + self.recipient + " ''")


def TrimString(string):
	valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	return ''.join(c for c in string if c in valid_chars)


def ConvertBook(parsedArticles):
	# Parameters chosen accordingly to the Calibre documentation: http://manual.calibre-ebook.com/cli/ebook-convert.html
		# ebook-convert
		# --author-sort
		#--authors
		#--book-producer
		#--comments
		#--cover
		#--pubdate
		#--publisher
		#--series
		#--series-index
		#--title
		#--title-sort

	for article in parsedArticles:
		convertParams = "'" + article.filePath + "' '" + article.filePath + ".mobi'" + " --author-sort '" + TrimString(article.feedTitle) + "' --authors '" + TrimString(article.feedTitle) + "' --book-producer 'Jacques Book Converter powered by Calibre eBook" + "' --comments '" + TrimString(article.articleTitle) + "' --publisher 'Jacques Book Converter powered by Calibre eBook" + "' --series '" + TrimString(article.feedTitle) + "' --series-index '" + TrimString(article.feedTitle) + "' --title '" + TrimString(article.articleTitle) + "' --title-sort '" + TrimString(article.articleTitle) + "' --max-toc-links 0"
		os.system("ebook-convert " + convertParams)

	return parsedArticles


def SendBook(parsedArticles):
	c = 0
	for article in parsedArticles:
		if (c == 4):
			timer.sleep(180)
			c = 0

		sender = Sender(article.filePath)


def ParseRSS(opml):
	parsedArticles = []
	socket.setdefaulttimeout(120)
	header = {
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
				'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
				'Accept-Encoding': 'none',
				'Accept-Language': 'en-US,en;q=0.8',
				'Connection': 'keep-alive'
				}
	opml = OPML(opml)

	for feed in opml.getFeedList():
		articles = feedparser.parse(feed.xmlUrl)
		fileName = ""
		path = "/tmp/RSS/"

		for article in articles.entries:
			try:
				fileName = os.path.join(path,str(int(hashlib.md5(article.id).hexdigest(), 16)))
			except AttributeError, e:
				print ("Failed to get Article ID from feed " + feed.title)
			except IOError, e:
				print ("Failed to find file " + fileName)
			except UnicodeEncodeError, e:
					print ("Unicode error on article " + article.link)

			if ((not os.path.exists(fileName)) and (fileName != "")):
				try:
					request = urllib2.Request(unicode(article.link).encode("utf-8"), headers=header)

					if not(os.path.isfile(fileName)):
						with open(fileName, "wb") as htmlFile:
							response = urllib2.urlopen(request)

							htmlFile.write(response.read())
							htmlFile.close
				except AttributeError, e:
					print ("Failed to get Article Link from feed " + feed.title)
				except urllib2.HTTPError, e:
					print e.fp.read()
					print ("Failed to fetch content from feed " + article.link)
				except UnicodeEncodeError, e:
					print ("Unicode error on article " + article.link)
			elif (os.path.exists(fileName)):
				print ("Post " + article.link + " already exists")

#					parsedArticle = ParsedArticle(fileName, feed.title, article.title, article.link)
#					parsedArticles.append(parsedArticle)

#	return parsedArticles
		
		
def main():
	#SendBook(ConvertBook(ParseRSS(sys.argv[1])))
	opmlFile = sys.argv[1]
	print(ParseRSS(opmlFile))

	#print "The Magic Medicine Worked......................Plam!"


if __name__ == '__main__':
		sys.exit(main())