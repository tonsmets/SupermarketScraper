SupermarketScraper
==================

Python project for scraping Dutch supermarkets

The idea behind this piece of code is to run it on set intervals (cron jobs) to collect the data. Before running (1 day before, or just a couple of hours), it should run tests to see if everything is still working (it is always possible that a website is changed). If something is broken, it should give you enough time to fix the problem before the cron job wil start the scraping proces.

This is still a work in progress. The code you find today could be gone or heavily modified by tomorrow!

## Current supported supermarkets:
- [x] Albert Heijn
- [x] C1000
- [x] Coop
- [x] Deka
- [x] Dirk
- [x] Jan Linders
- [x] Jumbo

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

There are some settings in util/settings.py you need to edit for your needs, but the defaults will probably work just fine.

## To-Do's
- [x] Make main file to run the scraper and scrape all supermarkets
- [x] Define better project structure
- [x] Make the supermarkets into "modules"
- [ ] Add as many supermarkets as possible
- [ ] Build tests to see if all scraping still works
- [x] Add database support and define a model to store all data in
- [x] Add debugging
- [x] Add custom logging (with colors)
- [ ] Add error handling
- [ ] Add argument parsing to make different modes possible

## Optional additions
- [ ] Add web interface to view all results
- [ ] Add support for scraping via Tor