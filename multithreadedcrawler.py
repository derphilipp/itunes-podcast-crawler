from bs4 import BeautifulSoup
import requests
from string import ascii_uppercase
import re 
import urllib.parse as urlparse
import json
import csv 
import sys
import os
import datetime
import threading
import queue

# declaring constants & variables
data_all = []
data_en = []
data_de = []
data_all_2020 = []
errors = {}

ids = []
feeds = {}
afreverse = {}

slink = 'https://podcasts.apple.com/de/genre/podcasts/id26'

sdir = "d:\\crawl_" + str(datetime.date.today()) 
cfgdir = "d:\\crawl_configfiles"

threadpool = 40
allthreads = []
feedqueues = []
queueID = 0
breakcondition = 0

idStack = []
idcountpercall = 10

# Functions and classes

def get_id(url): # extract Apple ID from URL
    parts = urlparse.urlsplit(url) 
    if parts.hostname == 'podcasts.apple.com':
        idstr = parts.path.rpartition('/')[2] # extract 'id123456'
        if idstr.startswith('id'):
            try: return int(idstr[2:])
            except ValueError: pass
        raise ValueError("Invalid url: %r" % (url,))

def savedata(the_data, filename): # well, what the name says
    if len(the_data)>0:
        with open(filename, 'w', newline="") as outfile:
            json.dump(the_data, outfile)

def saveall(savedir):
    print ("saving data_all...")
    savedata(data_all, savedir + '\\data_all.json')
    print ("done.")

    print ("saving data_en...")
    savedata(data_en, savedir + '\\data_en.json')
    print ("done.")
    
    print ("saving data_de...")
    savedata(data_de, savedir + '\\data_de.json')
    print ("done.")
    
    print ("saving data_all_2020...")
    savedata(data_all_2020, savedir + '\\data_all_2020.json')
    print ("done.")

    print ("saving errors...")
    savedata(errors, savedir + '\\errors.json')
    print ("done.")
    
    # flush memory
    data_all.clear()
    data_en.clear()
    data_de.clear()
    data_all_2020.clear()
    errors.clear()

exitflag = 0
class myThread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    def run(self):
        print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Starting " + str(self.threadID))

        for x in feedqueues[self.threadID]:
            theIDlocal = x
            f = feeds[theIDlocal]
            feedurl = f[0]

            primaryGenreName = feeds[theIDlocal][1],
            releaseDate = feeds[theIDlocal][2]

            # now we got the feed, let's download and parse
            try: 
                xmlfeed = requests.get(feedurl, timeout=30)
                xf = BeautifulSoup(xmlfeed.content, 'xml')
                title = xf.channel.title.get_text()

                try:
                    language = xf.channel.language.get_text()
                except:
                    language = "UNKNOWN"

                episodecount = str(len(xf.find_all("item")))
            except:
                errors[theIDlocal] = feedurl
                continue
            
            try:
                description = xf.channel.description.get_text()
            except:
                description = ""

            try:
                wlink = xf.channel.link.get_text()
            except:
                wlink = ""

            try: 
                author = xf.find("itunes:author").get_text()
            except:
                author = ""

            nl = urlparse.urlsplit(feedurl).netloc

            metadata = {
                "title": title,
                "description": description,
                "feedurl": feedurl,
                "itunesGenre": primaryGenreName,
                "itunesID": theIDlocal,
                "episodecount": episodecount,
                "link": wlink,
                "author": author,
                "language": language,
                "feeddomain": ".".join(nl.split('.')[-2:]),
                "feedtld": ".".join(nl.split('.')[-1:]),
                "releaseDate": releaseDate,
                "releaseyear": releaseDate[0:4]
            }

            if 'en-' in language.lower():
                data_en.append(metadata)

            if language.lower() == 'en':
                data_en.append(metadata)

            if 'de-' in language.lower():
                data_de.append(metadata)

            if language.lower() == 'de':
                data_de.append(metadata)

            if '2020' in releaseDate:
                data_all_2020.append(metadata)

            data_all.append(metadata)
            print (str(self.threadID) + ": " + title + " -----> " + feedurl)

        print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Exiting " + str(self.threadID))

def crawlItunesWebpage(startlink, savedir):
    # Program start - Let's collect all category links in Apple's directory
    allcatpage = requests.get(startlink, timeout=5)
    categories = BeautifulSoup(allcatpage.content, "html.parser")

    # ... but only if the crawling directory does not yet exist, otherwise we'll reload the file created previously
    if not os.path.exists(savedir):
        os.mkdir(savedir)
        
    try:
        with open(cfgdir + '\\allpodcastlinks.json', "r") as read_file:
            podcastlinks = json.load(read_file)
        return podcastlinks
    except:
        print ("no old crawl available, we start from scratch")

    for category in categories.select('.top-level-genre'): # Loop through all genres
        categorypage = requests.get(category['href'], timeout=5)
        alphabetpages = BeautifulSoup(categorypage.content, "html.parser")
        itunesGenre = category.get_text()
        print (itunesGenre)

        for letter in ascii_uppercase + "ÄÖÜ*": # Subpages from A-Z + ÄÖÜ + *
            letterpageurl = category['href'] + "&letter=" + letter
            letterpage = requests.get(letterpageurl, timeout=5)
            pagedletterpage = BeautifulSoup(letterpage.content, 'html.parser')
            print (itunesGenre + " - " + letter)

            pgcount = 1
            linkcount = 1

            while linkcount>0:
                print (pgcount)
                pgurl = letterpageurl + "&page=" + str(pgcount)
                pgcount += 1

                podcastpage = requests.get(pgurl, timeout=5)
                allpodcasts = BeautifulSoup(podcastpage.content, 'html.parser')
                allpodcastlinks = allpodcasts.select('#selectedcontent ul>li a')
                linkcount = len(allpodcastlinks)

                for link in allpodcastlinks: # Finally! We loop through all podcast links! Yey!
                    if "/id" in link['href']:
                        theID = get_id(link['href'])

                        # Duplikate ausschließen
                        if not theID in ids:
                            ids.append(theID)
                            linkinfo = {
                                "link": link['href'],
                                "itunesID": theID
                            }
                            podcastlinks.append(linkinfo)

                if linkcount == 1: # Bug in itunes: Jede page hat mindestens einen podcast, egal wie hoch die Paginierungszahl. Eine Seite mit nur einem Podcast ist also garantiert die letzte.
                    linkcount = 0

    # Save links...
    with open(savedir + '\\allpodcastlinks.json', 'w', newline="") as outfile:
        json.dump(podcastlinks, outfile)

    return podcastlinks

def iTunesLookup(luIDs):
    starturl = 'https://itunes.apple.com/de/lookup?id='
    lookupurl = ""

    while (luIDs.qsize()>0):
        x = luIDs.get()
        lookupurl += x + ','
    
    c = 0
    while True:
        try:
            r =  requests.get(starturl + lookupurl, timeout=5)

            if (r.status_code==200):
                break
            
        except:
            c += 1
            if (c>=5):
                raise
            print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> let's sleep a moment and then retry...")
            time.sleep(c * 10)

    luresults = r.json()

    return luresults["results"]

def resolveFeedurls(savedir, podcastlinks):
    try: 
        with open(cfgdir + '\\allfeeds.json', "r") as read_file:
            allfeeds = json.load(read_file)
            return allfeeds
    except:
        print("no old data, we start from scratch")

    print ("resolving feed urls...")

    # First step: We cannot work with Apple's links, let's replace them with Feed URLs
    try: 
        for x in podcastlinks: 
            theID = str(x["itunesID"])

            # did we see this ID before?
            if (theID in allfeeds.keys()):
                continue
                
            else: # let's ask Apple. 
                idStack.put(theID)

                if (idStack.qsize() >= random.randint(50,200)): # some variation in requests protects us from being locked out
                    
                    for x in iTunesLookup(idStack):
                        if ("feedUrl" in x.keys()): 
                            allfeeds[x["collectionId"]] = [x["feedUrl"], x["primaryGenreName"], x["releaseDate"]]
                            idcountpercall += 1
                            print (str(idcountpercall)+ ": " + str(x["collectionId"]) + " : " + x["feedUrl"])

        
    except:
        print ("f*ck.")
        savedata (allfeeds, savedir + '\\allfeeds_partialdata.json')
        raise    

    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> securing all resolved feeds")
    savedata (allfeeds, savedir + '\\allfeeds.json') 

    return allfeeds

print ("resolving feed urls...")

# Apple lists podcasts in their directory online. Let's collect their landing pages
ApplePodcastLinks = crawlItunesWebpage(slink, sdir)

# Convert Apple URLs into feed urls
feeds = resolveFeedurls(sdir, ApplePodcastLinks)

# create the work packages
for i in range(threadpool):
    feedqueues.append([])

queueID = 0
for x in feeds.keys():
    feedqueues[queueID].append(x)
    queueID += 1
    if (queueID==threadpool):
        queueID = 0

# setup thread pool
for x in range(threadpool):
    aThread = myThread(x)
    allthreads.append(aThread)
    aThread.daemon = True
    aThread.start()

for x in range(threadpool):
    allthreads[x].join()

saveall(sdir)   

print ("so long and thanks for all the fish.")
