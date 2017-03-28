#!/usr/bin/env python3

import json
from bs4 import BeautifulSoup
import requests
import time
from fpdf import FPDF
from unidecode import unidecode

config = json.load(open('config.json'))
FPDF_FONTPATH = ''


def scrape(book, data):
    latest = book['latest']
    ended = False
    prev_chapter = {'content': []}
    while(not ended):
        soup = get_chapter(book, latest)
        if is_valid_chapter(soup):
            if (len(prev_chapter['content']) > 0):
                data['chapters'].append(prev_chapter)

            prev_chapter = process_chapter(soup, latest)
            latest += 1
        else:
            if (not book['preview'] and len(prev_chapter['content']) > 0):
                data['chapters'].append(prev_chapter)
                latest += 1

            book['latest'] = latest - 1
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

    start = soup.find('div', {'itemprop': 'articleBody'}).find_next('hr')
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
    if start.find_next('img', {'class': 'size-full'}) is not None:
        return False

    return True


def get_chapter(book, number):
    page = requests.get(config['base_url'].format(book['index'],
                                                  book['chapter'], number))
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


def build_pdf_page(pdf, title, text):
    pdf = FPDF(format='letter', unit='pt')
    pdf.add_font('EBGaramond', '', 'EBGaramondRegular.ttf', uni=True)
    pdf.set_margins(144, 72, 144)
    pdf.add_page()
    width = pdf.w - 2 * pdf.l_margin
    pdf.set_font('EBGaramond', '', 20)
    pdf.multi_cell(width, 15, title)
    pdf.ln(15)
    pdf.set_font('EBGaramond', '', 12)
    for p in text:
        pdf.multi_cell(width, 15, p, align='L')
        pdf.ln(15)

    pdf.output('pdfs/{}.pdf'.format(config['books'][0]['index']))


def main():
    '''Check for existing file'''
    data = {}
    data['title'] = config['books'][0]['title']
    data['chapters'] = []
    sr = config['books'][0]

    scrape(sr, data)
    json.dump(data, open('books/{}.json'.format(sr['index']), 'w'), indent=4)
    json.dump(config, open('config.json', 'w'), indent=4)


if __name__ == "__main__":
    main()
