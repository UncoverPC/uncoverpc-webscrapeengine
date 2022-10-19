from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

options = Options()
options.headless = True


DRIVER_PATH = './chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get("https://www.amazon.ca/s?k=laptop")
html = driver.page_source
soup = BeautifulSoup(html,"html.parser")


dic = {}

with open("output.html", 'wt', encoding='utf-8') as html_file:
    for line in soup.prettify():
        html_file.write(line)

links = []
for a in soup.find_all('a', {"class": "a-link-normal s-no-outline"}):
    links.append(a["href"])

for i in range(len(links)-30):
    driver.get(f"https://www.amazon.ca{links[i]}")
    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("span", {"id": "productTitle"}).get_text()
    tables = soup.find("table", {"class":"a-normal a-spacing-micro"}).find_all("span")

    temp = {}
    for i in range(0,len(tables),2):
        temp[tables[i].get_text()]=tables[i+1].get_text()
    dic[title]=temp




dic =json.dumps(dic)

print(dic)


# NEXT STEP: Find a-size-base a-text-bold from within this object


driver.quit()


