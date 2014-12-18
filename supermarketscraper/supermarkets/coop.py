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
    LogI("Fetching Coop discounts...")
    start_time = time.time() * 1000

    root_url = 'http://www.coop.nl'
    index_url = root_url + '/aanbiedingen'
    
    try:
        response = requests.get(index_url, headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    try:
        soup = bs4.BeautifulSoup(response.text)
        soup.encode('utf-8')
    except:
        LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return

    count = 0
    failedcount = 0
    totalexceptions = 0

    category_divs = soup.findAll('div', {'class':'deal'})
    for div in category_divs:
        exceptioncount = 0
        temp_data = {}
        temp_data = models.defaultModel.copy()
        temp_data['supermarket'] = 'coop'
        temp_data['url'] = index_url

        # PRODUCTNAME
        try:
            temp_data['productname'] = div.find('h3').get_text()
        except:
            LogE("[IGNORING] Productname not found","{0}".format(sys.exc_info()[0]))
            exceptioncount = exceptioncount + 1
            pass

        # DURATION
        try:
            temp_data['duration'] = soup.select('div#ctl00_ctl00_ContentPlaceHolderMain_cpLeftAndContent_Header2_divTextLink div.periode strong')[0].get_text() + " t/m " + soup.select('div#ctl00_ctl00_ContentPlaceHolderMain_cpLeftAndContent_Header2_divTextLink div.periode strong')[1].get_text()
        except IndexError as e:
            LogE("[IGNORING] Duration not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # IMAGE
        try:
            temp_data['image'] = root_url + div.find('img').get('src')
        except:
            LogE("[IGNORING] Image not found","{0}".format(sys.exc_info()[0]))
            exceptioncount = exceptioncount + 1
            pass
        
        # DESCRIPTION
        try:
            temp_data['description'] = ''
        except IndexError as e:
            LogE("[IGNORING] Description not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # AMOUNT
        try:
            temp_data['amount'] = ", ".join(str(info.get_text()) for info in div.select('div.deal-info ul li'))
        except IndexError as e:
            LogE("[IGNORING] Amount not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        # ACTION PRICE
        tempActPrice = div.select('span.deal-euros')
        if tempActPrice:
            temp_data['action_price'] = tempActPrice[0].get_text()
        else:
            if div.select('div.i50procentkorting'):
                temp_data['action_price'] = "50% korting"
            elif div.select('div.i25procentkorting'):
                temp_data['action_price'] = "25% korting"
            elif div.select('div.i2halen1betalen'):
                temp_data['action_price'] = "2 halen, 1 betalen"
            else:
                LogE("[IGNORING] Action price not found","{0}".format("Skipped all possible options"))
                exceptioncount = exceptioncount + 1

        count = count + 1
        totalexceptions = totalexceptions + exceptioncount
        if exceptioncount > settings.maxErrors:
            LogE("Too much missing info, skipping this discount","{0} Errors occured".format(exceptioncount))
            failedcount = failedcount + 1
        else:
            db.insert(temp_data)
            LogD("[{0}] ({1}) Fetched '{2}'".format(exceptioncount, count, temp_data['productname']))
        
        if failedcount > settings.maxFailedDiscounts:
            LogE("Skipping this supermarket, too much missing info.","More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
            LogI("Skipping this supermarket, too much missing info")
            LogI("More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
            return

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} AH discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))
 
def test():
    #will define test here
    LogI("Coop test")