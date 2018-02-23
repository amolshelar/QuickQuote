# -*- coding: utf-8 -*-

from imapclient import IMAPClient
from secrets import EMAIL, PASSWORD
from email.message import EmailMessage
from email.headerregistry import Address
import email.utils
import pandas as pd
import config
import collections
import os

def give_email_address(addresses):
    parts = email.utils.getaddresses(addresses)
    username, domain = parts[0][1].split('@')
    display_name = parts[0][0]
    address = Address(display_name=display_name,
                      username=username, domain=domain)
    return address

# Create the base text message.

def create_email(email_to, email_subject, email_from, email_content):
    msg = EmailMessage()
    msg['Subject'] = email_subject
    msg['From'] = email_from
    msg['To'] = email_to
    msg.set_content(email_content)
    return bytes(msg)


# Reading Template from email.template

def read_template():
    with open(config.template, 'r', encoding='utf8') as file:
        email_template = file.read()
    return email_template

def empty_predicted_mails():
    open(config.predicted_csv,encoding = 'utf-8', mode = 'w').close()

# Marking the predicted emails

def mark_predicted(id, message_id):
    entry = collections.OrderedDict({'ID' : id, 'MessageID' : message_id})
    df = pd.DataFrame([entry])
    file_exists = os.path.isfile(config.predicted_csv)
    if not file_exists or os.stat(config.predicted_csv).st_size == 0:
        df.to_csv(config.predicted_csv, header=True, index=False, encoding='utf-8')
    else:
        df.to_csv(config.predicted_csv, mode='a', index=False,
                  header=False, encoding='utf-8')    
    

def append_mail(doc, server, folder, new_flags):
    email_to = give_email_address([doc['Senderemail']])
    email_from = give_email_address([config.email_from])
    email_subject = 'Re:' + doc['Subject']
    result = doc['Offer']
    email_template = read_template()
    email_content = email_template.format(product_=result,from_=doc['Senderemail'],subject_=doc['Subject'],sendon_=doc['SentOn'],content_=doc['Contents'])
    mail = create_email(email_to, email_subject, email_from, email_content)
    server.append(folder, mail, flags=(new_flags), msg_time=None)
    mark_predicted(doc['ID'], doc['MessageID'])
    pass


def login():
    server = IMAPClient(config.imap_server, use_uid=True, ssl=True)
    server.login(EMAIL, PASSWORD)
    return server


def mail_append_main():
    print('>> MailAppend started')
    server = login()
    df = pd.read_csv(config.eraw_data_csv, encoding='utf8')
    empty_predicted_mails()
    df.apply(append_mail, args=(server, config.append_box, []), axis=1)
    server.logout()
    print('>> MailAppend Ended')

# mail_append_main()
