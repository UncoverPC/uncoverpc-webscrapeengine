import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, sys
from bson.binary import Binary

import nlp_utilities as utils
from pymongo import MongoClient
from decouple import config
import uuid

import bing as bing
sys.path.append(os.path.join(os.path.dirname(__file__), "Google"))
import article as article

# ---------------------------------------INIT BEGIN---------------------------------------
# BESTBUY SCRAPER
item = "laptop"
urlID = {"laptop":"20352"}
URL = f"https://www.bestbuy.ca/en-ca/category/{urlID[item]}"
options = Options()
options.headless = True
options.add_experimental_option("excludeSwitches", ["enable-logging"])
DRIVER_PATH = './chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get(URL)
html = driver.page_source

# MONGO
MONGO_USER = config('USER')
MONGO_PASS = config('PASS')
CONNECTION_STRING = f'mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.fgvaysh.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)
db = client['Products']
# quiz = db['quiz']
bestBuyCollection = db['BestBuy']
articlesCollection = db['Articles']

# Change this value depending on how much is to be scraped.
iterations = int(input("Enter number of products to scrape: "))

productInfo = {}
articleInfo = {}
description = []


#---------------------------------------INIT END---------------------------------------

# BEST BUY SEARCH PAGE
links = []
soup = BeautifulSoup(html,"html.parser")

# f=open("out.html", "w")
# f.write(soup.prettify())
# f.close()
for a_tag in soup.find('div', {"class": "productListingContainer_3JUbO"}).find_all('a', {"class": "link_3hcyN"}):
    links.append(a_tag["href"])

# BESTBUY
for iterator in range(iterations):
    pageURL = f"https://www.bestbuy.ca{links[iterator]}"
    driver.get(pageURL)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    lines = soup.get_text(separator = "\n").split("\n")
    out = [line for line in lines if line.strip() != ""]

    try:
        details = out[out.index("What's Included") +1:out.index("Specifications")-1]
        overview = out[out.index("Overview") +1]
        out = out[out.index("Specifications") +1 : out.index("From the Manufacturer")]
        sentences = []
        for i in soup.find_all("h3", {"class": "groupName_3O9-v"}):
            if i.get_text() in out:
                out.remove(i.get_text())

        for i in range(1,len(out) +1, 2):
            sentences.append(f"{out[i-1]}: {out[i]}.")
        
        ID = Binary.from_uuid(uuid.uuid4())

        productInfo["_id"] = ID  
        productInfo["Name"] = soup.find("h1", {"class": "productName_2KoPa"}).get_text()
        productInfo["Link"] = pageURL
        productInfo["Price"] = soup.find_all("span", {"class": "screenReaderOnly_2mubv large_3uSI_"})[0].get_text() if soup.find_all("span", {"class": "screenReaderOnly_2mubv large_3uSI_"}) else ""
        productInfo["Img"] = soup.find("img", {"class":"productImage_1NbKv"})["src"]
        
        productInfo["Properties"] = sentences
        
        articleInfo["_id"] = ID
        articleInfo["Articles"] = article.getArticles(productInfo["Name"]) 
        articleInfo["Contents"] = details
        articleInfo["Description"] = overview

        # print(details)
        # print(overview)
        # print(productInfo)
        
        bestBuyCollection.insert_one(productInfo)
        articlesCollection.insert_one(articleInfo)

        print(f"Inserted a total of {iterator+1} items into database")
    except:
        print("Could not scrape product")
driver.quit()
