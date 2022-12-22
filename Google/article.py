import requests
import urllib.parse
from bs4  import BeautifulSoup
from lxml import html
from lxml import etree
import traceback
import re

#Checking if the article title matches the product
def isArticleTitleMatch(articleTitle, productTitle):
    words = productTitle.split()
    count = 0
    for x in words:
        if x.lower() in articleTitle.lower():
            count = count + 1
    if count/len(words) > 0.65:
        return True
    return False

#Connection to Google
def getLinksToArticles(productTitle):
    try:
            URL = "https://www.google.com/search?q=" + \
                urllib.parse.quote(productTitle.encode('utf8') + ' review'.encode('utf8'))
            HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                        'Accept-Language': 'en-US, en;q=0.5'})

            webpage = requests.get(URL, headers=HEADERS)
            dom = html.fromstring(webpage.content)
            articles = []
            soup = BeautifulSoup(webpage.content, 'html.parser')
            for a_href in soup.select("div > a"):
                if(a_href.has_attr('href')):
                    title = a_href.parent.findChild("h3")
                    if title:
                        article = {'link': a_href['href'], 'title': title.text}
                        articles.append(article)
            return articles
    except:
        #TO DO send an email
        print("An error has occred getting articles links. Source: " + URL)
        return 'error'

def getArticleContent(article):
    try:
            URL = article['link']
            HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                        'Accept-Language': 'en-US, en;q=0.5'})

            webpage = requests.get(URL, headers=HEADERS)
            dom = html.fromstring(webpage.content)
            return dom
    except:
        #TO DO send an email
        print('An error has occured getting article content. Source: ' + article['link'])
        return 'error'

#Call this function
def getArticles(productTitle):
    print('Retriving Prodct: ' + productTitle + '\n')
    articles = getLinksToArticles(productTitle)
    filteredArticles = []
    count = 0
    #Filtering articles
    for x in articles:
        count = count + 1
        if(isArticleTitleMatch(x['title'],productTitle)):
            print(str(count) + '. Article Accepted: ' + x['title'] + '\n')
            print('Retriving article dom... Link: ' + x['link'] + "\n")
            #Getting Article Content
            dom = getArticleContent(x)
            x['dom'] = dom
            filteredArticles.append(x)
            print('Successfully retrived article. Link: ' + x['link'] + "\n")
        else:
            print(str(count) + '. Article Rejected: ' + x['title'] +  '\n')
    return filteredArticles

# Test code
# getArticles('asus vivobook 14')