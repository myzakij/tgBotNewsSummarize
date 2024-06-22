import re
import requests
from bs4 import BeautifulSoup


def remove_votermark_ria(text):

    dot_index = text.find('.')+1
    if dot_index != -1:
        text = text[dot_index+1:]
    return text

def text_ria(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    novost = soup.find_all('div', class_=['article__text', 'article__vrez'])
    text = ""
    for block in novost:
        text += block.get_text()
    alltText = remove_votermark_ria(' '.join(re.split(r'(?<=[.!?])\s*(?=[A-ЯЁ])', text)))
    return alltText