import bs4
import requests
import json
import time
from util.logging import *
import util.settings as settings
import models.model as models

import util.database as db
 
def fetch():
    LogI("Fetching Coop discounts...")
    start_time = time.time() * 1000

    root_url = 'http://www.coop.nl'
    index_url = root_url + '/aanbiedingen'
    
    response = requests.get(index_url, headers=settings.headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    count = 0

    category_divs = soup.findAll('div', {'class':'deal'})
    for div in category_divs:
        temp_data = {}
        temp_data = models.defaultModel.copy()
        temp_data['supermarket'] = 'coop'
        temp_data['url'] = index_url
        temp_data['productname'] = div.find('h3').get_text()
        temp_data['duration'] = soup.select('div#ctl00_ctl00_ContentPlaceHolderMain_cpLeftAndContent_Header2_divTextLink div.periode strong')[0].get_text() + " t/m " + soup.select('div#ctl00_ctl00_ContentPlaceHolderMain_cpLeftAndContent_Header2_divTextLink div.periode strong')[1].get_text()
        temp_data['image'] = root_url + div.find('img').get('src')
        try:
            temp_data['description'] = div.select('div.deal-info ul li')[0].get_text()
        except:
            pass

        try:
            temp_data['amount'] = div.select('div.deal-label')[0].get_text()
        except:
            pass

        try:
            temp_data['action_price'] = div.select('span.deal-euros')[0].get_text()
        except:
            pass

        try:
            temp = div.select('div.i50procentkorting')[0].get_text()
            temp_data['action_price'] = "50% korting"
        except:
            pass

        try:
            temp = div.select('div.i25procentkorting')[0].get_text()
            temp_data['action_price'] = "25% korting"
        except:
            pass

        count = count + 1
        db.insert(temp_data)

        if settings.debugging:
            LogD("({0}) Fetched '{1}'".format(count, temp_data['productname']))

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} Coop discounts in {1}ms.\n".format(count, format(seconds, '.2f')))

 
def test():
    #will define test here
    LogI("Coop test")