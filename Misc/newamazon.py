import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
URL = "https://www.bestbuy.ca/en-ca/product/asus-rog-strix-g15-15-6-gaming-laptop-amd-ryzen-7-4800h-512gb-ssd-16gb-ram-geforce-nbsp-rtx-nbsp-3050-win-11/15961157"
page = requests.get(URL, headers = headers)


soup = BeautifulSoup(page.text, 'html.parser')
texts = soup.findAll(text=True)
lines = soup.get_text(separator = "\n").split("\n")


out = [line for line in lines if line.strip() != ""]

# with open("output.html", 'wt', encoding='utf-8') as html_file:
#     for line in out:
#         html_file.write(line + "\n")

questions = ["Product Details", "Graphics Card", "Processor Type", "Screen Size", "Dedicated Video Memory Size", "RAM Size", "Battery - Capacity", "Pre-loaded Operating System", "Weight (lbs)" ]
for item in questions:
    if item in out:
        print(item + ": " + out[out.index(item)+1])
    else:
        print(item + ": N/A")


options = Options()
options.headless = True


DRIVER_PATH = './chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get("https://www.amazon.ca/Vivobook-Processor-Microsoft-Personal-L210MA-BH09-CB/dp/B09Z756H4C/ref=sr_1_6?crid=7I4J2F6PE1QD")
html = driver.page_source

# AMAZON
soup2 = BeautifulSoup(html,"html.parser")
texts = soup2.findAll(text=True)
lines = soup2.get_text(separator = "\n").split("\n")
out = [line for line in lines if line.strip() != ""]

out = out[out.index("Technical Details") : out.index("Additional Information")]

for item in out:
    print(item)


driver.quit()
