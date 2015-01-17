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
# 259   6 voor
# 260   <empty>
# 261   <none>
# 262   Per bak
# 263   Per blik
# 264   Per doos
# 265   Per set
# 267   Per schaal
# 291   Halve vlaai
# 292   Per paar
# 293   Per pack
# 294   Per pot
# 295   Zoek uit
# 296   100 gram
# 297   250 gram
# 298   600 gram
# 299   800 gram
# 300   2,5 kilo
# 301   5 kilo
# 302   750 gram

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
import demjson

import util.database as db

root_url = 'http://www.dekamarkt.nl/'
index_url = root_url + 'aanbiedingen'

count = 0
failedcount = 0
totalexceptions = 0

duration = ""
 
def get_actie_data(actie_page_url):
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

    global count
    global failedcount
    global totalexceptions
    global duration

    category_divs = soup.findAll('div', {'class':'aanbieding'})
    for div in category_divs:
        exceptioncount = 0
        temp_data = {}
        temp_data = models.defaultModel.copy()
        temp_data['supermarket'] = 'deka'
        temp_data['url'] = actie_page_url
        try:
            temp_data['productname'] = div.find('h2').get_text()
        except:
            LogE("[IGNORING] Productname not found","{0}".format(sys.exc_info()[0]))
            exceptioncount = exceptioncount + 1
            pass

        try:
            temp_data['duration'] = ''
        except:
            LogE("[IGNORING] Duration not found","{0}".format(sys.exc_info()[0]))
            exceptioncount = exceptioncount + 1
            pass

        try:
            temp_data['description'] = div.select('div.text')[0].get_text()
        except IndexError as e:
            LogE("[IGNORING] Description not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        try:
            temp_data['image'] = root_url + div.find('img').get('src')
        except:
            LogE("[IGNORING] Image not found","{0}".format(sys.exc_info()[0]))
            exceptioncount = exceptioncount + 1
            pass

        try:
            temp_data['amount'] = getAmount(div.find('div', {'class' : re.compile("tag")}).get('class')[1].replace('tag', ''))
        except:
            LogE("[IGNORING] Amount not found","{0}".format(sys.exc_info()[0]))
            exceptioncount = exceptioncount + 1
            pass
        
        try:
            temp_data['action_price'] = div.select('span.current span.whole')[0].get_text() + div.select('span.current span.part')[0].get_text()
        except IndexError as e:
            LogE("[IGNORING] Action price not found","{0}".format(e))
            exceptioncount = exceptioncount + 1
            pass

        try:
            temp_data['old_price'] = div.select('span.old span.whole')[0].get_text() + div.select('span.old span.part')[0].get_text()
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

def fetch():
    LogI("Fetching Deka discounts...")
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

    urls = soup.find('div', {'class':'paging'})

    for e in urls.findAll('a', {'class': 'last'}):
        e.extract()

    duration = soup.select('div.aanbiedingenData')[0].get_text().replace("Aanbieding geldig van ","")
    
    actie_page_urls = [a.attrs.get('href') for a in soup.select('a[href^=https://www.dekamarkt.nl/aanbiedingen?]')]

    global count
    global totalexceptions

    for actie_page_url in actie_page_urls:
        single_output = get_actie_data(actie_page_url)

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching {0} Deka discounts in {1}ms. {2} errors occured and ignored (mostly missing old price).\n".format(count, format(seconds, '.2f'), totalexceptions))

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
    elif tag == '259':
        return "6 voor"
    elif tag == '260':
        return ""
    elif tag == '261':
        return ""
    elif tag == '262':
        return "Per bak"
    elif tag == '263':
        return "Per blik"
    elif tag == '264':
        return "Per doos"
    elif tag == '265':
        return "Per set"
    elif tag == '267':
        return "Per schaal"
    elif tag == '291':
        return "Halve vlaai"
    elif tag == '292':
        return "Per paar"
    elif tag == '293':
        return "Per pack"
    elif tag == '294':
        return "Per pot"
    elif tag == '295':
        return "Zoek uit"
    elif tag == '296':
        return "100 gram"
    elif tag == '297':
        return "250 gram"
    elif tag == '298':
        return "600 gram"
    elif tag == '299':
        return "800 gram"
    elif tag == '300':
        return "2,5 kilo"
    elif tag == '301':
        return "5 kilo"
    elif tag == '302':
        return "750 gram"
    else:
        LogE("No amount found in if-list","For tag: {0}".format(tag))
        pass

def meta():
    LogI("Fetching Deka metadata...")
    start_time = time.time() * 1000
    try:
        r = requests.get('https://www.dekamarkt.nl/winkels#|0|0|', headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    try:
        soup = bs4.BeautifulSoup(r.text, 'html5lib')
        soup.encode('utf-8')
    except:
        LogE("[META] Unable to parse HTML","{0}".format(sys.exc_info()[0]))
        return

    try:
        origdata = soup.select('div.contentWrapper script')[0].get_text().replace(';Filialen.init(markers,types,departments);','').replace('var markers=','')
    except IndexError as e:
        LogE("[META] Unable to find data","{0}".format(e))
        return

    #print(data)
    data = re.sub("(\;var\s.+\=\[\{.*\}\])","",origdata)
    data = demjson.decode(data)

    m = re.search('(var\sdepartments\=\[\{.*\}\])', origdata)
    if m:
        found = m.group(1).replace('var departments=','')
        departments = json.loads(found)
        print(departments)

    LogD("Amount of supermarkets: {0}".format(str(len(data))))
    for store in data:
        tempMeta = models.metaModel.copy()
        tempMeta['supermarket'] = 'deka'
        tempMeta['superid'] = store['ID']
        
        try:
            tempMeta['name'] = "Deka {0} {1}".format(store['address'].split(' ')[0], store['city'])
        except KeyError as e:
            LogE("[META] Name not found","{0}".format(e))
            pass
        
        try:
            tempMeta['address'] = "{0}, {1} {2}".format(store['address'], store['zip'], store['city'])
        except KeyError as e:
            LogE("[META] Address not found","{0}".format(e))
            pass
        
        try:        
            tempMeta['lat'] = store['lat']
        except KeyError as e:
            LogE("[META] Latitude not found","{0}".format(e))
            pass
        
        try:        
            tempMeta['lon'] = store['lng']
        except KeyError as e:
            LogE("[META] Longitude not found","{0}".format(e))
            pass
        
        try:
            tempMeta['phone'] = store['phone']
        except KeyError as e:
            LogE("[META] Phone number not found","{0}".format(e))
            pass

        try:
            mapping = [ ('1', 'monday'), ('2', 'tuesday'), ('3', 'wednesday'), ('4', 'thursday'), ('5', 'friday'), ('6', 'saturday'), ('0', 'sunday') ]
            #mapping = {'Maandag':'monday', 'Dinsdag':'tuesday', 'Woensdag':'wednesday', 'Donderdag':'thursday', 'Vrijdag':'friday', 'Zaterdag':'saturday', 'Zondag':'sunday'}
            tempMeta['opening'] = []
            days = store['open']
            for day in days:
                dow = str(day['dayOfWeek'])
                for k, v in mapping:
                    dow = dow.replace(k, v)
                if '00:00' in day['open'] and '00:00' in day['close']:
                    hours = 'Gesloten'
                else:
                    hours = "{0} - {1}".format(day['open'], day['close'])
                tempMeta['opening'].append({'dow':dow, 'hours': hours})

            tempMeta['opening'].pop(1)
            
        except (IndexError, KeyError) as e:
            LogE("[META] Opening hours not found","{0}".format(e))
            pass

        try:
            tempMeta['services'] = []         
            services = store['departments']
            for service in services:
                name = ""
                for i in range(0, len(departments)):
                    if departments[i]['ID'] == service:
                        name = departments[i]['name']
                tempMeta['services'].append({'service':name})
        except (IndexError, KeyError) as e:
            LogE("[META] Services not found","{0}".format(e))
            pass

        LogD('Fetched metadata for "{0}"'.format(tempMeta['name']))
        db.insertMeta(tempMeta)
        #LogI(tempMeta)

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching Deka metadata in {0}ms".format(format(seconds, '.2f')))

def test():
    #will define test here
    LogI("Deka test")