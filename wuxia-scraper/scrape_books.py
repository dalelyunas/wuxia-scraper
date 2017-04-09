import json
from bs4 import BeautifulSoup
import requests
import time
from unidecode import unidecode
import os

config = json.load(open('../config.json'))


def scrape(book_config, data):
    latest = book_config['latest']
    chapters = data['chapters']
    if len(chapters) > 0:
        del chapters[len(chapters) - 1]
    ended = False
    while(not ended):
        soup = get_chapter(book_config, latest)
        if is_valid_chapter(soup):
            chapters.append(process_chapter(soup, latest))
            latest += 1
        else:
            book_config['latest'] = latest - 1
            ended = True

        time.sleep(config['delay'])


def process_chapter(soup, number):
    chapter = {}
    chapter['content'] = []

    title = 'Chapter {}'.format(number)
    header_title = soup.find('h1', {'class': 'entry-title'})
    title = title if header_title is None else header_title.text.strip()
    body_title = soup.find_next("strong")
    title = title if body_title is None else body_title.text.strip()
    chapter['title'] = unidecode(title)

    article = soup.find('div', {'itemprop': 'articleBody'})

    start = article.find_next('hr')
    start = article.find_all('p')[1] if start is None else start

    nested = start.find_all('p')
    text = nested if nested else start.find_next_siblings()
    for p in text:
        if p.name == 'hr':
            break
        p_text = unidecode(str(p.text))
        if 'Previous Chapter' in p_text and 'Next Chapter' in p_text:
            break
        elif p.name == 'p':
            chapter['content'].append(p_text)

    return chapter


def is_valid_chapter(soup):
    if soup.find('section', {'class': 'error-404'}) is not None:
        return False

    start = soup.find('div', {'class': 'entry-content'}).find_next('hr')

    if start is not None:
        if start.find_next('img', {'class': 'size-full'}) is not None:
            return False

        if start.find_next('iframe') is not None:
            return False

    return True


def get_chapter(book_config, number):
    page = requests.get(config['base_url'].format(book_config['index'],
                        book_config['chapter'], number))
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


def process_book(book):
    json_path = '../var/books/{}.json'.format(book['index'])
    if os.path.isfile(json_path):
        data = json.load(open(json_path))
    else:
        data = {}
        data['title'] = book['title']
        data['chapters'] = []

    scrape(book, data)
    json.dump(data, open(json_path, 'w'), indent=4)


def scrape_all_books():
    for book in config['books']:
        print('Scraping: {}'.format(book['title']))
        process_book(book)
        time.sleep(config['delay'])

    json.dump(config, open('../config.json', 'w'), indent=4)
