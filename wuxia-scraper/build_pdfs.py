from fpdf import FPDF
import json
import os
from threading import Thread

FPDF_FONTPATH = '../fonts'


def build_pdf(book_path):
    book_data = json.load(open('../var/books/{}'.format(book_path)))
    print('Converting: {}'.format(book_data['title']))
    pdf = FPDF(format='letter', unit='pt')
    pdf.add_font('EBGaramond', '', '../fonts/EBGaramondRegular.ttf', uni=True)
    pdf.set_margins(144, 72, 144)

    for chapter in book_data['chapters']:
        pdf.add_page()

        width = pdf.w - 2 * pdf.l_margin
        pdf.set_font('EBGaramond', '', 20)
        pdf.multi_cell(width, 15, chapter['title'])
        pdf.ln(15)
        pdf.set_font('EBGaramond', '', 12)

        for p in chapter['content']:
            pdf.multi_cell(width, 15, p, align='L')
            pdf.ln(15)

    pdf.output('../var/pdfs/{}.pdf'.format(book_data['title']))


def convert_all_books():
    threads = []
    for book in os.listdir('../var/books'):
        if book.endswith('.json'):
            threads.append(Thread(target=build_pdf, args=(book,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()
