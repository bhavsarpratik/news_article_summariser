import math
import re
from heapq import nlargest
from string import punctuation

import urllib3
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize, word_tokenize

urllib3.disable_warnings()

url = 'http://www.thehindu.com/news/cities/Delhi/why-the-embers-of-student-protests-refuse-to-die/article17386842.ece?homepage=true'
# url = 'http://indianexpress.com/article/india/parliament-budget-session-congress-pm-modi-govt-hate-crimes-in-us-rajnath-singh-statement-4561833/'
#url = 'http://timesofindia.indiatimes.com/elections/assembly-elections/manipur/news/manipur-exit-polls-bjp-and-congress-neck-and-neck-npf-may-break-stalemate/articleshow/57560143.cms'
# url = "https://www.washingtonpost.com/opinions/there-is-no-principled-reason-to-vote-against-gorsuch/2017/03/08/25e53ec8-041f-11e7-b1e9-a05d3c21f7cf_story.html?hpid=hp_no-name_opinion-card-b%3Ahomepage%2Fstory&utm_term=.651dd375b951"

customStopWords = set(stopwords.words('english') + list(punctuation))


def getPageData(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, 'html.parser')

    website = re.findall(r'(\w+).com', url)[0]

    if website == 'indiatimes':
        soup = soup.find("div",  {'class': 'Normal'})
        return soup.find_all("br")[0].text.replace('\n', ' ').strip()

    elif website == 'thehindu':
        soup = soup.find("div",  {'class': 'article'})
        idName = re.findall(r'<div id="(.+)">', str(soup))[0]
        text = soup.find("div",  {'id': idName}).text.replace(
            '\xa0', ' ').replace('\n', ' ')
        return text

    elif website == 'indianexpress':
        text = soup.find_all("p")

        temp = []

        for i, ptag in enumerate(text[:-1]):
            if re.search(r'jQuery', ptag.text) is None:
                temp.append(ptag.text)

        return ' '.join(temp)

    elif website == 'washingtonpost':
        text = soup.find('article').text
        return text


def summarize(url, sentenceRatio=.15):
    text = getPageData(url)
    sents = sent_tokenize(text)
    words = word_tokenize(text.lower())

    numberOfSentences = math.ceil(len(sents) * sentenceRatio)

    # removing some extra stopwords from text
    extraStopWords = ["—", '”']
    customStopWords.update(extraStopWords)
    filteredWords = [w for w in words if w not in customStopWords]

    # generating dictionary of word frequency
    freq = FreqDist(filteredWords)

    from collections import defaultdict
    ranking = defaultdict(int)

    for i, sent in enumerate(sents):
        for word in word_tokenize(sent.lower()):
            if word in freq:
                ranking[i] += freq[word]

    bestSentences = nlargest(numberOfSentences, ranking, key=ranking.get)

    # put sentences in order and print them
    for i in sorted(bestSentences):
        print('>', sents[i], '\n')


sentenceRatio = 0.15
summarize(url, sentenceRatio)
