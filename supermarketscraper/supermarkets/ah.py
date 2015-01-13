import bs4
import requests
import json
import time
import sys
import traceback
from util.logging import *
import util.settings as settings
import models.model as models
import util.database as db


def fetch():
    LogI("Fetching AH discounts...")
    start_time = time.time() * 1000
    
    index_url = 'http://www.ah.nl/bonus'

    try:
        r = requests.get(index_url, headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return
    
    try:
        soup = bs4.BeautifulSoup(r.text, 'html5lib')
        soup.encode('utf-8')
    except:
        LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return

    count = 0
    failedcount = 0
    totalexceptions = 0

    bonus_products = soup.findAll(attrs={'data-class': 'product'})
    for bonus in bonus_products:
        exceptioncount = 0
        superdata = {}
        superdata = models.defaultModel.copy()
        superdata['supermarket'] = 'ah'

        # URL
        try:
            superdata['url'] = "http://www.ah.nl" + bonus.select('div.detail a')[0].get('href')
            superdata['url'] = "http://www.ah.nl" + bonus.get('href')
        except (IndexError, TypeError) as e:
            if superdata['url'] is None:
                LogE("[IGNORING] Error","{0}".format(e))
                exceptioncount = exceptioncount + 1
            pass

        # PRODUCTNAME
        try:
            superdata['productname'] = bonus.select('div.detail h2')[0].get_text().strip()
        except IndexError as e:
            LogE("[IGNORING] Productname not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # DURATION
        try:
            #superdata['duration'] = soup.select('div.columns p.header-bar__term')[0].get_text()
            superdata['duration'] = 'This week'
        except IndexError as e:
            LogE("[IGNORING] Duration not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # IMAGE
        try:
            superdata['image'] = bonus.select('div.image img')[0].get('data-original')
        except IndexError as e:
            LogE("[IGNORING] Image not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass
        
        # AMOUNT
        try:
            tempAmount = bonus.select('div.image p.unit')[0].get_text().strip()
            if tempAmount is not None:
                superdata['amount'] = tempAmount
        except IndexError as e:
            LogE("[IGNORING] Amount not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass
        
        # BONUS
        try:
            superdata['bonus'] = bonus.select('div.shield')[0].get_text().strip()
        except IndexError as e:
            LogE("[IGNORING] Bonus not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # ACTION PRICE    
        try:
            superdata['action_price'] = bonus.select('p.price ins')[0].get_text()
        except IndexError as e:
            LogE("[IGNORING] Action price not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # OLD PRICE
        try:
            superdata['old_price'] = bonus.select('p.price del')[0].get_text()
        except IndexError as e:
            LogE("[IGNORING] Old price not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        count = count + 1
        totalexceptions = totalexceptions + exceptioncount
        if exceptioncount > settings.maxErrors:
            LogE("Too much missing info, skipping this discount","{0} Errors occured".format(exceptioncount))
            failedcount = failedcount + 1
        else:
            db.insert(superdata)
            LogD("[{0}] ({1}) Fetched '{2}'".format(exceptioncount, count, superdata['productname']))
        
        if failedcount > settings.maxFailedDiscounts:
            LogE("Skipping this supermarket, too much missing info.","More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
            LogI("Skipping this supermarket, too much missing info")
            LogI("More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
            return

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} AH discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def test():
    #will define test here
    LogI("AH test")
