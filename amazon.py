import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os, sys
import uuid
from bson.binary import Binary
from tqdm import tqdm
import traceback

import nlp_utilities as utils

from pymongo import MongoClient
from decouple import config

import bing as bing
sys.path.append(os.path.join(os.path.dirname(__file__), "Google"))
import article as article
sys.path.append(os.path.join(os.path.dirname(__file__), "Scraping"))
import quizClassification as qClassify

# ---------------------------------------INIT BEGIN---------------------------------------

# Change this value depending on how much is to be scraped.
iterations = int(input("Enter number of products to scrape: "))

# AMAZON SCRAPER
item = "laptop"
URL = f"https://www.amazon.ca/s?k={item}"
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
quizDB = client['uncoverpc']
amazonCollection = db['Amazon']
articlesCollection = db['Articles']
quizCollection = quizDB['quiz']


productInfo = {}
articleInfo = {}

#---------------------------------------INIT END---------------------------------------

questions = []
answers = []
quiz_questions = quizCollection.find()[0]['questions']
for quiz_question in quiz_questions:
    questions.append(quiz_question['question'])

# AMAZON SEARCH PAGE
links = []
soup = BeautifulSoup(html,"html.parser")
for a_tag in soup.find_all('a', {"class": "a-link-normal s-no-outline"}):
    links.append(a_tag["href"])

# AMAZON
for iterator in tqdm(range(iterations)):
    try:

        pageURL = f"https://www.amazon.ca{links[iterator]}"
        driver.get(pageURL)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        lines = soup.get_text(separator = "\n").split("\n")
        out = [line for line in lines if line.strip() != ""]
        out = out[out.index("Technical Details") : out.index("Additional Information")]
        out = out[2:]
        sentences = []


        # Get name first, so that less information needs to be processed if it's a repeated product
        productInfo["Name"] = soup.find("span", {"id": "productTitle"}).get_text().split(',')[0].lstrip()

         # Check if item is already in db
        if amazonCollection.find_one({'Name': f'{productInfo["Name"]}'}) != None:
            print("This product is already in DB")
            continue


        # Cleanup text
        for i in range(1,len(out)+1, 2):
            try:
                out[i] = out[i].replace("‎", "")
                out[i] = out[i].strip()
                out[i-1] = out[i-1].strip()
                sentences.append(f"{out[i-1]}: {out[i]}.")
            except:
                print("Error replacing character")

        for i in soup.find_all('script', type='text/javascript'):
            if "\'dp60MainImage\': \'https:" in i.text:
                lst = "".join([line for line in i.get_text() if line.strip() != ""])
                lst = lst[lst.index("dp60MainImage"):]
                lst = lst[lst.index("https://"):]
                lst = lst[:lst.index("\'")]
                productInfo["Img"] = lst
                break

        # Generate UUID
        ID = Binary.from_uuid(uuid.uuid4())
        
        details = [] 
        for detail in soup.find("div", {"id": "featurebullets_feature_div"}).find_all("span", {"class": "a-list-item"}):
            details.append(detail.text.strip().replace(u'\xa0', u'').replace(u'· ', u''))

        productInfo["_id"] = ID
        productInfo["Link"] = pageURL
        productInfo["Price"] = soup.find("span", {"class": "a-offscreen"}).text
        productInfo["Properties"] = sentences


        articleInfo["_id"] = ID
        articleInfo["Articles"] = article.getArticles(productInfo["Name"])
        articleInfo["Extras"] = details
        # print(productInfo)
        # print(articleInfo)
        classifiedItem = qClassify.processProduct(productInfo, questions, quiz_questions)

        print(classifiedItem)
        # amazonCollection.insert_one(productInfo)
        # articlesCollection.insert_one(articleInfo)
    except Exception as e:
        print("Could not scrape or process product")
        print(traceback.format_exc())


driver.quit()


# TESTING-----------------------
#     if iterator>iterations:
#         fullproducts[name] = productInfo
#     else:
#         missingproducts[name] = productInfo
    
# def postNewProducts(products, collection, formatting):
# 	productIds = []
# 	for product in formatting(products):
# 		productIds.append(collection.insert_one(product).inserted_id)
# 	return productIds

# def laptopFormatting(laptops):
# 	formattedLaptops = []
# 	for laptop in laptops:
# 		formatted = {
# 			"name": laptop,
# 			"specs": laptops[laptop]
# 		}
# 		formattedLaptops.append(formatted)
# 	return formattedLaptops

# postNewProducts(fullproducts, laptopCollection, laptopFormatting)
# postNewProducts(missingproducts, incLaptopsCollection, laptopFormatting)

