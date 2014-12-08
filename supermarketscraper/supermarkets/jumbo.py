import bs4
import requests
import json
import time

import util.database as database
collection = database.collection

root_url = 'http://www.jumbosupermarkten.nl'
index_url = root_url + '/Homepage/Nu-in-de-winkel/acties/'
 
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}

count = 0
 
def get_actie_page_urls():
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text)
    return [a.attrs.get('href') for a in soup.select('a[href^=/Homepage/Nu-in-de-winkel/acties/Product]')]
 
def get_actie_data(actie_page_url):
    actie_data = {}
    response = requests.get(root_url + actie_page_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')
    actie_data['supermarket'] = 'jumbo'
    actie_data['url'] = root_url + actie_page_url
    actie_data['productname'] = soup.select('div.header h1')[0].get_text().strip()
    actie_data['duration'] = soup.select('div.header em.subtitle')[0].get_text().strip()
    actie_data['amount'] = soup.select('div.product-detail p.description')[0].get_text().strip()
    actie_data['image'] = root_url + soup.select('img.photo')[0].get('src')

    try:
        actie_data['action-price'] = soup.select('div.content-box em.single-value')[0].get_text().strip().replace(",",".")   
    except:
        actie_data['action-price'] = "Unknown"

    try:
        actie_data['action-price'] = soup.select('em.discount-type-alt')[0].get_text().strip()
    except:
        pass

    try:
        actie_data['action-price'] = soup.select('div.content-box em.text-subtext strong')[0].get_text().strip().replace(",",".") + soup.select('div.content-box em.text-subtext strong span')[0].get_text().strip().replace(",",".")  
    except:
        pass

    try:
        actie_data['action-price'] = soup.select('div.content-box em.text-pretext strong')[0].get_text().strip().replace(",",".")  
    except:
        pass

    try:
        actie_data['action-price'] = soup.select('div.content-box  p.action-price')[0].get_text().strip().replace("Actieprijs ", "").replace(",",".")   
    except:
        pass

    try:
        actie_data['old-price'] = soup.select('div.content-box p.pricing')[0].get_text().strip().replace("Normaal ", "")
    except:
        actie_data['old-price'] = "Unknown"

    return actie_data
 
def fetch():
    global count
    print("# Fetching Jumbo discounts...")
    start_time = time.time() * 1000
    actie_page_urls = get_actie_page_urls()
    for actie_page_url in actie_page_urls:
        superdata = get_actie_data(actie_page_url) 
        count = count + 1
        collection.insert(superdata)

    seconds = (time.time() * 1000) - start_time
    print("# Done fetching {0} Jumbo discounts in {1}ms.\n".format(count, format(seconds, '.2f')))

def test():
    #will define test here
    print("Jumbo test")
 