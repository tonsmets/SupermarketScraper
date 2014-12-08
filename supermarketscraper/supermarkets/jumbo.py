import re
import requests
import bs4
import json

root_url = 'http://www.jumbosupermarkten.nl'
index_url = root_url + '/Homepage/Nu-in-de-winkel/acties/'
 
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}
 
def get_actie_page_urls():
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text)
    return [a.attrs.get('href') for a in soup.select('a[href^=/Homepage/Nu-in-de-winkel/acties/Product]')]
 
def get_actie_data(actie_page_url):
    actie_data = {}
    response = requests.get(root_url + actie_page_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')
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
 
def get_data():
    output = []
    print "Jumbo Scraper\n"
    print "[Productname] - [Amount] - [Action price]"
    actie_page_urls = get_actie_page_urls()
    for actie_page_url in actie_page_urls:
        single_output = get_actie_data(actie_page_url)
        output.append(single_output)
        print single_output['productname'] + " - " + single_output['amount'] + " - " + single_output['action-price']
    with open('jumbo.json', 'w') as outfile:
        json.dump(output, outfile)
 
if __name__ == '__main__':
    get_data()