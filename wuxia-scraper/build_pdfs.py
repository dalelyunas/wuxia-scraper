from fpdf import FPDF

FPDF_FONTPATH = '../fonts'


def build_pdf(book_data):
    pdf = FPDF(format='letter', unit='pt')
    pdf.add_font('EBGaramond', '', 'EBGaramondRegular.ttf', uni=True)
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
