from bs4 import BeautifulSoup
import requests
import os
import json
from flask import Flask, jsonify, request
from forex_python.converter import CurrencyRates

app = Flask(__name__)

proxies = {
#TODO: ISRAELI IP ADDRESSES
'http' : '',
'https' : '',

}

@app.route('/calculate', methods=['POST'])
def get_prices():
    if(str(request.form['amazon_url']).startswith('https://www.amazon.com')):
        return amazon_us(True,"",request.form['amazon_url'],True)
    elif(str(request.form['amazon_url']).startswith('https://www.amazon.de')):
        return amazon_ger(True,"",request.form['amazon_url'],True)
    elif(str(request.form['amazon_url']).startswith('https://www.amazon.it')):
        return amazon_it(True,"",request.form['amazon_url'],True)

s = requests.Session()
# so Amazon doesn't think I'm a bot
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
# s.proxies = proxies


def build_json(us, ger, it):
    c = CurrencyRates()
    amazon_us_usd = us
    if(not us == "error" and not us == False):
        amazon_us_ils = round(c.convert('USD', 'ILS', us), 2)
    amazon_ger_eur = ger
    if(not ger == "error" and not ger == False):
        amazon_ger_ils = round(c.convert('EUR', 'ILS', ger),2)
    amazon_it_eur = it
    if(not it == "error" and not us == False):
        amazon_it_ils = round(c.convert('EUR', 'ILS', it),2)

    j = json.dumps({
    'amazon_us':{'usd': amazon_us_usd, 'ils': amazon_us_ils},
    'amazon_ger':{'eur': amazon_ger_eur, 'ils': amazon_ger_ils},
    'amazon_it':{'eur': amazon_it_eur, 'ils': amazon_it_ils}

    })

    return j

    # print(str(amazon_us_usd) + "$ = " + str(amazon_us_ils) +" "+str(amazon_ger_eur)+"EUR = " + str(amazon_ger_ils) +" "+str(amazon_it_eur)+"EUR = " + str(amazon_it_ils))



def substract(a, b):
    return "".join(a.rsplit(b))



def amazon_us(from_url, asin, prod_url = "", is_first = False):

    is_error = False
    if from_url:
        amazon_c = s.get("https://www.amazon.com/")
        if(not prod_url.startswith("https://www.amazon")):
            print("Please enter a valid Amazon URL.")
            return "InvalidURL"
        price_response = s.get(prod_url)
        price_soup = BeautifulSoup(price_response.content, features="html.parser")
        # with open('test.html', 'w') as file:
        #     file.write(str(price_soup.encode("utf-8")))
        product_asin = price_soup.find("input", {"id": "ASIN"})['value']
        product_name = price_soup.find("span", {"id":"productTitle"}).text
        product_name = substract(product_name, "\n")
        price_span = price_soup.find("span", {"id":"priceblock_ourprice"})
        if(price_span == None):
            if(is_first == False):
                print (product_name + "Cannot be shipped to Israel from US")
                is_shipping = False
            else:
                print("Whoops! Something went wrong. Please try again later.")
                is_error = True
        else:
            price = price_span.text
            price = substract(price, "$")
            price = substract(price, "\n")
            if(not "." in price):
                price = float(price) / 100
            price = float(price)
        try:

            delivery_message = price_soup.find("div", {"id" : "delivery-message"}).text
            if "ships to Israel" in delivery_message or "AmazonGlobal Standard Shipping at checkout" in delivery_message:
                print(product_name + " from US ships to Israel and costs: " + str(price))
                is_shipping = True

            else:
                print(product_name + " from US doesn't ship to Israel")
                is_shipping = False

        except AttributeError:
            if(is_first):
                #this is the first func, user didnt pick an attr
                os.system('cls')
                print ("Whoops! Something went wrong. Please try again later.")
                is_error = True
            else:
                #product doesnt ship to israel
                if(not is_shipping):
                    print(product_name + " from US doesn't ship to Israel")
                    is_shipping = False

        if(is_error):
            us = "error"
        elif (is_shipping):
            us = price
        elif(not is_shipping):
            us = False
        if(is_first):
            ger = amazon_ger(False, product_asin)
            it = amazon_it(False, product_asin)
            print(build_json(us,ger,it))
            return build_json(us,ger,it)
        else:
            return us

    else:
        asin_r = s.get("https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + asin + "&rh=i%3Aaps%2Ck%3AB0722DMYTN")
        asin_soup = BeautifulSoup(asin_r.content, features="html.parser")
        first_product = asin_soup.find("li", {"id" : "result_0"})
        if(first_product == None or not ("/dp/" + asin) in first_product.findAll("a")[0]['href']):
            print("Item doesn't exist in this (US) store")
            return False
        else:
            first_asin = first_product['data-asin']
            product_name = first_product.find("h2", {"class":"a-size-medium"})['data-attribute']
            product_name = substract(product_name, "\n")
            first_href = first_product.findAll("a")[0]['href']
            print(product_name + " found in the (US) store: " + first_href)
        return amazon_us(True, "", first_href)


#end amazon us

def amazon_ger(from_url, asin, prod_url ="", is_first = False):

    is_error = False
    if from_url:
        amazon_c = s.get("https://www.amazon.com/")
        if(not prod_url.startswith("https://www.amazon")):
            print("Please enter a valid Amazon URL.")
            return "InvalidURL"
        price_response = s.get(prod_url)
        price_soup = BeautifulSoup(price_response.content, features="html.parser")
        # with open('test.html', 'w') as file:
        #     file.write(str(price_soup.encode("utf-8")))
        product_asin = price_soup.find("input", {"id": "ASIN"})['value']
        product_name = price_soup.find("span", {"id":"productTitle"}).text
        product_name = substract(product_name, "\n")
        price_span = price_soup.find("span", {"id":"priceblock_ourprice"})
        if(price_span == None):
            if(is_first == False):
                print(product_name + " Cannot be shipped to Israel from GERMANY")
                is_shipping = False
            else:

                print ("Whoops! Something went wrong. Please try again later.")
                is_error = True
        else:
            price = price_span.text
            price = substract(price, "EUR ")
            price = price.replace(",", ".")
            price = substract(price, "\n")
            price = float(price)

        try:
            delivery_message = price_soup.find("div", {"id" : "ddmDeliveryMessage"}).text
            if "Dieser Artikel kann nach Israel geliefert werden" in delivery_message:
                print(product_name + " from GERMANY ships to Israel and costs: " + str(price))
                is_shipping = True

            else:
                print(product_name + " from GERMANY doesn't ship to Israel")
                is_shipping = False

        except AttributeError:

            if(is_first):
                #this is the first func, user didnt choose an attribute
                os.system('cls')
                print ("Whoops! Something went wrong. Please try again later.")
                is_error = True
            else:
                #this isnt a first func. product doesnt ship to israel
                if(not is_shipping):
                    print(product_name + " from GERMANY doesn't ship to Israel")
                    is_shipping = False

        if(is_error):
            ger = "error"
        elif (is_shipping):
            ger = float(price)
        elif(not is_shipping):
            ger = False
        if(is_first):
            us = amazon_us(False, product_asin)
            it = amazon_it(False, product_asin)
            return build_json(us,ger,it)
        else:
            return ger



    else:
        asin_r = s.get("https://www.amazon.de/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + asin + "&rh=i%3Aaps%2Ck%3AB0722DMYTN")
        asin_soup = BeautifulSoup(asin_r.content, features="html.parser")
        first_product = asin_soup.find("li", {"id" : "result_0"})
        if(first_product == None or not ("/dp/" + asin) in first_product.findAll("a")[0]['href']):
            print("Item doesn't exist in this (Germany) store")
            return False
        else:
            first_asin = first_product['data-asin']
            product_name = first_product.find("h2", {"class":"a-size-medium"})['data-attribute']
            product_name = substract(product_name, "\n")
            first_href = first_product.findAll("a")[0]['href']
            print(product_name + " found in the (Germany) store: " + first_href)
        return amazon_ger(True, "", first_href)

        #end amazon_ger

def amazon_it(from_url, asin, prod_url = "", is_first = False):
    is_error = False
    if from_url:
        amazon_c = s.get("https://www.amazon.com/")
        if(not prod_url.startswith("https://www.amazon")):
            print("Please enter a valid Amazon URL.")
            return "InvalidURL"
        price_response = s.get(prod_url)
        price_soup = BeautifulSoup(price_response.content, features="html.parser")
        # with open('test.html', 'w') as file:
        #     file.write(str(price_soup.encode("utf-8")))
        product_asin = price_soup.find("input", {"id": "ASIN"})['value']
        product_name = price_soup.find("span", {"id":"productTitle"}).text
        product_name = substract(product_name, "\n")
        price_span = price_soup.find("span", {"id":"priceblock_ourprice"})
        if(price_span == None):
            if(is_first == False):
                print(product_name + " Cannot be shipped to Israel from ITALY")
                is_shipping = False
            else:
                print ("Whoops! Something went wrong. Please try again later.")
                is_error = True
        else:
            price = price_span.text
            price = substract(price, "EUR ")
            price = price.replace(",", ".")
            price = substract(price, "\n")
            price = float(price)

        try:
            delivery_message = price_soup.find("div", {"id" : "ddmDeliveryMessage"}).text
            if "Il prodotto può essere consegnato in Israele" in delivery_message:
                print(product_name + " from ITALY ships to Israel and costs: " + str(price))
                is_shipping = True

            else:
                print(product_name + " from ITALY doesn't ship to Israel.")
                is_shipping = False

        except AttributeError:

            if(is_first):
                #this is the first func, user didnt choose an attribute
                os.system('cls')
                print ("Whoops! Something went wrong. Please try again later.")
                is_error = True
            else:
                #this isnt a first func. product doesnt ship to israel
                if(not is_shipping):
                    print(product_name + " from ITALY doesn't ship to Israel")
                    is_shipping = False

        if(is_error):
            it = "error"
        elif (is_shipping):
            it = price
        elif(not is_shipping):
            it = False

        if(is_first):
            us = amazon_us(False, product_asin)
            ger = amazon_ger(False, product_asin)
            return build_json(us,ger,it)
        else:
            return it

    else:
        asin_r = s.get("https://www.amazon.it/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + asin + "&rh=i%3Aaps%2Ck%3AB0722DMYTN")
        asin_soup = BeautifulSoup(asin_r.content, features="html.parser")
        first_product = asin_soup.find("li", {"id" : "result_0"})
        if(first_product == None or not ("/dp/" + asin) in first_product.findAll("a")[0]['href']):
            print("Item doesn't exist in this (Italy) store")
            return False
        else:
            first_asin = first_product['data-asin']
            product_name = first_product.find("h2", {"class":"a-size-medium"})['data-attribute']
            product_name = substract(product_name, "\n")
            first_href = first_product.findAll("a")[0]['href']
            print(product_name + " found in the (Italy) store: " + first_href)
        return amazon_it(True, "", first_href)

# amazon_us(True,"","https://www.amazon.com/Oculus-Marvel-Powers-United-Special-Touch/dp/B07F6WN2LJ/ref=sr_1_1_sspa?s=electronics&ie=UTF8&qid=1537031807&sr=1-1-spons&keywords=oculus+rift&psc=1",True)
