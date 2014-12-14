import bs4
import requests
import json
import time
import sys
import traceback
import cssutils
from util.logging import *
import util.settings as settings
import models.model as models

import util.database as db

root_url = 'https://www.dirk.nl/'
index_url = root_url + 'aanbiedingen'
 
def get_actie_page_urls():
    response = requests.get(index_url, headers=settings.headers)
    soup = bs4.BeautifulSoup(response.text)
    urls = [a.attrs.get('href') for a in soup.select('div.rightside div.body p a[href^=aanbiedingen/]')]
    return urls

def get_actie_data(actie_page_url):
    actie_data = {}
    actie_data = models.defaultModel.copy()
    actie_data['supermarket'] = 'dirk'
    url = root_url + actie_page_url
    response = requests.get(url, headers=settings.headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')
    actie_data['url'] = root_url + actie_page_url
    actie_data['productname'] = soup.find('h2').get_text()
    actie_data['duration'] = soup.select('div.fromTill')[0].get_text().strip()

    amount = soup.select('div.subtitle')[0].get_text().strip()
    if(amount != '' and amount != ' '):
        actie_data['amount'] = amount 

    div_style = soup.find('div', {'class':'image'})['style']
    style = cssutils.parseStyle(div_style)
    url = style['background-image']
    url = url.replace('url(', '').replace(')', '')
    actie_data['image'] = root_url + url

    try:
        actie_data['action_price'] = soup.select('div.star')[0].get('title').strip().replace(u"\u20AC ","").replace(",",".")
    except:
        pass

    try:
        actie_data['old_price'] = soup.select('span.stripe')[0].get_text()
    except:
        pass

    return actie_data
 
def fetch():
    try:
        LogI("Fetching Dirk discounts...")
        start_time = time.time() * 1000

        count = 0

        actie_page_urls = get_actie_page_urls()
        for actie_page_url in actie_page_urls:
            single_output = get_actie_data(actie_page_url)
            
            count = count + 1
            db.insert(single_output)

            if settings.debugging:
                LogD("({0}) Fetched '{1}'".format(count, single_output['productname']))

        seconds = (time.time() * 1000) - start_time
        LogI("Done fetching {0} Dirk discounts in {1}ms.\n".format(count, format(seconds, '.2f')))    
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
    LogI("Dirk test")