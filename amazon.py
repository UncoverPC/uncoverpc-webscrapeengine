from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True


DRIVER_PATH = './chromedriver.exe'
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
driver.get("https://www.amazon.ca/s?k=laptop")
html = driver.page_source
soup = BeautifulSoup(html,"html.parser")


with open("output.html", 'wt', encoding='utf-8') as html_file:
    for line in soup.prettify():
        html_file.write(line)

links = []
for a in soup.find_all('a', {"class": "a-link-normal s-no-outline"}):
    links.append(a["href"])


driver.get(f"https://www.amazon.ca{links[0]}")
html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

tables = soup.find("table", {"class":"a-normal a-spacing-micro"}).find_all("span")
# children = tables.findChildren("span")

for count, item in enumerate(tables):
    
    if count % 2 == 0:
        print("\n")
        print(item.get_text(),end = ": ")
    else:
        print(item.get_text(),end = "")

   





# NEXT STEP: Find a-size-base a-text-bold from within this object


driver.quit()

# for item in links:

