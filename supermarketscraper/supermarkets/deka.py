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
# 259   ???
# 260   <empty>
# 261   ???
# 262   Per bak
# 263   Per blik
# 264   Per doos
# 265   Per set

import re
import requests
import bs4
import json

root_url = 'http://www.dekamarkt.nl/'
index_url = root_url + 'aanbiedingen'
 
output = []

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}
 
def get_actie_page_urls():
    response = requests.get(index_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    urls = soup.find('div', {'class':'paging'})
    for e in urls.findAll('a', {'class': 'last'}):
                e.extract()
    return [a.attrs.get('href') for a in soup.select('a[href^=https://www.dekamarkt.nl/aanbiedingen?]')]
 
def get_actie_data(actie_page_url):
    response = requests.get(actie_page_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    category_divs = soup.findAll('div', {'class':'aanbieding'})
    for div in category_divs:
        temp_data = {}
        temp_data['url'] = actie_page_url
        temp_data['productname'] = div.find('h2').get_text()
        #temp_data['duration'] = re.sub(r'[\t\r\n]', '', soup.find('a', {'id' : 'content_0_contentrij1_0_linkTabHuidigeWeek'}).get_text()).strip().replace('                     ', ' ')
        temp_data['description'] = div.select('div.text')[0].get_text()
        temp_data['image'] = root_url + div.find('img').get('src')

        temp_data['amount'] = getAmount(div.find('div', {'class' : re.compile("tag")}).get('class')[1].replace('tag', ''))
        
        try:
            temp_data['action-price'] = div.select('span.current span.whole')[0].get_text() + div.select('span.current span.part')[0].get_text()
        except:
            temp_data['action-price'] = "Unknown"

        try:
            temp_data['old-price'] = div.select('span.old span.whole')[0].get_text() + div.select('span.old span.part')[0].get_text()
        except:
            temp_data['old-price'] = "Unknown"

        output.append(temp_data)

        print temp_data['productname'] + " - " + temp_data['amount'] + " - " + temp_data['action-price']
 
def get_data():
    print "Deka Scraper\n"
    actie_page_urls = get_actie_page_urls()
    for actie_page_url in actie_page_urls:
        single_output = get_actie_data(actie_page_url)

    with open('deka.json', 'w') as outfile:
        json.dump(output, outfile)

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
    elif tag == '262':
        return "Per bak"
    elif tag == '263':
        return "Per blik"
    elif tag == '264':
        return "Per doos"
    elif tag == '265':
        return "Per set"
    else:
        return "Unknown"
 
if __name__ == '__main__':
    get_data()