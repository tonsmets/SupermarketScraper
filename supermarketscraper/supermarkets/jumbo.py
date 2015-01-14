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

root_url = 'http://www.jumbo.com'
index_url = root_url + '/aanbiedingen'

duration = ""

count = 0
failedcount = 0
totalexceptions = 0
 
def get_discount_data(actie_page_url):
    global duration
    global count
    global totalexceptions
    global failedcount
    
    try:
        response = requests.get(actie_page_url, headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    try:
        soup = bs4.BeautifulSoup(response.text)
        soup.encode('utf-8')
    except:
        LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return

    output = []

    for discount in soup.findAll('li', {'class': 'jum-result'}):
        exceptioncount = 0
        discount_data = {}
        discount_data = models.defaultModel.copy()
        discount_data['supermarket'] = 'jumbo'
        discount_data['url'] = index_url
        try:
            discount_data['productname'] = discount.find('h3').get_text()
        except:
            LogE("[IGNORING] Image not found","{0}".format(sys.exc_info()[0]))
            exceptioncount = exceptioncount + 1
            pass

        discount_data['duration'] = duration

        try:
            discount_data['amount'] = discount.select('dd.jum-promotion-text-field')[0].get_text()
        except IndexError as e:
            LogE("[IGNORING] Amount not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        try:
            discount_data['image'] = 'http://www.jumbo.com' + discount.select('dd.jum-item-figure img')[0].get('src')
        except IndexError as e:
            LogE("[IGNORING] Image not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        try:
            discount_data['action_price'] = discount.find(text=re.compile('Actieprijs')).replace("Actieprijs ","")
        except AttributeError as e:
            LogE("[IGNORING] Action price not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        try:
            discount_data['old_price'] = discount.find(text=re.compile('Normale prijs')).replace("Normale prijs ","")
        except AttributeError as e:
            LogE("[IGNORING] Old price not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        count = count + 1
        totalexceptions = totalexceptions + exceptioncount
        if exceptioncount > settings.maxErrors:
            LogE("Too much missing info, skipping this discount","{0} Errors occured".format(exceptioncount))
            failedcount = failedcount + 1
        else:
            db.insert(discount_data)
            LogD("[{0}] ({1}) Fetched '{2}'".format(exceptioncount, count, discount_data['productname']))
        
        if failedcount > settings.maxFailedDiscounts:
            LogE("Skipping this supermarket, too much missing info.","More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
            LogI("Skipping this supermarket, too much missing info")
            LogI("More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
            return

    return output
 
def fetch():
    LogI("Fetching Jumbo discounts...")
    start_time = time.time() * 1000
    try:
        response = requests.get(index_url, headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return
    
    try:
        soup = bs4.BeautifulSoup(response.text, 'html5lib')
    except:
        LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return


    discount_page_urls = []

    try:
        amount = soup.find('div', {'class' : 'ws-promotion-listing-pagination'}).get('data-jum-pagecount')
        dataUrl = soup.find('div', {'class' : 'ws-promotion-listing-pagination'}).get('data-jum-pagination-link-template')[:-1]
        #duration = soup.select('li.jum-content-type-summary')[0].get_text()
        
        for x in range(0, int(amount) + 1):
            discount_page_urls.append(dataUrl + str(x))
    except:
        LogE("Unable to find discount urls","{0}".format(sys.exc_info()[0]))
        return

    global count
    global totalexceptions


    for discount_page_url in discount_page_urls:
        get_discount_data(discount_page_url) 

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} Jumbo discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def test():
    #will define test here
    print("Jumbo test")
 