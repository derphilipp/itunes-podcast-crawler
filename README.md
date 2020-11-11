# itunes-podcast-crawler
Collects itunes Podcast links on the itunes podcast directory, retrieves feeds through the apple lookup api and collects key info from the podcast feeds. Use multithreadedcrawl.py for your own experiments. No guarantees are given. Please note that the itunes directory contains A LOT of links and that feeds can get multiple megabites in size...
A crawl will take approximetely 1-2 days and at the time of this writing (Nov 2020) you can expect about 1GB of result data. 

Please note: this is a rough and hacky script, no guarantees are given nor is it an example of good programming practices. You'll need to install beautifulsoup4 for it to run and consider adjusting the folder structures listed in the variables of the top section. 
