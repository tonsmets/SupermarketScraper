SupermarketScraper
==================

Python project for scraping Dutch supermarkets

Since big data and data gathering are words you hear quite often, I started looking into gathering data that I thought was interesting.

This is still a work in progress. The code you find today could be gone or heavily modified by tomorrow!

## Current supported supermarkets:
- [x] Albert Heijn
- [x] C1000
- [x] Coop
- [x] Deka
- [ ] Dirk
- [x] Jan Linders
- [x] Jumbo

## DEPENDENCIES
In order to run this script you need to have some dependencies installed:
* Python3
* pip3 (to make installing the dependencies easier)
* BeautifulSoup4
* Requests
* PyMongo
* html5lib
* colorama
* cssutils

There are some settings in util/settings.py you need to edit for your needs. The defaults will probably work.

## TODO
- [x] Make main file to run the scraper and scrape all supermarkets
- [x] Define better project structure
- [x] Make the supermarkets into "modules"
- [ ] Add as many supermarkets as possible
- [ ] Build tests to see if all scraping still works
- [x] Add database support and define a model to store all data in
- [x] Add debugging
- [x] Add custom logging (with colors)
- [ ] Add error handling

## OPTIONAL
- [ ] Add web interface to view all results
- [ ] Add support for scraping via Tor