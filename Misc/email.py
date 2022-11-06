import os
import smtplib

from dotenv import load_dotenv

load_dotenv()

EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

sent_from = 'uncoverpc@gmail.com'
recipients = ['jy90023@gmail.com']

subject = 'Error Report'
body = 'There is a internal error'

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(recipients), subject, body)

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    server.sendmail(sent_from, recipients, email_text)
    server.quit()
except:
    print("Unable to send email")
