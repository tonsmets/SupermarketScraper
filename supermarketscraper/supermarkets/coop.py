import re
import requests
import bs4
import json

root_url = 'http://www.coop.nl'
index_url = root_url + '/aanbiedingen'

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}
 
def get_data():
    output = []
    print "Coop Scraper\n"
    print "[Productname] - [Amount] - [Action price]"
    
    response = requests.get(index_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    category_divs = soup.findAll('div', {'class':'deal'})
    for div in category_divs:
        temp_data = {}
        temp_data['url'] = index_url
        temp_data['productname'] = div.find('h3').get_text()
        temp_data['duration'] = soup.select('div#ctl00_ctl00_ContentPlaceHolderMain_cpLeftAndContent_Header2_divTextLink div.periode strong')[0].get_text() + " t/m " + soup.select('div#ctl00_ctl00_ContentPlaceHolderMain_cpLeftAndContent_Header2_divTextLink div.periode strong')[1].get_text()
        temp_data['image'] = root_url + div.find('img').get('src')
        try:
            temp_data['description'] = div.select('div.deal-info ul li')[0].get_text()
        except:
            temp_data['description'] = "Unknown"

        try:
            temp_data['amount'] = div.select('div.deal-label')[0].get_text()
        except:
            temp_data['amount'] = "Unknown"

        try:
            temp_data['action-price'] = div.select('span.deal-euros')[0].get_text()
        except:
            temp_data['action-price'] = "Unknown"

        try:
            temp = div.select('div.i50procentkorting')[0].get_text()
            temp_data['action-price'] = "50% korting"
        except:
            pass

        try:
            temp = div.select('div.i25procentkorting')[0].get_text()
            temp_data['action-price'] = "25% korting"
        except:
            pass

        output.append(temp_data)

        print temp_data['productname'] + " - " + temp_data['amount'] + " - " + temp_data['action-price']

    with open('coop.json', 'w') as outfile:
        json.dump(output, outfile)
    #print output
 
if __name__ == '__main__':
    get_data()