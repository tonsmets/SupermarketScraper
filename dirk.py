import re
import requests
import bs4
import json
import cssutils

root_url = 'http://www.dirk.nl/'
index_url = root_url + 'aanbiedingen'

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}
 
def get_actie_page_urls():
    response = requests.get(index_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    return [a.attrs.get('href') for a in soup.select('div.rightside div.body p a[href^=aanbiedingen/]')]

 
def get_actie_data(actie_page_url):
    actie_data = {}
    response = requests.get(root_url + actie_page_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    actie_data['url'] = root_url + actie_page_url
    actie_data['productname'] = soup.find('h2').get_text()
    actie_data['duration'] = soup.select('div.fromTill')[0].get_text().strip()
    actie_data['amount'] = soup.select('div.subtitle')[0].get_text().strip()

    div_style = soup.find('div', {'class':'image'})['style']
    style = cssutils.parseStyle(div_style)
    url = style['background-image']
    url = url.replace('url(', '').replace(')', '')
    actie_data['image'] = root_url + url

    try:
        actie_data['action-price'] = soup.select('div.star')[0].get('title').strip().replace(u"\u20AC ","").replace(",",".")
    except:
        actie_data['action-price'] = "Unknown"

    try:
        actie_data['old-price'] = soup.select('span.stripe')[0].get_text()
    except:
        actie_data['old-price'] = "Unknown"

    return actie_data
 
def get_data():
    output = []
    print "Dirk Scraper\n"
    actie_page_urls = get_actie_page_urls()

    for actie_page_url in actie_page_urls:
        single_output = get_actie_data(actie_page_url)
        output.append(single_output)
        print single_output['productname'] + " - " + single_output['amount'] + " - " + single_output['action-price']
    with open('dirk.json', 'w') as outfile:
        json.dump(output, outfile)
 
if __name__ == '__main__':
    get_data()