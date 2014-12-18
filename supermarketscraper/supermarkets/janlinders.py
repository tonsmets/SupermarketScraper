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
    LogI("Fetching Jan Linders discounts...")
    start_time = time.time() * 1000

    root_url = 'http://www.janlinders.nl'
    index_url = root_url + '/acties/weekacties/'

    count = 0
    failedcount = 0
    totalexceptions = 0

    try:
        response = requests.get(index_url, headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    try:
        soup = bs4.BeautifulSoup(response.text, 'html5lib')
        soup.encode('utf-8')
    except:
        LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return

    category_divs = soup.find_all('div', class_=re.compile('dots_\d+'))

    for div in category_divs:
        div_items = div.findAll('div', { 'class' : 'hover_discount_product'})
        for actdiv in div_items:
            exceptioncount = 0
            temp_data = {}
            temp_data = models.defaultModel.copy()
            temp_data['supermarket'] = 'janlinders'
            temp_data['url'] = index_url

            if actdiv.select('div.action b'):
                temp_data['productname'] = actdiv.select('div.action b')[0].get_text() + " " + actdiv.select('div.action h4')[0].get_text().replace('\n' , ' ')
            else:
                try:
                    temp_data['productname'] = actdiv.select('div.action h4')[0].get_text().replace('\n' , ' ')
                except IndexError as e:
                    LogE("[IGNORING] Productname not found","{0}".format(e))
                    exceptioncount = exceptioncount + 1
                    pass

            try:
                temp_data['duration'] = soup.select('div.date-small')[0].get_text()
            except IndexError as e:
                LogE("[IGNORING] Duration not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass

            try:
                tempOldPrice = actdiv.select('.oldprice')[0].get_text()
                if tempOldPrice is not None and tempOldPrice != '' and tempOldPrice is not '':
                    temp_data['old_price'] = tempOldPrice
            except IndexError as e:
                LogE("[IGNORING] Old price not found","{0}".format(e))
                exceptioncount = exceptioncount + 1
                pass

            try:
                tempamount = actdiv.find('div', { 'class' : re.compile("^description")})
                for e in tempamount.findAll('h4'):
                    e.extract()
                for e in tempamount.findAll('b'):
                    e.extract()
                for e in tempamount.findAll('span'):
                    e.extract()
                for e in tempamount.findAll('div'):
                    e.extract()
                temp_data['amount'] = tempamount.get_text().replace('\n' , ' ')

                try:
                    temp_data['amount'] += ". " + actdiv.select('div.x_price_w_amount span.small')[0].get_text()
                except:
                    pass
            except:
                LogE("[IGNORING] Amount not found","{0}".format(sys.exc_info()[0]))
                exceptioncount = exceptioncount + 1
                pass

            try:
                temp_data['image'] = root_url + actdiv.find('img').get('src')
            except:
                LogE("[IGNORING] Image not found","{0}".format(sys.exc_info()[0]))
                exceptioncount = exceptioncount + 1
                pass

            # TODO
            try:
                temp_data['action_price'] = actdiv.select('div.action div.regular_price span.big')[0].get_text() + "." + actdiv.select('div.action div.regular_price span.small')[0].get_text()
            except:
                pass

            try:
                temp_data['action_price'] = actdiv.select('div.big')[0].get_text() + "." + actdiv.select('div.small')[1].get_text()
            except:
                pass

            try:
                temp_data['action_price'] = actdiv.select('div.regular_price div.big')[0].get_text() + "." + actdiv.select('div.regular_price div.small')[0].get_text()
            except:
                pass

            try:
                temp_data['action_price'] = actdiv.select('div.price div.big')[0].get_text() + "." + actdiv.select('div.price div.small')[0].get_text()
            except:
                pass

            try:
                temp_data['action_price'] = actdiv.select('div.action div.x_discount div.big')[0].get_text() + " " + actdiv.select('div.action div.x_discount div.small')[0].get_text()
            except:
                pass

            totalexceptions = totalexceptions + exceptioncount

            count = count + 1
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
    LogI("Done fetching {0} Jan Linders discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def test():
    #will define test here
    LogI("Jan Linders test")
