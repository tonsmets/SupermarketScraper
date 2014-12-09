import bs4
import requests
import re
import json
import time
from util.logging import *
import util.settings as settings
import models.model as models

import util.database as db

root_url = 'http://www.jumbosupermarkten.nl'
index_url = root_url + '/Homepage/Nu-in-de-winkel/acties/'
 
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}
 
def get_discount_page_urls():
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text)
    return [a.attrs.get('href') for a in soup.select('a[href^=/Homepage/Nu-in-de-winkel/acties/Product]')]
 
def get_discount_data(actie_page_url):
    discount_data = {}
    discount_data = models.defaultModel.copy()
    response = requests.get(root_url + actie_page_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')
    discount_data['supermarket'] = 'jumbo'
    discount_data['url'] = root_url + actie_page_url
    discount_data['productname'] = soup.select('div.header h1')[0].get_text().strip()
    discount_data['duration'] = soup.select('div.header em.subtitle')[0].get_text().strip()
    discount_data['amount'] = soup.select('div.product-detail p.description')[0].get_text().strip()
    discount_data['image'] = root_url + soup.select('img.photo')[0].get('src')

    try:
        discount_data['action-price'] = soup.select('div.content-box em.single-value')[0].get_text().strip().replace(",",".")   
    except:
        pass

    try:
        discount_data['action-price'] = soup.select('em.discount-type-alt')[0].get_text().strip()
    except:
        pass

    try:
        discount_data['action-price'] = soup.select('div.content-box em.text-subtext strong')[0].get_text().strip().replace(",",".") + soup.select('div.content-box em.text-subtext strong span')[0].get_text().strip().replace(",",".")  
    except:
        pass

    try:
        discount_data['action-price'] = soup.select('div.content-box em.text-pretext strong')[0].get_text().strip().replace(",",".")  
    except:
        pass

    try:
        discount_data['action-price'] = soup.select('div.content-box  p.action-price')[0].get_text().strip().replace("Actieprijs ", "").replace(",",".")   
    except:
        pass

    try:
        discount_data['old-price'] = soup.select('div.content-box p.pricing')[0].get_text().strip().replace("Normaal ", "")
    except:
        pass

    return discount_data
 
def fetch():
    LogI("Fetching Jumbo discounts...")
    start_time = time.time() * 1000

    count = 0

    discount_page_urls = get_discount_page_urls()
    for discount_page_url in discount_page_urls:
        superdata = get_discount_data(discount_page_url) 
        count = count + 1
        db.insert(superdata)
        if settings.debugging:
            LogD("({0}) Fetched '{1}'".format(count, superdata['productname']))

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} Jumbo discounts in {1}ms.\n".format(count, format(seconds, '.2f')))

def test():
    #will define test here
    print("Jumbo test")
 