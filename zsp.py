#!/usr/bin/env python3
import sys
import os
import glob
import csv

from transformers import pipeline
import torch as T

module_path = os.path.abspath("../")
sys.path.insert(0, module_path)

from parse import *

files_ = glob.glob("./../../../documents/yahoomail/inbox/*")
files = sorted(files_)

model_path = "/home/russellb/.cache/huggingface/hub/models--facebook--bart-large-mnli/snapshots/d7645e127eaf1aefc7862fd59a17a5aa8558b8ce"

email_classifier = pipeline(
        "zero-shot-classification",
        model=model_path,
        device=0 if T.cuda.is_available() else -1)

email_categories = [
        "Promotional",
        "Personal",
        "Newsletter or bulletin",
        "Groups"
        ]

def classify_email(subject, body):
    """
    Classify e-mail into any one the specified category using subject line and
    first 500 characters of e-mail body
    """
    email = f"{subject} {body[5000:]}"

    result = email_classifier(email, email_categories)
    # print(f"RESULT: {result}")

    return {
            'category': result['labels'][0],
            'confidence': result['scores'][0],
            'all_scores': dict(zip(result['labels'], result['scores']))
            }

classified = []
from_addrs = []

for file in files:
    try:
        email = parse_email_file(file)
        print(f" ===== E-mail Meta-data ===== ")
        for k, v in email.items():
            if k != 'Body':
                print(f"{k}: {v}")
                if k == 'From':
                    from_addrs.append(v)
        print(f" ===== E-mail Body ===== ")
        txt_frm_html = get_text_from_html(email['Body'])
        if is_html(email['Body']):
            category = classify_email(email['Subject'], txt_frm_html)
            classified.append(category['category'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            # print(f"{re.sub("\n\\s*\n", "\n", txt_frm_html)}")
        else:
            category = classify_email(email['Subject'], email['Body'])
            classified.append(category['category'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            # print(f"{re.sub("\n\\s*\n", "\n", email['Body'])}")
        print(f" ===== ===== ===== ")
    except Exception as err:
        print(f"Failed: {err}")

with open("output.txt", "w", newline='\n') as fp:
    writer = csv.writer(fp)
    writer.writerow(['From address', 'Class'])
    for item1, item2 in zip(from_addrs, classified):
        writer.writerow([item1, item2])

    # writer.writerow(zip(from_addrs, classified))

