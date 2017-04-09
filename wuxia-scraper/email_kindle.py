import os
import smtplib
import json
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

config = json.load(open('../config.json'))


def send_email(filename):
    email_username = config['send_email']
    email_password = config['send_password']
    kindle_email = config['kindle_email']

    email = MIMEMultipart()
    email['Subject'] = 'convert'
    email['To'] = kindle_email
    email['From'] = email_username

    pdf = open('../var/pdfs/{}'.format(filename), "rb")

    attachment = MIMEApplication(pdf.read(), _subtype='pdf')
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition',
                          'attachment', filename=filename)

    email.attach(attachment)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email_username, email_password)
    server.sendmail(email_username, kindle_email, email.as_string())
    server.close()


def send_all_books():
    for pdf in os.listdir('../var/pdfs'):
        if pdf.endswith('.pdf'):
            print('Sending: {}'.format(pdf))
            send_email(pdf)
