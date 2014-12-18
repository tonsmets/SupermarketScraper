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

count = 0
failedcount = 0
totalexceptions = 0

def get_actie_data(actie_page_url):
    global count
    global failedcount
    global totalexceptions
    exceptioncount = 0
    actie_data = {}
    actie_data = models.defaultModel.copy()
    actie_data['supermarket'] = 'dirk'
    url = root_url + actie_page_url
    try:
        response = requests.get(url, headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    try:
        soup = bs4.BeautifulSoup(response.text)
        soup.encode('utf-8')
    except:
        LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return

    actie_data['url'] = root_url + actie_page_url

    try:
        actie_data['productname'] = soup.find('h2').get_text()
    except:
        LogE("[IGNORING] Productname not found","{0}".format(sys.exc_info()[0]))
        exceptioncount = exceptioncount + 1
        pass

    try:
        actie_data['duration'] = soup.select('div.fromTill')[0].get_text().strip()
    except IndexError as e:
        LogE("[IGNORING] Duration not found","{0}".format(e))
        exceptioncount = exceptioncount + 1
        pass

    try:
        amount = soup.select('div.subtitle')[0].get_text().strip()
        if(amount != '' and amount != ' ' and amount is not None):
            actie_data['amount'] = amount 
    except IndexError as e:
        LogE("[IGNORING] Amount not found","{0}".format(e))
        exceptioncount = exceptioncount + 1
        pass

    try:
        div_style = soup.find('div', {'class':'image'})['style']
        style = cssutils.parseStyle(div_style)
        url = style['background-image']
        url = url.replace('url(', '').replace(')', '')
        actie_data['image'] = root_url + url
    except:
        LogE("[IGNORING] Image not found","{0}".format(sys.exc_info()[0]))
        exceptioncount = exceptioncount + 1
        pass

    try:
        actie_data['action_price'] = soup.select('div.star')[0].get('title').strip().replace(u"\u20AC ","").replace(",",".")
    except IndexError as e:
        LogE("[IGNORING] Action price not found","{0}".format(e))
        exceptioncount = exceptioncount + 1
        pass

    try:
        actie_data['old_price'] = soup.select('span.stripe')[0].get_text()
    except IndexError as e:
        LogE("[IGNORING] Old price not found","{0}".format(e))
        exceptioncount = exceptioncount + 1
        pass

    totalexceptions = totalexceptions + exceptioncount

    count = count + 1
    if exceptioncount > settings.maxErrors:
        LogE("Too much missing info, skipping this discount","{0} Errors occured".format(exceptioncount))
        failedcount = failedcount + 1
    else:
        db.insert(actie_data)
        LogD("[{0}] ({1}) Fetched '{2}'".format(exceptioncount, count, actie_data['productname']))
    
    if failedcount > settings.maxFailedDiscounts:
        LogE("Skipping this supermarket, too much missing info.","More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
        LogI("Skipping this supermarket, too much missing info")
        LogI("More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
        return

def fetch():
    LogI("Fetching Dirk discounts...")
    start_time = time.time() * 1000

    try:
        response = requests.get(index_url, headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    try:
        soup = bs4.BeautifulSoup(response.text)
    except:
        LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return

    actie_page_urls = [a.attrs.get('href') for a in soup.select('div.rightside div.body p a[href^=aanbiedingen/]')]

    global count
    global failedcount
    global totalexceptions

    for actie_page_url in actie_page_urls:
        single_output = get_actie_data(actie_page_url)

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} Dirk discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def test():
    #will define test here
    LogI("Dirk test")