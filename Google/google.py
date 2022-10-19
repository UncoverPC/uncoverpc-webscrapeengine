import requests
import urllib.parse
from lxml import html
from lxml import etree
import traceback

PAK = "People also ask"
HA = "Highlighted Answer"
A = "General Answer"

item = "iphone 12"
goal = ["battery"] # there may be multiple items missing per product
search_term = f"how long does the {item} battery last?"

# Getting People also ask


def findPAK(dom):
    y = html.fromstring(etree.tostring(
        dom, method='html', with_tail=False)).xpath('///span/text()')
    if y[0] == PAK:
        y.remove(y[0])
        return y
    else:
        return []

# Getting Answer


def findAnswer(dom):
    return dom.xpath(
        '//*[@id="rso"]/div[1]/div/block-component/div/div[1]/div/div/div/div/div[1]/div/div/div/div/div[1]/div/span/span')

# Getting Specific Answer Key


def findKeyAnswer(dom):
    return dom.xpath(
        '//*[@id="rso"]/div[1]/div/block-component/div/div[1]/div/div/div/div/div[1]/div/div/div/div/div[1]/div/span/span/b/text()')


def getData(searchTerm):
    try:
        URL = "https://www.google.com/search?q=" + \
            urllib.parse.quote(searchTerm.encode('utf8'))
        print(URL)
        HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US, en;q=0.5'})

        webpage = requests.get(URL, headers=HEADERS)
        dom = html.fromstring(webpage.content)

        info = {PAK: '', HA: '', A: ''}

        # Getting People Also Ask
        x = dom.xpath('//*[@id="rso"]/div/div/div/div')
        for y in x:
            if len(y.text_content()) > 15 and y.text_content()[0:15] == PAK:
                info[PAK] = findPAK(y)
                break

        # Getting Answer
        answer = findAnswer(dom)
        # Checking if answer exists
        if type(answer) == list and len(answer) > 0:
            info[A] = answer[0].text_content()
            # Specific Answer Key
            highlightAnswer = findKeyAnswer(dom)
            if type(highlightAnswer) == list and len(highlightAnswer) > 0:
                info[HA] = highlightAnswer[0]

        return info
    except TypeError as e:
        print("An unexpected error has occured while getting data")
        traceback.print_exc()


output = getData(search_term)
