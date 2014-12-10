import bs4
import requests
import re
import json
import time
from util.logging import *
import util.settings as settings
import models.model as models

import util.database as db

root_url = 'http://www.jumbo.com'
index_url = root_url + '/aanbiedingen'
 
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}

duration = ""

count = 0
 
def get_discount_page_urls():
    global duration
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text)
    amount = soup.find('div', {'class' : 'ws-promotion-listing-pagination'}).get('data-jum-pagecount')
    dataUrl = soup.find('div', {'class' : 'ws-promotion-listing-pagination'}).get('data-jum-pagination-link-template')[:-1]
    duration = soup.select('ul.jum-lister-navigation-tab li')[0].get_text()
    urls = []
    for x in range(0, int(amount) + 1):
        urls.append(dataUrl + str(x))

    return urls
 
def get_discount_data(actie_page_url):
    global duration
    global count
    response = requests.get(actie_page_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    output = []

    for discount in soup.findAll('li', {'class': 'jum-result'}):
        discount_data = {}
        discount_data = models.defaultModel.copy()
        discount_data['supermarket'] = 'jumbo'
        discount_data['url'] = index_url
        discount_data['productname'] = discount.find('h3').get_text()
        discount_data['duration'] = duration
        discount_data['amount'] = discount.select('dd.jum-promotion-text-field')[0].get_text()
        discount_data['image'] = discount.find('img').get('src')

        try:
            discount_data['action_price'] = discount.find(text=re.compile('Actieprijs')).replace("Actieprijs ","")
        except:
            pass

        try:
            discount_data['old_price'] = discount.find(text=re.compile('Normale prijs')).replace("Normale prijs ","")
        except:
            pass
        count = count + 1
        output.append(discount_data)
        if settings.debugging:
            LogD("({0}) Fetched '{1}'".format(count, discount_data['productname']))

    return output
 
def fetch():
    LogI("Fetching Jumbo discounts...")
    start_time = time.time() * 1000

    global count
    
    discount_page_urls = get_discount_page_urls()

    for discount_page_url in discount_page_urls:
        superdata = get_discount_data(discount_page_url) 
        db.insert(superdata)

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} Jumbo discounts in {1}ms.\n".format(count, format(seconds, '.2f')))

def test():
    #will define test here
    print("Jumbo test")
 