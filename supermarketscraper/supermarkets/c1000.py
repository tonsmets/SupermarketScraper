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

def fetch():
    LogI("Fetching C1000 discounts...")
    start_time = time.time() * 1000

    root_url = 'http://www.c1000.nl/'
    index_url = root_url + 'aanbiedingen'
    
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

    category_divs = soup.findAll('div', id=re.compile("^content_0_contentrij1_0_weekAanbiedingen_listViewCategorieen_"))
    for div in category_divs:
        list_items = div.findAll('li')
        for li in list_items:
            exceptioncount = 0
            temp_data = {}
            temp_data = models.defaultModel.copy()
            temp_data['supermarket'] = 'c1000'

            # URL
            temp_data['url'] = index_url

            # PRODUCTNAME
            try:
                temp_data['productname'] = li.find('h2').get_text().strip()
            except:
                LogE("[IGNORING] Productname not found","{0}".format(sys.exc_info()[0]))
                exceptioncount = exceptioncount + 1
                pass

            # DURATION
            try:
                temp_data['duration'] = re.sub(r'[\t\r\n]', '', soup.find('a', {'id' : 'content_0_contentrij1_0_linkTabHuidigeWeek'}).get_text()).strip().replace('                     ', ' ')
            except:
                LogE("[IGNORING] Productname not found","{0}".format(sys.exc_info()[0]))
                exceptioncount = exceptioncount + 1
                pass

            # DESCRIPTION
            try:
                temp_data['description'] = re.sub(r'[\t\r\n]', '', li.select('div.product_details p')[0].get_text().strip())
            except IndexError as e:
                LogE("[IGNORING] Description not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass

            # IMAGE
            try:
                temp_data['image'] = root_url + li.find('img').get('src')
            except:
                LogE("[IGNORING] Image not found","{0}".format(sys.exc_info()[0]))
                exceptioncount = exceptioncount + 1
                pass

            # AMOUNT
            try:
                temp_data['amount'] = li.select('div.product_details p')[0].get_text().strip()
                temp_data['amount'] = li.select('div.pricetag em')[0].get_text().strip()
            except IndexError as e:
                if temp_data['amount'] is None:
                    LogE("[IGNORING] Amount not found","{0}".format(e))
                    exceptioncount = exceptioncount + 1
                pass

            # ACTION PRICE
            # derp = li.select('div.pricetag strong')
            # if derp is not None:
            #   derp = derp[0].get_text().strip()
            try:
                temp_data['action_price'] = li.select('div.pricetag strong')[0].get_text().strip()
            except (IndexError, TypeError) as e:
                try:
                    temp_data['action_price'] = li.select('img.visual')[1].get('alt').strip()
                except IndexError as e:
                    pass
                if temp_data['action_price'] is None:
                    LogE("[IGNORING] Action price not found","{0}".format(e))
                    exceptioncount = exceptioncount + 1
                pass

            # OLD PRICE
            try:
                temp_data['old_price'] = li.select('del')[0].get_text().strip()
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
                db.insert(temp_data)
                LogD("[{0}] ({1}) Fetched '{2}'".format(exceptioncount, count, temp_data['productname']))
            
            if failedcount > settings.maxFailedDiscounts:
                LogE("Skipping this supermarket, too much missing info.","More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
                LogI("Skipping this supermarket, too much missing info")
                LogI("More than {0} discounts missing too much info".format(settings.maxFailedDiscounts))
                return
    
    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} C1000 discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def test():
    #will define test here
    LogI("C1000 test")
