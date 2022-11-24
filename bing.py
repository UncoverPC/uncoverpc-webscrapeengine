import requests
import urllib.parse
from lxml import html
from lxml import etree
import traceback

PAK = "People also ask"
HA = "Highlighted Answer"
A = "General Answer"
DA = "Definite Answer"


def findAnswer(dom):
    return dom.xpath(
        '//*[@id="d_ans"]/div/div[2]/div/div[1]')


def findKeyAnswer(dom):
    return dom.xpath(
        '//*[@id="d_ans"]/div/div[2]/div/div[1]/strong')


def findDefiniteAnswer(dom):
    return dom.xpath('//*[@id="d_ans"]/div/div[1]/div/div[1]')

# Getting People also ask


def findPAK(dom):
    # print(dom.xpath('//*[@id="df_listaa"]/div/div/div/div'))
    # if(dom.xpath('//*[@id="df_listaa"]/div/div/div/div/text()')[0] == PAK):
    return dom.xpath('//*[@id="df_listaa"]/div/div[2]/div/div[2]/div/div[3]/div/div/div/div/div/span[1]')


def getData(searchTerm):
    try:
        URL = "https://www.bing.com/search?q=" + \
            urllib.parse.quote(searchTerm.encode('utf8'))
        print(URL)
        HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US, en;q=0.5'})

        webpage = requests.get(URL, headers=HEADERS)
        dom = html.fromstring(webpage.content)

        info = {PAK: '', HA: '', A: '', DA: ''}

        # Getting People Also Ask
        peopleAlsoAsk = findPAK(dom)
        # print(peopleAlsoAsk)
        if type(peopleAlsoAsk) == list and len(peopleAlsoAsk) > 0:
            placeholder = []
            for x in peopleAlsoAsk:
                placeholder.append(x.text_content())
            info[PAK] = placeholder

        # Getting Answer
        answer = findAnswer(dom)
        # Checking if answer exists
        if type(answer) == list and len(answer) > 0:
            info[A] = answer[0].text_content()
            # Specific Answer Key
            highlightAnswer = findKeyAnswer(dom)
            if type(highlightAnswer) == list and len(highlightAnswer) > 0:
                info[HA] = highlightAnswer[0].text_content()
            # Definite Answer
            definiteAnswer = findDefiniteAnswer(dom)
            if type(definiteAnswer) == list and len(definiteAnswer) > 0:
                info[DA] = definiteAnswer[0].text_content()
        return info
    except TypeError as e:
        print("An unexpected error has occured while getting data")
        traceback.print_exc()


output = getData(
    "ASUS TUF Gaming A17 Gaming Laptop battery life")
print(output)
