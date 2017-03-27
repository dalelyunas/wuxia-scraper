#!/usr/bin/env python3

import json
from bs4 import BeautifulSoup
import requests
import time
from fpdf import FPDF
from unidecode import unidecode

config = json.load(open('config.json'))
FPDF_FONTPATH = ''


def scrape(book, pdf):
    latest = book['latest']
    ended = False
    while(not ended):
        soup = get_chapter(book['url'], latest)
        if is_valid_chapter(soup):
            chapter = process_chapter(soup, latest)
            build_pdf_page(pdf, chapter[0], chapter[1])
            latest += 1
        else:
            book['latest'] = latest - 1
            ended = True

        time.sleep(config['delay'])


def process_chapter(soup, number):
    strings = []
    title = 'Chapter {}'.format(number)
    header_title = soup.find('h1', {'class': 'entry-title'})
    title = title if header_title is None else header_title.text.strip()
    body_title = soup.find_next("strong")
    title = title if body_title is None else body_title.text.strip()

    start = soup.find('div', {'itemprop': 'articleBody'}).find_next('hr')
    nested = start.find_all('p')
    text = nested if nested else start.find_next_siblings()
    for p in text:
        if p.name == 'hr':
            break
        elif 'Previous Chapter' in p.text and 'Next Chapter' in p.text:
            break
        elif p.name == 'p':
            strings.append(unidecode(str(p.text)))

    return (title, strings)


def is_valid_chapter(soup):
    if soup.find('section', {'class': 'error-404'}) is not None:
        return False

    start = soup.find('div', {'class': 'entry-content'}).find_next('hr')
    if start.find_next('img') is not None:
        return False

    return True


def get_chapter(book, chapter):
    page = requests.get(config['base_url'].format(book, book, chapter))
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup


def build_pdf_page(pdf, title, text):
    pdf.add_page()
    width = pdf.w - 2 * pdf.l_margin
    pdf.set_font('EBGaramond', '', 20)
    pdf.multi_cell(width, 15, title)
    pdf.ln(15)
    pdf.set_font('EBGaramond', '', 12)
    for p in text:
        pdf.multi_cell(width, 15, p)
        pdf.ln(15)


def main():
    pdf = FPDF(format='letter', unit='pt')
    pdf.add_font('EBGaramond', '', 'EBGaramondRegular.ttf', uni=True)
    pdf.set_margins(144, 72, 144)
    chapter = process_chapter(get_chapter('renegade', 397), 397)
    build_pdf_page(pdf, chapter[0], chapter[1])
    pdf.output('{}.pdf'.format('ast'))


if __name__ == "__main__":
    main()
