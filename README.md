SupermarketScraper
==================

Python project for scraping Dutch supermarkets

Since big data and data gathering are words you hear quite often, I started looking into gathering data that I thought was interesting.

This is still a work in progress.

## Current supported supermarkets:
- [x] Albert Heijn
- [ ] C1000
- [ ] Coop
- [ ] Deka
- [ ] Dirk
- [ ] Jan Linders
- [x] Jumbo (sort of)

## MANUAL
In order to run this script you need to have some dependencies installed:
* Python3
* pip3 (to make installing the dependencies easier)
* BeautifulSoup4
* Requests
* PyMongo

## TODO
- [ ] Make main file to run the scraper and scrape all supermarkets
- [ ] Define better project structure
- [ ] Make the supermarkets into "modules"
- [ ] Build tests to see if all scraping still works
- [ ] Add database support and define a model to store all data in

## OPTIONAL
- [ ] Add web interface to view all results