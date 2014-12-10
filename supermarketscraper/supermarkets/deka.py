# The amount is found by getting the class of the price tag.
# 248   Per stuk
# 249   Per pak
# 250   Per zak
# 251   Per fles
# 252   Per krat
# 253   500 gram
# 254   kilo
# 255   2 voor
# 256   3 voor
# 257   4 voor //Assumption
# 258   5 voor
# 259   ???
# 260   <empty>
# 261   ???
# 262   Per bak
# 263   Per blik
# 264   Per doos
# 265   Per set

import bs4
import requests
import json
import time
import re
from util.logging import *
import util.settings as settings
import models.model as models

import util.database as db

root_url = 'http://www.dekamarkt.nl/'
index_url = root_url + 'aanbiedingen'

count = 0

duration = ""
 
def get_actie_page_urls():
    global duration
    response = requests.get(index_url, headers=settings.headers)
    soup = bs4.BeautifulSoup(response.text)
    urls = soup.find('div', {'class':'paging'})

    for e in urls.findAll('a', {'class': 'last'}):
        e.extract()

    duration = soup.select('div.aanbiedingenData')[0].get_text().replace("Aanbieding geldig van ","")
    
    return [a.attrs.get('href') for a in soup.select('a[href^=https://www.dekamarkt.nl/aanbiedingen?]')]
 
def get_actie_data(actie_page_url):
    response = requests.get(actie_page_url, headers=settings.headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    global count
    global duration

    category_divs = soup.findAll('div', {'class':'aanbieding'})
    for div in category_divs:
        temp_data = {}
        temp_data = models.defaultModel.copy()
        temp_data['supermarket'] = 'deka'
        temp_data['url'] = actie_page_url
        temp_data['productname'] = div.find('h2').get_text()
        #temp_data['duration'] = re.sub(r'[\t\r\n]', '', soup.find('a', {'id' : 'content_0_contentrij1_0_linkTabHuidigeWeek'}).get_text()).strip().replace('                     ', ' ')
        temp_data['description'] = div.select('div.text')[0].get_text()
        temp_data['image'] = root_url + div.find('img').get('src')
        temp_data['duration'] = duration
        temp_data['amount'] = getAmount(div.find('div', {'class' : re.compile("tag")}).get('class')[1].replace('tag', ''))
        
        try:
            temp_data['action_price'] = div.select('span.current span.whole')[0].get_text() + div.select('span.current span.part')[0].get_text()
        except:
            pass

        try:
            temp_data['old_price'] = div.select('span.old span.whole')[0].get_text() + div.select('span.old span.part')[0].get_text()
        except:
            pass

        count = count + 1
        db.insert(temp_data)

        if settings.debugging:
            LogD("({0}) Fetched '{1}'".format(count, temp_data['productname']))


 
def fetch():
    LogI("Fetching Deka discounts...")
    start_time = time.time() * 1000

    global count

    actie_page_urls = get_actie_page_urls()
    for actie_page_url in actie_page_urls:
        single_output = get_actie_data(actie_page_url)

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} Deka discounts in {1}ms.\n".format(count, format(seconds, '.2f')))


def getAmount(tag):
    if tag == '248':
        return "Per stuk"
    elif tag == '249':
        return "Per pak"
    elif tag == '250':
        return "Per zak"
    elif tag == '251':
        return "Per fles"
    elif tag == '252':
        return "Per krat"
    elif tag == '253':
        return "500 gram"
    elif tag == '254':
        return "Kilo"
    elif tag == '255':
        return "2 voor"
    elif tag == '256':
        return "3 voor"
    elif tag == '257':
        return "4 voor"
    elif tag == '258':
        return "5 voor"
    elif tag == '262':
        return "Per bak"
    elif tag == '263':
        return "Per blik"
    elif tag == '264':
        return "Per doos"
    elif tag == '265':
        return "Per set"
    else:
        pass

def test():
    #will define test here
    LogI("Deka test")