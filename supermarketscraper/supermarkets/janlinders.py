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

            if actdiv.select('div.action div.regular_price span.big') and actdiv.select('div.action div.regular_price span.small'):
                try:
                    temp_data['action_price'] = actdiv.select('div.action div.regular_price span.big')[0].get_text() + "." + actdiv.select('div.action div.regular_price span.small')[0].get_text()
                except:
                    LogE("[IGNORING] Action price not found","None")
                    exceptioncount = exceptioncount + 1
                    pass
            elif actdiv.select('div.x_price_w_amount div.small') and actdiv.select('div.x_price_w_amount div.small') and actdiv.select('div.x_price_w_amount div.big'):
                try:
                    temp_data['action_price'] = actdiv.select('div.x_price_w_amount div.small')[0].get_text() + " " + actdiv.select('div.x_price_w_amount div.big')[0].get_text() + "." + actdiv.select('div.x_price_w_amount div.small')[1].get_text()
                except:
                    LogE("[IGNORING] Action price not found","None")
                    exceptioncount = exceptioncount + 1
                    pass
            elif actdiv.select('div.x_free div.big') and actdiv.select('div.x_free div.small'):
                try:
                    temp_data['action_price'] = ' '.join(actdiv.select('div.x_free div.big')[0].get_text().strip().split()) + " " + ' '.join(actdiv.select('div.x_free div.small')[0].get_text().strip().split())
                except:
                    LogE("[IGNORING] Action price not found","None")
                    exceptioncount = exceptioncount + 1
                    pass
            elif actdiv.select('div.regular_price div.big') and actdiv.select('div.regular_price div.small'):
                try:
                    temp_data['action_price'] = actdiv.select('div.regular_price div.big')[0].get_text() + "." + actdiv.select('div.regular_price div.small')[0].get_text()
                except:
                    LogE("[IGNORING] Action price not found","None")
                    exceptioncount = exceptioncount + 1
                    pass
            #elif actdiv.select('div.price div.big') and actdiv.select('div.price div.small'):
                #temp_data['action_price'] = actdiv.select('div.price div.big')[0].get_text() + "." + actdiv.select('div.price div.small')[0].get_text()
            
            elif actdiv.select('div.action div.x_discount div.big') and actdiv.select('div.action div.x_discount div.small'):
                try:
                    temp_data['action_price'] = ' '.join(actdiv.select('div.action div.x_discount div.big')[0].get_text().strip().split()) + " " + actdiv.select('div.action div.x_discount div.small')[0].get_text()
                except:
                    LogE("[IGNORING] Action price not found","None")
                    exceptioncount = exceptioncount + 1
                    pass
            elif actdiv.select('div.x_get_for div.small'):
                try:
                    temp_data['action_price'] = ' '.join(actdiv.select('div.x_get_for div.small')[0].get_text().strip().split()) + ", " + actdiv.select('div.x_get_for div.small')[1].get_text().strip()
                except:
                    LogE("[IGNORING] Action price not found","None")
                    exceptioncount = exceptioncount + 1
                    pass
            elif actdiv.select('div.x_half_price div.small'):
                try:
                    temp_data['action_price'] = ' '.join(actdiv.select('div.x_half_price div.small')[0].get_text().strip().split()) + " " + actdiv.select('div.x_half_price div.small')[1].get_text().strip()
                except:
                    LogE("[IGNORING] Action price not found","None")
                    exceptioncount = exceptioncount + 1
                    pass
            else:
                LogE("[IGNORING] Action price not found","None")
                exceptioncount = exceptioncount + 1
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

def meta():
    LogI("Fetching Jan Linders metadata...")
    start_time = time.time() * 1000
    try:
        r = requests.get('http://www.janlinders.nl/ajax_requests/postcode/&postcode=&plaats=', headers=settings.headers)
    except requests.exceptions.ConnectionError as ce:
        LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
        return

    data = json.loads(r.text)
    data.pop(0)
    #print(data)
    LogD("Amount of supermarkets: {0}".format(str(len(data))))
    for store in data:
        tempMeta = models.metaModel.copy()
        tempMeta['supermarket'] = 'janlinders'
        tempMeta['superid'] = store['entry_id']
        
        try:
            temp = store['straat_huisnummer'].split(' ')
            temp.pop(-1)
            temp = ' '.join(temp)
            tempMeta['name'] = "Jan Linders {0} {1}".format(temp, store['plaats'])
        except KeyError as e:
            LogE("[META] Name not found","{0}".format(e))
            pass
        
        try:
            tempMeta['address'] = "{0}, {1} {2}".format(store['straat_huisnummer'], store['postcode'], store['plaats'])
        except KeyError as e:
            LogE("[META] Address not found","{0}".format(e))
            pass
        
        try:        
            tempMeta['lat'] = store['latitude']
        except KeyError as e:
            LogE("[META] Latitude not found","{0}".format(e))
            pass
        
        try:        
            tempMeta['lon'] = store['longitude']
        except KeyError as e:
            LogE("[META] Longitude not found","{0}".format(e))
            pass
        
        try:
            tempMeta['phone'] = store['telefoonnummer']
        except KeyError as e:
            LogE("[META] Phone number not found","{0}".format(e))
            pass

        try:
            #mapping = [ ('Maandag', 'monday'), ('Dinsdag', 'tuesday'), ('Woensdag', 'wednesday'), ('Donderdag', 'thursday'), ('Vrijdag', 'friday'), ('Zaterdag', 'saturday'), ('Zondag', 'sunday') ]
            #mapping = {'Maandag':'monday', 'Dinsdag':'tuesday', 'Woensdag':'wednesday', 'Donderdag':'thursday', 'Vrijdag':'friday', 'Zaterdag':'saturday', 'Zondag':'sunday'}
            tempMeta['opening'] = []
            tempMeta['opening'].append({'dow':'monday', 'hours': store['openingstijden_op_maandag']})
            tempMeta['opening'].append({'dow':'tuesday', 'hours': store['openingstijden_op_dinsdag']})
            tempMeta['opening'].append({'dow':'wednesday', 'hours': store['openingstijden_op_woensdag']})
            tempMeta['opening'].append({'dow':'thursday', 'hours': store['openingstijden_op_donderdag']})
            tempMeta['opening'].append({'dow':'friday', 'hours': store['openingstijden_op_vrijdag']})
            tempMeta['opening'].append({'dow':'saturday', 'hours': store['openingstijden_op_zaterdag']})
            if (store['openingstijden_op_zondag'] is None) or (store['openingstijden_op_zondag'] == ""):
                tempMeta['opening'].append({'dow':'sunday', 'hours': 'Gesloten'})
            else:
                tempMeta['opening'].append({'dow':'sunday', 'hours': store['openingstijden_op_zondag']})
        except (IndexError, KeyError) as e:
            LogE("[META] Opening hours not found","{0}".format(e))
            pass

        try:
            try:
                r = requests.get('http://www.janlinders.nl/filialen/gegevens/' + store['url'], headers=settings.headers)
            except requests.exceptions.ConnectionError as ce:
                LogE("Failed to connect to '{0}'".format(index_url),"{0}".format(ce))
                pass

            try:
                storesoup = bs4.BeautifulSoup(r.text, 'html5lib')
                storesoup.encode('utf-8')
            except:
                LogE("Unable to parse HTML","{0}".format(sys.exc_info()[0]))
                pass

            tempMeta['services'] = []
            rows = storesoup.find(text=re.compile('Service')).parent.parent.select('img.service_icon')
            for service in rows:
                tempMeta['services'].append({'service':service.get('alt')})
        except (IndexError, KeyError) as e:
            LogE("[META] Services not found","{0}".format(e))
            pass

        LogD('Fetched metadata for "{0}"'.format(tempMeta['name']))
        db.insertMeta(tempMeta)
        #LogI(tempMeta)

    seconds = (time.time() * 1000) - start_time
    LogI("Done fetching Jan Linders metadata in {0}ms".format(format(seconds, '.2f')))

def test():
    #will define test here
    LogI("Jan Linders test")
