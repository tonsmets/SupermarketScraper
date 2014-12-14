import bs4
import requests
import json
import time
import sys
import traceback
import re
from util.logging import *
import util.settings as settings
import models.model as models

import util.database as db

def fetch():
    try:
        LogI("Fetching C1000 discounts...")
        start_time = time.time() * 1000

        root_url = 'http://www.c1000.nl/'
        index_url = root_url + 'aanbiedingen'
        
        response = requests.get(index_url, headers=settings.headers)
        soup = bs4.BeautifulSoup(response.text)
        soup.encode('utf-8')

        count = 0

        category_divs = soup.findAll('div', id=re.compile("^content_0_contentrij1_0_weekAanbiedingen_listViewCategorieen_"))
        for div in category_divs:
            list_items = div.findAll('li')
            for li in list_items:
                temp_data = {}
                temp_data = models.defaultModel.copy()
                temp_data['supermarket'] = 'c1000'
                temp_data['url'] = index_url
                temp_data['productname'] = li.find('h2').get_text()
                temp_data['duration'] = re.sub(r'[\t\r\n]', '', soup.find('a', {'id' : 'content_0_contentrij1_0_linkTabHuidigeWeek'}).get_text()).strip().replace('                     ', ' ')
                temp_data['description'] = re.sub(r'[\t\r\n]', '', li.select('div.product_details p')[0].get_text())
                temp_data['image'] = root_url + li.find('img').get('src')
                try:
                    temp_data['amount'] = li.select('div.pricetag em')[0].get_text()
                except:
                    pass

                try:
                    temp_data['action_price'] = li.select('div.pricetag strong')[0].get_text()
                except:
                    pass

                try:
                    temp_data['action_price'] = li.select('img.visual')[1].get('alt')
                except:
                    pass

                try:
                    temp_data['old_price'] = li.select('del')[0].get_text()
                except:
                    pass

                count = count + 1
                db.insert(temp_data)

                if settings.debugging:
                    LogD("({0}) Fetched '{1}'".format(count, temp_data['productname']))

        
        seconds = (time.time() * 1000) - start_time
        LogI("Done fetching {0} C1000 discounts in {1}ms.\n".format(count, format(seconds, '.2f')))
    except requests.exceptions.ConnectionError:
        e = None
        if settings.debugging:
            e = traceback.format_exc()
        else:
            e = sys.exc_info()[0]
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(e))
        pass
    except:
        e = None
        if settings.debugging:
            e = traceback.format_exc()
        else:
            e = sys.exc_info()[0]
        LogE("General failure! Check Traceback for info!", "{0}".format(e))
        pass

def test():
    #will define test here
    LogI("C1000 test")
