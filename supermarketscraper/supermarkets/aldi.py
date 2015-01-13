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
    LogI("Fetching Aldi discounts...")
    start_time = time.time() * 1000
    
    index_url = 'http://www.aldi.nl/'

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

    pages = soup.select('ul#ul_menu_142002 li')[0]
    pages = pages.select('ul li a')
    for page in pages:
        try:
            r = requests.get(index_url + page.get('href'), headers=settings.headers)
        except requests.exceptions.ConnectionError as ce:
            LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
            return
        
        try:
            soup = bs4.BeautifulSoup(r.text, 'html5lib')
            soup.encode('utf-8')
        except:
            LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
            return

        duration = "n/a"

        try:
            duration = "Vanaf " + soup.select('li.active h2.tab-headline span')[0].get_text()
        except IndexError as e:
            LogE("[IGNORING] Duration not found","{0}".format(e))
            totalexceptions = totalexceptions + 1
            pass
        

        discounts = soup.select('div.product-tile')
        for discount in discounts:
            exceptioncount = 0
            superdata = {}
            superdata = models.defaultModel.copy()
            superdata['supermarket'] = 'aldi'

            # URL
            try:
                superdata['url'] = index_url + discount.select('a')[1].get('href')
            except (IndexError, TypeError) as e:
                if superdata['url'] is None:
                    LogE("[IGNORING] Error","{0}".format(e))
                    exceptioncount = exceptioncount + 1
                pass

            # PRODUCTNAME
            try:
                superdata['productname'] = discount.select('h3')[0].get_text().strip()
            except IndexError as e:
                LogE("[IGNORING] Productname not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass  

            # DURATION
            try:
                #superdata['duration'] = soup.select('div.columns p.header-bar__term')[0].get_text()
                superdata['duration'] = duration
            except IndexError as e:
                LogE("[IGNORING] Duration not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass

            # IMAGE
            try:
                superdata['image'] = index_url + discount.select('img')[0].get('src')
            except IndexError as e:
                LogE("[IGNORING] Image not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass
        
            # AMOUNT
            try:
                tempAmount = discount.select('div.unit')[0].get_text().strip()
                if tempAmount is not None:
                    superdata['amount'] = tempAmount
            except IndexError as e:
                LogE("[IGNORING] Amount not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass

            # ACTION PRICE    
            try:
                superdata['action_price'] = discount.select('strong')[0].get_text().replace('*','')
            except IndexError as e:
                LogE("[IGNORING] Action price not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass

            # DESCRIPTION  
            # try:
            #     superdata['description'] = discount.select('div.richtext')[0].get_text().strip()
            # except IndexError as e:
            #     LogE("[IGNORING] Description not found","{0}".format(e))
            #     exceptioncount = exceptioncount + 1
            #     pass

            # OLD PRICE
            try:
                superdata['old_price'] = "n/a"
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
    LogI("Done fetching {0} Aldi discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def test():
    #will define test here
    LogI("AH test")
