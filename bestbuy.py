import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from transformers import pipeline

import nlp_utilities as utils
from pymongo import MongoClient
from decouple import config
import uuid

import bing as bing

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
db = client['uncoverpc']
quiz = db['quiz']
laptopCollection = db['laptops']
incLaptopsCollection = db['inc-laptops']

# Change this value depending on how much is to be scraped.
iterations = 1

fullproducts = {}
missingproducts = {}
productInfo = {}
description = []

#MODELS 
qa_model = pipeline("question-answering")

#---------------------------------------INIT END---------------------------------------

# QUIZ QUESTIONS
questions = []
collection = quiz.find()[0]['questions']
for quiz_question in collection:
    questions.append(quiz_question['question'])

# Have to check edge cases: if it's a laptop, or pc, or etc
# AMAZON SEARCH PAGE
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

     
    details = out[out.index("What's Included") +1:out.index("Specifications")-1]
    overview = out[out.index("Overview") +1]
    out = out[out.index("Specifications") +1 : out.index("From the Manufacturer")]
    sentences = []
    for i in soup.find_all("h3", {"class": "groupName_3O9-v"}):
        if i.get_text() in out:
            out.remove(i.get_text())

    for i in range(1,len(out) +1, 2):
        sentences.append(f"{out[i-1]}: {out[i]}.")
    
    productInfo["Name"] = soup.find("h1", {"class": "productName_2KoPa"}).get_text()
    productInfo["Link"] = pageURL
    productInfo["Price"] = soup.find_all("span", {"class": "screenReaderOnly_2mubv large_3uSI_"})[0].get_text()
    productInfo["Img"] = soup.find("img", {"class":"productImage_1NbKv"})["src"]
    productInfo["ID"] = uuid.uuid4()
    productInfo["Properties"] = sentences



    print(details)
    print(overview)
    print(productInfo)
   
#     missing = []
#     for item in questions:
        
#         temp = qa_model(question = item, context = context)
#         if (temp['score']>0.5): #May require fine-tuning
#             productInfo[out[out.index(f"{temp['answer']} ") -1].strip()] = temp['answer']
#         else:
#             missing.append(item)

#     # print(productInfo)
#     # print(missing)

#     for item in missing:
#         temp = bing.getData(f"{productInfo['Name']} {item}")
#         print(item)
#         print(temp)
#         # temp = utils.automateAnswer(productInfo["Name"], item)

#         if temp['General Answer'] != "":
#             productInfo[item] = temp['General Answer']
#         elif temp['Highlighted Answer'] != "":
#             productInfo[item] = temp['Highlighted Answer']

#         else:
#             # This is if there are no highlighted or regular answers
#             question = utils.extraSentences(productInfo["Name"], item, temp['People also ask'])
#             if question == 0:
#                 # There is no good "people also ask"
#                 print(iterator)
#                 if iterator >iterations:
#                     print("\n\n\n\n\n")
#                     item = item.replace("?", "")
#                     answer = input(f" {(item)} for the {productInfo['Name']}: ")
#                     productInfo[item] = answer

#             else:
#                 pass

#     name = productInfo.pop('Name',None)

#     for j in range(len(questions)):
#         if questions[j] in dict.keys(productInfo):
#             label = utils.classifyLabel(productInfo[questions[j]],collection[j]['answers'])
#             print(label)
#             productInfo[questions[j]] = label['labels'][0]
            


# # TESTING-----------------------
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

# # postNewProducts(fullproducts, laptopCollection, laptopFormatting)
# # postNewProducts(missingproducts, incLaptopsCollection, laptopFormatting)


# driver.quit()

# print(missingproducts)
# print(fullproducts)
