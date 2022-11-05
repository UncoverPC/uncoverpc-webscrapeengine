import requests
from bs4 import BeautifulSoup
from lxml import html
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

def scrape(link):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    URL = f"https://www.google.com/search?q={link}"
    webpage = requests.get(URL, headers=headers)
    dom = html.fromstring(webpage.content)

    return dom
    # return soup.get_text(separator = "\n").split("\n")
