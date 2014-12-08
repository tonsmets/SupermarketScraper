import re
import requests
import bs4
import json

root_url = 'http://www.c1000.nl/'
index_url = root_url + 'aanbiedingen'

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}
 
def get_data():
    output = []
    print "C1000 Scraper\n"
    print "[Productname] - [Amount] - [Action price]"
    
    response = requests.get(index_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    category_divs = soup.findAll('div', id=re.compile("^content_0_contentrij1_0_weekAanbiedingen_listViewCategorieen_"))
    for div in category_divs:
        list_items = div.findAll('li')
        for li in list_items:
            temp_data = {}
            temp_data['url'] = index_url
            temp_data['productname'] = li.find('h2').get_text()
            temp_data['duration'] = re.sub(r'[\t\r\n]', '', soup.find('a', {'id' : 'content_0_contentrij1_0_linkTabHuidigeWeek'}).get_text()).strip().replace('                     ', ' ')
            temp_data['description'] = re.sub(r'[\t\r\n]', '', li.select('div.product_details p')[0].get_text())
            temp_data['image'] = root_url + li.find('img').get('src')
            try:
                temp_data['amount'] = li.select('div.pricetag em')[0].get_text()
            except:
                temp_data['amount'] = "Unknown"

            try:
                temp_data['action-price'] = li.select('div.pricetag strong')[0].get_text()
            except:
                temp_data['action-price'] = "Unknown"

            try:
                temp_data['action-price'] = li.select('img.visual')[1].get('alt')
            except:
                pass

            try:
                temp_data['old-price'] = li.select('del')[0].get_text()
            except:
                temp_data['old-price'] = "Unknown"

            output.append(temp_data)

            print temp_data['productname'] + " - " + temp_data['amount'] + " - " + temp_data['action-price']

    with open('c1000.json', 'w') as outfile:
        json.dump(output, outfile)
    #print output
 
if __name__ == '__main__':
    get_data()