import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from transformers import pipeline

import nlp_utilities as utils


URL = "https://www.amazon.ca/Vivobook-Processor-Microsoft-Personal-L210MA-BH09-CB/dp/B09Z756H4C/ref=sr_1_6?crid=7I4J2F6PE1QD"
options = Options()
options.headless = True
DRIVER_PATH = './chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get(URL)
html = driver.page_source
driver.quit()


qa_model = pipeline("question-answering")

questions = ["Series", "Screen Size", "RAM", "Hard Drive", "Operating System", "Battery Life"]

# AMAZON
soup2 = BeautifulSoup(html,"html.parser")
texts = soup2.findAll(text=True)
lines = soup2.get_text(separator = "\n").split("\n")
out = [line for line in lines if line.strip() != ""]

out = out[out.index("Technical Details") : out.index("Additional Information")]
sentences = []

for i in range(1,len(out)+1, 2):
    out[i] = out[i].replace("‎", "")
    out[i] = out[i].lstrip()

    sentences.append(f"{out[i-1]}is {out[i]}.")

context = "".join(sentences) 

output = {}
output["link"] = URL
missing = []
for item in questions:
    question = f"what is the {item}?"
    if (qa_model(question = question, context = context)['score']>0.5):
        output[item] = qa_model(question = question, context = context)['answer']
    else:
        missing.append(item)

###### SPECIAL CASES ######
# SERIES
output["Series"] = out[out.index(" Series ") + 1]
missing.remove("Series")

print(output)
print("Missing items:" , missing)

for item in missing:
    print(utils.automateAnswer(output["Series"], item))
