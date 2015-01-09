SupermarketScraper
==================

Python project for scraping Dutch supermarkets

The idea behind this piece of code is to run it on set intervals (cron jobs) to collect the data. Before running (1 day before, or just a couple of hours), it should run tests to see if everything is still working (it is always possible that a website has changed). If something is broken, it should give you enough time to fix the problem before the cron job wil start the scraping proces.

In the second phase of this project I would like to add some postprocessing for the data. Things like downloading images, storing them and deleting old ones. It should als store some extra data about each run of the scraper to prevent me from drowning in endless data without knowing when it was scraped :P. I will also need to add some sort of logic to prevent the scraper from adding duplicate data.

This is still a work in progress. The code you find today could be gone or heavily modified by tomorrow!

Running the script is as easy as:
```
python3 main.py
```
To get the help function, add the -h or --help argument.
```
python3 main.py -h
```

## Current supported supermarkets:
- [x] Albert Heijn
- [x] C1000
- [x] Coop
- [x] Deka
- [x] Dirk
- [x] Jan Linders
- [x] Jumbo
- [ ] Lidl
- [ ] ~~Emté~~
- [ ] Aldi
- [ ] Attent
- [ ] Poiesz

## Dependencies
In order to run this script you need to have some dependencies installed:
* Python3
* pip3 (to make installing the dependencies easier)
* BeautifulSoup4
* Requests
* PyMongo
* html5lib
* colorama
* cssutils

The software uses MongoDB as database supplier so you will also need to install that. 

To install all needed dependencies on a debian flavoured linux distribution (tested on Ubuntu 14.04 LTS) use the following commands:
```
sudo apt-get install python3 python3-pip mongodb
sudo pip3 install beautifulsoup4 requests pymongo html5lib colorama cssutils
```

There are some settings in util/settings.py you can edit for your needs, but the defaults will probably work just fine.

## First phase To-Do's
- [x] Make main file to run the scraper and scrape all supermarkets
- [x] Define better project structure
- [x] Make the supermarkets into "modules"
- [ ] Add as many supermarkets as possible
- [ ] Build tests to see if all scraping still works
- [x] Add database support and define a model to store all data in
- [x] Add debugging
- [x] Add custom logging (with colors)
- [x] Add error handling
- [x] Add argument parsing to make different modes possible (still need to add more modes)

## Second phase To-Do's
- [ ] Add image downloader and manager
- [ ] Add database logging of each scraper run
- [ ] Add data refiner to parse things like duration dates to timestamps

## Optional additions
- [ ] Add web interface to view all results
- [ ] Add support for scraping via Tor
