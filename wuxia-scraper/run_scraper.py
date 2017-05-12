#!/usr/bin/env python3

import json
from scrape_books import scrape_all_books
from build_pdfs import convert_all_books
from email_kindle import send_all_books

config = json.load(open('../config.json'))


def run_scraper():
    scrape_all_books()
    convert_all_books()
    if config['email_enabled']:
        send_all_books()

if __name__ == "__main__":
        run_scraper()
