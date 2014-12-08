import re
import requests
import bs4
import json

root_url = 'http://www.ah.nl'
index_url = root_url + '/bonus'

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}

def get_data():
    output = []
    print "AH Scraper\n"
    print "[Productname] - [Amount] - [Action price]"
    
    response = requests.get(index_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    #bonus_products = soup.findAll('a', {'data-class':'product'})
    bonus_products = soup.findAll(attrs={'data-class': 'product'})
    for bonus in bonus_products:
        temp_data = {}
        try:
            temp_data['url'] = "http://www.ah.nl" + bonus.select('div.detail a')[0].get('href')
        except:
            pass
        try:
            temp_data['url'] = "http://www.ah.nl" + bonus.get('href')
        except:
            pass
        temp_data['productname'] = bonus.select('div.detail h2')[0].get_text().strip()

        temp_data['duration'] = soup.select('div.columns p.header-bar__term')[0].get_text()

        temp_data['image'] = bonus.select('div.image img')[0].get('data-original')

        try:
            temp_data['amount'] = bonus.select('div.image p.unit')[0].get_text().strip()
        except:
            temp_data['amount'] = "Unknown"

        if temp_data['amount'] == "":
            temp_data['amount'] = "Unknown"

        temp_data['bonus'] = bonus.select('div.shield')[0].get_text().strip()
        temp_data['action-price'] = bonus.select('p.price ins')[0].get_text()
        try:
            temp_data['old-price'] = bonus.select('p.price del')[0].get_text()
        except:
            temp_data['old-price'] = "Unknown"

        output.append(temp_data)

        print temp_data['productname'] + " - " + temp_data['amount'] + " - " + temp_data['action-price']

    with open('ah.json', 'w') as outfile:
        json.dump(output, outfile)
    #print output
 
if __name__ == '__main__':
    get_data()