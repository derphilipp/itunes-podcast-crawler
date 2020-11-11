# itunes-podcast-crawler
Collects itunes Podcast links on the itunes podcast directory, retrieves feeds through the apple lookup api and collects key info from the podcast feeds. Use multithreadedcrawl.py for your own experiments. No guarantees are given. Please note that the itunes directory contains A LOT of links and that feeds can get multiple megabites in size...
A crawl will take approximetely 1-2 days and at the time of this writing (Nov 2020) you can expect about 1GB of result data. 

Please note: this is a rough and hacky script, no guarantees are given nor is it an example of good programming practices. You'll need to install beautifulsoup4 for it to run and consider adjusting the folder structures listed in the variables of the top section. 

The crawler will look into a config directory to see if an allfeeds.json or allpodcastlinks.json file already exist. If that is the case then it will use those to start instead of doing a full crawl to speed up the process. 

Some other considerations: 
- the crawler is going through all feeds in one go. Feeds that cannot be retrieved are listed as errors and will not be included in the result set. A future iteration fo this tool may include a mechanism to queue those feeds and run through them at the end of the crawl for a second time because I'm sure some of those errors would be solved by trying at a different moment. 
- the crawler's first step is to iterate through the Apple directory's landing page which is organized by alphabet. Unfortunately many languages have special characters and I decided against iterating over all of them. So I may miss a number of shows. However, my personal focus was on English and German as a language and both should be covered. 
- while I call Apple's API and the feeds to retrieve information I decided not to store everything those calls return. In other words: there is more stuff YOU could decide to keep that I throw away. 
- Feeds have errors. That means some podcasts may be misattributed because settings like language have been wrong
- Depending on the geo you're starting from Apple may not show you everything. E.g. if you're crawling from India then all podcasts that contain even just one episode flagged as "explicit" will not be in the result set for Apple is filtering those to comply with local laws. 

the script generates a range of result files that are to some degree repetitive. 

- allfeeds.json => this file contains the resolved feed urls
- allpodcastlinks.json => result of the web crawl over the itunes directory, contains itunes URLs
- data_all.json => everything collected from the feeds
- data_all_2020.json => feeds that saw an update in 2020
- data_de.json => everything flagged as German
- data_en.json => everything flagged as English
- errors.json => feeds the crawler could not retrieve
