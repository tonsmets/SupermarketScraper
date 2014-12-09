import bs4
import requests
import json
import time
from util.logging import *
import util.settings as settings
import models.model as models

import util.database as db

def fetch():
    LogI("Fetching AH discounts...")
    start_time = time.time() * 1000
    
    index_url = 'http://www.ah.nl/bonus'

    r = requests.get(index_url, headers=settings.headers)
    soup = bs4.BeautifulSoup(r.text, 'html5lib')

    count = 0

    bonus_products = soup.findAll(attrs={'data-class': 'product'})
    for bonus in bonus_products:
        superdata = {}
        superdata = models.defaultModel.copy()
        superdata['supermarket'] = 'ah'

        try:
            superdata['url'] = "http://www.ah.nl" + bonus.select('div.detail a')[0].get('href')
        except:
            pass
        try:
            superdata['url'] = "http://www.ah.nl" + bonus.get('href')
        except:
            pass
        superdata['productname'] = bonus.select('div.detail h2')[0].get_text().strip()
        superdata['duration'] = soup.select('div.columns p.header-bar__term')[0].get_text()
        superdata['image'] = bonus.select('div.image img')[0].get('data-original')
        try:
            tempAmount = bonus.select('div.image p.unit')[0].get_text().strip()
            if (tempAmount != '' and tempAmount != ' '):
                superdata['amount'] = bonus.select('div.image p.unit')[0].get_text().strip()
        except:
            pass
        superdata['bonus'] = bonus.select('div.shield')[0].get_text().strip()
        superdata['action_price'] = bonus.select('p.price ins')[0].get_text()
        try:
            superdata['old_price'] = bonus.select('p.price del')[0].get_text()
        except:
            pass

        count = count + 1
        db.insert(superdata)

        if settings.debugging:
            LogD("({0}) Fetched '{1}'".format(count, superdata['productname']))

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} AH discounts in {1}ms.\n".format(count, format(seconds, '.2f')))

def test():
    #will define test here
    LogI("AH test")
