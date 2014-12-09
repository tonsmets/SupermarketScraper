SupermarketScraper
==================

Python project for scraping Dutch supermarkets

Since big data and data gathering are words you hear quite often, I started looking into gathering data that I thought was interesting.

This is still a work in progress. The code you find today could be gone or heavily modified by tomorrow!

## Current supported supermarkets:
- [x] Albert Heijn
- [ ] C1000
- [ ] Coop
- [ ] Deka
- [ ] Dirk
- [ ] Jan Linders
- [ ] Jumbo

## DEPENDENCIES
In order to run this script you need to have some dependencies installed:
* Python3
* pip3 (to make installing the dependencies easier)
* BeautifulSoup4
* Requests
* PyMongo
* html5lib
* colorama

There are some settings in util/settings.py you need to edit for your needs. The defaults will probably work.

## TODO
- [ ] Make main file to run the scraper and scrape all supermarkets
- [ ] Define better project structure
- [x] Make the supermarkets into "modules"
- [ ] Add as many supermarkets as possible
- [ ] Build tests to see if all scraping still works
- [x] Add database support and define a model to store all data in
- [x] Add debugging
- [x] Add custom logging (with colors)

## OPTIONAL
- [ ] Add web interface to view all results
- [ ] Add support for scraping via Tor