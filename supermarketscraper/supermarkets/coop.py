import bs4
import requests
import json
import time
import sys
import re
import traceback
from util.logging import *
import util.settings as settings
import models.model as models
import demjson

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
    LogI("Done fetching {0} Coop discounts in {1}ms. {2} errors occured and ignored.\n".format(count, format(seconds, '.2f'), totalexceptions))

def meta():
    LogI("Fetching Coop metadata...")
    start_time = time.time() * 1000
    try:
        r = requests.get('http://www.coop.nl/Webcontrols/Winkels/StoresJSON.aspx', headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    temp = r.text.replace('var Markers=','')
    temp = re.sub("<!--.*?-->", "", temp)
    data = demjson.decode(temp)

    LogD("Parsed JSON")

    LogD("Amount of supermarkets: {0}".format(str(len(data))))
    for store in data:
        #print(store)
        tempMeta = models.metaModel.copy()
        tempMeta['supermarket'] = 'coop'

        try:
            tempMeta['superid'] = store['SEOLabel']
        except KeyError as e:
            LogE("[META] SuperID not found","{0}".format(e))
            pass
        
        try:
            tempMeta['name'] = store['StoreName']
        except KeyError as e:
            LogE("[META] Name not found","{0}".format(e))
            pass
        
        try:
            tempMeta['address'] = "{0} {1}, {2} {3}".format(store['Address'], store['AddressNumber'], store['PostalCode'], store['City'])
        except KeyError as e:
            LogE("[META] Address not found","{0}".format(e))
            pass
        
        try:        
            tempMeta['lat'] = store['y']
        except KeyError as e:
            LogE("[META] Latitude not found","{0}".format(e))
            pass
        
        try:        
            tempMeta['lon'] = store['x']
        except KeyError as e:
            LogE("[META] Longitude not found","{0}".format(e))
            pass
        
        try:
            tempMeta['phone'] = store['Phone']
        except KeyError as e:
            LogE("[META] Phone number not found","{0}".format(e))
            pass

        try:
            tempMeta['opening'] = []
            tempMeta['opening'].append({'dow':'monday', 'hours':store['OpenMo']})
            tempMeta['opening'].append({'dow':'tuesday', 'hours':store['OpenTu']})
            tempMeta['opening'].append({'dow':'wednesday', 'hours':store['OpenWe']})
            tempMeta['opening'].append({'dow':'thursday', 'hours':store['OpenTh']})
            tempMeta['opening'].append({'dow':'friday', 'hours':store['OpenFr']})
            tempMeta['opening'].append({'dow':'saturday', 'hours':store['OpenSa']})
            tempMeta['opening'].append({'dow':'sunday', 'hours':store['OpenSu']})
        except (IndexError, KeyError) as e:
            LogE("[META] Opening hours not found","{0}".format(e))
            pass

        try:
            tempMeta['services'] = []
            try:
                req = requests.get('http://www.coop.nl/supermarkten/{0}/{1}'.format(store['City'].lower(), store['SEOLabel']), headers=settings.headers)
            except requests.exceptions.ConnectionError as ce:
                LogE("[META] Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
                pass

            try:
                soup = bs4.BeautifulSoup(req.text)
                soup.encode('utf-8')
            except:
                LogE("[META] Unable to parse HTML","{0}".format(sys.exc_info()[0]))
                pass

            try:
                facilities = soup.select('div.facilitiesBlock ul li')
                for service in facilities:
                    tempMeta['services'].append(service.get_text().strip())
            except e:
                LogE("[META] Services not found","{0}".format(e))
            pass

        except (IndexError, KeyError) as e:
            LogE("[META] Services not found","{0}".format(e))
            pass

        LogD('Fetched metadata for "{0}"'.format(tempMeta['name']))
        db.insertMeta(tempMeta)
        #LogI(tempMeta)

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching Coop metadata in {0}ms".format(format(seconds, '.2f')))
 
def test():
    #will define test here
    LogI("Coop test")