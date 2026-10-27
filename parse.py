#!/usr/bin/env python3

import json
import glob

from bs4 import BeautifulSoup as bs

files = glob.glob("./../../../documents/yahoomail/jsons/*.json")

def is_html(text: str): 
    soup = bs(text, 'html.parser')
    if len(soup.find_all()) > 0:
        return True
    else:
        return False


for file in files:
    with open(file, "r") as f:
        data = json.load(f)
        curr_headers = data.keys()
        if 'body' not in data.keys():
            print(f"Message: No e-mail body")
        else:
            if is_html(data['body']):
                # print(f"IT IS HTML TEXT")
                pass
            else:
                # print(f"Body: {data['body']}")
                # print(f"{'='*10}\t{f}")
                if 'x-originating-ip' in data.keys():
                    print(f"From: {data['from'][0][1]}\nIP: {data['x-originating-ip']}\n")
                else:
                    print(f"From: {data['from']}")
        """

                print(f"{'='*30}")
                if 'date' not in data.keys():
                    print(f"Date not found")
                elif 'date_header_defects' not in data.keys():
                    print(f"Date: {data['date']}")
                else:
                    print(f"Date header defect")
                print(f"{'='*30}")
                if 'reply-to' in data.keys():
                    print(f"To: {data['reply-to']}")
                elif 'to' in data.keys():
                    print(f"To: {data['to']}")
                elif 'bcc' in data.keys():
                    print(f"To: {data['bcc']}")
                elif 'cc' in data.keys():
                    print(f"To: {data['cc']}")
                elif 'x-forwarded-to' in data.keys():
                    print(f"To: {data['x-forwarded-to']}")
                else:
                    pass
                print(f"{'='*30}")
                if 'subject' in data.keys():
                    print(f"Subject: {data['subject']}")
                else:
                    print(f"Subject not specified")
                print(f"{'='*30}")
                """
