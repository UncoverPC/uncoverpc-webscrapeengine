import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from transformers import pipeline

import nlp_utilities as utils
from pymongo import MongoClient
from decouple import config

import bing as bing

# ---------------------------------------INIT BEGIN---------------------------------------
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
db = client['uncoverpc']
quiz = db['quiz']
laptopCollection = db['laptops']
incLaptopsCollection = db['inc-laptops']

# Change this value depending on how much is to be scraped.
iterations = 4

fullproducts = {}
missingproducts = {}
productInfo = {}

#MODELS 
qa_model = pipeline("question-answering")

#---------------------------------------INIT END---------------------------------------

# QUIZ QUESTIONS
questions = []
collection = quiz.find()[0]['questions']
for quiz_question in collection:
    questions.append(quiz_question['question'])

# AMAZON SEARCH PAGE
links = []
soup = BeautifulSoup(html,"html.parser")
for a_tag in soup.find_all('a', {"class": "a-link-normal s-no-outline"}):
    links.append(a_tag["href"])

# AMAZON
for iterator in range(iterations):
    pageURL = f"https://www.amazon.ca{links[iterator]}"
    driver.get(pageURL)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    texts = soup.findAll(text=True)
    lines = soup.get_text(separator = "\n").split("\n")
    out = [line for line in lines if line.strip() != ""]

    out = out[out.index("Technical Details") : out.index("Additional Information")]
    out = out[2:]
    sentences = []

    # Cleanup text
    for i in range(1,len(out)+1, 2):
        out[i] = out[i].replace("‎", "")
        out[i] = out[i].lstrip()
        sentences.append(f"{out[i-1]} is {out[i]}.")
    context = "".join(sentences) 

    productInfo["Name"] = soup.find("span", {"id": "productTitle"}).get_text().split(',')[0].lstrip()
    productInfo["Link"] = pageURL
    missing = []
    for item in questions:
        
        temp = qa_model(question = item, context = context)
        if (temp['score']>0.5): #May require fine-tuning
            productInfo[out[out.index(f"{temp['answer']} ") -1].strip()] = temp['answer']
        else:
            missing.append(item)

    # print(productInfo)
    # print(missing)

    for item in missing:
        temp = bing.getData(f"{productInfo['Name']} {item}")
        print(item)
        print(temp)
        # temp = utils.automateAnswer(productInfo["Name"], item)

        if temp['General Answer'] != "":
            productInfo[item] = temp['General Answer']
        elif temp['Highlighted Answer'] != "":
            productInfo[item] = temp['Highlighted Answer']

        else:
            # This is if there are no highlighted or regular answers
            question = utils.extraSentences(productInfo["Name"], item, temp['People also ask'])
            if question == 0:
                # There is no good "people also ask"
                print(iterator)
                if iterator >iterations:
                    print("\n\n\n\n\n")
                    item = item.replace("?", "")
                    answer = input(f" {(item)} for the {productInfo['Name']}: ")
                    productInfo[item] = answer

            else:
                pass

    name = productInfo.pop('Name',None)

    for j in range(len(questions)):
        if questions[j] in dict.keys(productInfo):
            label = utils.classifyLabel(productInfo[questions[j]],collection[j]['answers'])
            print(label)
            productInfo[questions[j]] = label['labels'][0]
            


# TESTING-----------------------
    if iterator>iterations:
        fullproducts[name] = productInfo
    else:
        missingproducts[name] = productInfo
    
def postNewProducts(products, collection, formatting):
	productIds = []
	for product in formatting(products):
		productIds.append(collection.insert_one(product).inserted_id)
	return productIds

def laptopFormatting(laptops):
	formattedLaptops = []
	for laptop in laptops:
		formatted = {
			"name": laptop,
			"specs": laptops[laptop]
		}
		formattedLaptops.append(formatted)
	return formattedLaptops

# postNewProducts(fullproducts, laptopCollection, laptopFormatting)
# postNewProducts(missingproducts, incLaptopsCollection, laptopFormatting)


driver.quit()

print(missingproducts)
print(fullproducts)
