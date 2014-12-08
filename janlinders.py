import re
import requests
import bs4
import json

root_url = 'http://www.janlinders.nl'
index_url = root_url + '/acties/weekacties/'

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
}
 
def get_data():
    output = []
    print "Jan Linders Scraper\n"
    print "[Productname] - [Amount] - [Action price]"
    
    response = requests.get(index_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text)
    soup.encode('utf-8')

    category_divs = soup.find_all('div', class_=re.compile('dots_\d+'))

    for div in category_divs:
        div_items = div.findAll('div', { 'class' : 'hover_discount_product'})
        for actdiv in div_items:
            temp_data = {}
            temp_data['url'] = index_url
            try:
                temp_data['productname'] = actdiv.select('div.action b')[0].get_text() + " "
            except:
                temp_data['productname'] = ""

            temp_data['productname'] += actdiv.select('div.action h4')[0].get_text().replace('\n' , ' ')
            temp_data['duration'] = soup.select('div.date-small')[0].get_text()
            
            # Needs some work
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

            temp_data['image'] = root_url + actdiv.find('img').get('src')

            try:
                temp_data['action-price'] = actdiv.select('div.action div.regular_price span.big')[0].get_text() + "." + actdiv.select('div.action div.regular_price span.small')[0].get_text()
            except:
                temp_data['action-price'] = "Unknown"

            try:
                temp_data['action-price'] = actdiv.select('div.big')[0].get_text() + "." + actdiv.select('div.small')[1].get_text()
            except:
                pass

            try:
                temp_data['action-price'] = actdiv.select('div.regular_price div.big')[0].get_text() + "." + actdiv.select('div.regular_price div.small')[0].get_text()
            except:
                pass

            try:
                temp_data['action-price'] = actdiv.select('div.price div.big')[0].get_text() + "." + actdiv.select('div.price div.small')[0].get_text()
            except:
                pass

            try:
                temp_data['action-price'] = actdiv.select('div.action div.x_discount div.big')[0].get_text() + " " + actdiv.select('div.action div.x_discount div.small')[0].get_text()
            except:
                pass
            
            try:
                temp_data['old-price'] = actdiv.select('span.oldprice')[0].get_text()
            except:
                temp_data['old-price'] = "Unknown"

            if temp_data['old-price'] == "":
                temp_data['old-price'] = "Unknown"

            output.append(temp_data)
            print temp_data['productname'] + " - " + temp_data['amount'] + " - " + temp_data['action-price']

    with open('janlinders.json', 'w') as outfile:
        json.dump(output, outfile)
    #print output
 
if __name__ == '__main__':
    get_data()