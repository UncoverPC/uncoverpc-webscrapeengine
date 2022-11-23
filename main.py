import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from transformers import pipeline

import nlp_utilities as utils
from pymongo import MongoClient
from decouple import config


item = "laptop"
URL = f"https://www.amazon.ca/s?k={item}"
options = Options()
options.headless = True
options.add_experimental_option("excludeSwitches", ["enable-logging"])
DRIVER_PATH = './chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get(URL)
html = driver.page_source


MONGO_USER = config('USER')
MONGO_PASS = config('PASS')
CONNECTION_STRING = f'mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.fgvaysh.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)
db = client['uncoverpc']
quiz = db['quiz']

qa_model = pipeline("question-answering")

# QUIZ QUESTIONS
questions = []
collection = quiz.find()[0]['questions']
for item in collection:
    questions.append(item['question'])



# questions = ["Series", "Screen Size", "RAM", "Hard Drive", "Operating System", "Battery Life"]

# AMAZON SEARCH PAGE
links = []
soup = BeautifulSoup(html,"html.parser")
for a in soup.find_all('a', {"class": "a-link-normal s-no-outline"}):
    links.append(a["href"])



fullproducts = {}
missingproducts = {}
# AMAZON
for i in range(2):
    pageURL = f"https://www.amazon.ca{links[i]}"
    driver.get(pageURL)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    texts = soup.findAll(text=True)
    lines = soup.get_text(separator = "\n").split("\n")
    out = [line for line in lines if line.strip() != ""]

    out = out[out.index("Technical Details") : out.index("Additional Information")]
    sentences = []

    for i in range(1,len(out)+1, 2):
        out[i] = out[i].replace("‎", "")
        out[i] = out[i].lstrip()

        sentences.append(f"{out[i-1]}is {out[i]}.")

    context = "".join(sentences) 

    output = {}
    output["Name"] = soup.find("span", {"id": "productTitle"}).get_text().split(',')[0].lstrip()
    output["Link"] = pageURL
    missing = []
    for item in questions:
        question = item
        if (qa_model(question = question, context = context)['score']>0.5):
            output[item] = qa_model(question = question, context = context)['answer']
        else:
            missing.append(item)

    print(output)
    print("Missing items:" , missing)

    for item in missing:
        temp = utils.automateAnswer(output["Name"], item)

        if temp['General Answer'] != "":
            output[item] = temp['General Answer']
        elif temp['Highlighted Answer'] != "":
            output[item] = temp['Highlighted Answer']

        else:
            # This is if there are no highlighted or regular answers
            question = utils.extraSentences(output["Name"], item, temp['People also ask'])
            if question == 0:
                # There is no good "people also ask"
                if i < 1:
                    item = item.replace("?", "")
                    answer = input(f" {(item)} for the {output['Name']}: ")
                    output[item] = answer

            else:
                pass

    name = output.pop('Name',None)

    for j in range(len(questions)):
        if questions[j] in dict.keys(output):
            label = utils.classifyLabel(output[questions[j]],collection[j]['answers'])
            print(label)
# TESTING-----------------------
    if i<1:
        fullproducts[name] = output
    else:
        missingproducts[name] = output
    
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

# postNewProducts(products, laptopCollection, laptopFormatting)
driver.quit()

