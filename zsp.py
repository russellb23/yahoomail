#!/usr/bin/env python3
import sys
import os
import glob

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
    email = f"{subject} {body[3000:]}"

    result = email_classifier(email, email_categories)
    # print(f"RESULT: {result}")

    return {
            'category': result['labels'][0],
            'confidence': result['scores'][0],
            'all_scores': dict(zip(result['labels'], result['scores']))
            }

for file in files[:10]:
    try:
        email = parse_email_file(file)
        print(f" ===== E-mail Meta-data ===== ")
        for k, v in email.items():
            if k != 'Body':
                print(f"{k}: {v}")
        print(f" ===== E-mail Body ===== ")
        txt_frm_html = get_text_from_html(email['Body'])
        if is_html(email['Body']):
            category = classify_email(email['Subject'], txt_frm_html)
            print(f"Classification details: {category}")
            print(f"{re.sub("\n\\s*\n", "\n", txt_frm_html)}")
        else:
            category = classify_email(email['Subject'], email['Body'])
            print(f"Classification details: {category}")
            print(f"{re.sub("\n\\s*\n", "\n", email['Body'])}")
        print(f" ===== ===== ===== ")
    except Exception as err:
        print(f"Failed: {err}")

