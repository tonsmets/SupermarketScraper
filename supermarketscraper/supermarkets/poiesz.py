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
    LogI("Fetching Poiesz discounts...")
    start_time = time.time() * 1000
    
    index_url = 'http://www.poiesz-supermarkten.nl/aanbiedingen'

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

    discounts = soup.select('div.meevaller')
    for discount in discounts:
        exceptioncount = 0
        superdata = {}
        superdata = models.defaultModel.copy()
        superdata['supermarket'] = 'poiesz'

        # URL
        try:
            superdata['url'] = index_url
        except (IndexError, TypeError) as e:
            if superdata['url'] is None:
                LogE("[IGNORING] Error","{0}".format(e))
                exceptioncount = exceptioncount + 1
            pass

        # PRODUCTNAME
        try:
            superdata['productname'] = discount.select('h2')[0].get_text().strip()
        except IndexError as e:
            LogE("[IGNORING] Productname not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # DURATION
        try:
            superdata['duration'] = soup.select('div.validThrough')[0].get_text().strip()
        except IndexError as e:
            LogE("[IGNORING] Duration not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # IMAGE
        try:
            superdata['image'] = "http://www.poiesz-supermarkten.nl/" + discount.select('img')[0].get('src')
        except IndexError as e:
            LogE("[IGNORING] Image not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass
        
        # AMOUNT
        try:
            tempAmount = discount.select('div.shieldNew div.top')[0].get_text().strip()
            if tempAmount is not None:
                superdata['amount'] = tempAmount
        except IndexError as e:
            LogE("[IGNORING] Amount not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # DESCRIPTION  
        try:
            subtitles = discount.select('div.subtitle')
            for sub in subtitles:
                if sub.get_text() is not None:
                    superdata['description'] = superdata['description'] + sub.get_text().strip() + ' '
        except IndexError as e:
            LogE("[IGNORING] Description not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # ACTION PRICE    
        try:
            superdata['action_price'] = discount.select('div.forPrice div.whole')[0].get_text() + "." + discount.select('div.forPrice div.part')[0].get_text()
        except IndexError as e:
            try:
                superdata['action_price'] = discount.select('div.forPrice div.combined')[0].get_text()
            except IndexError as ex:  
                if superdata['action_price'] is None:
                    LogE("[IGNORING] Action price not found","{0}".format(e))
                    exceptioncount = exceptioncount + 1
                pass
            pass

        # OLD PRICE
        try:
            superdata['old_price'] = discount.select('div.fromPriceWrap')[0].get_text()
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
    LogI("Done fetching {0} Poiesz discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def test():
    #will define test here
    LogI("AH test")
