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
files = sorted(files_) # For consistent comparison

model_path = "/home/russellb/.cache/huggingface/hub/models--facebook--bart-large-mnli/snapshots/d7645e127eaf1aefc7862fd59a17a5aa8558b8ce"
# model_path = "/home/russellb/.cache/huggingface/hub/models--distilbert--distilbert-base-uncased-finetuned-sst-2-english/snapshots/714eb0fa89d2f80546fda750413ed43d93601a13"

email_classifier = pipeline(
        "zero-shot-classification",
        model=model_path,
        device=0 if T.cuda.is_available() else -1)

"""
email_categories = [
        "Product or Sales promotion",
        "Newsletter",
        "Advertisement",
        "Personal communication",
        "Group communication",
        "Social Media update"
        ]
"""
email_categories = [
    "Newsletter",
    "Personal email",
    "Marketing advertisement",
    "Social media notification",
    "Support communication",
    "Discussion thread",
    "Promotional advertisement"
]

def classify_email(subject, body):
    """
    Classify e-mail into any one the specified category using subject line and
    first 500 characters of e-mail body
    """
    email = f"{subject} {body[:2000]}"

    result = email_classifier(email, email_categories, \
                              hypothesis_template="This email is a {}.")
    # print(f"RESULT: {result}")

    return {
            'category': result['labels'][0],
            'confidence': result['scores'][0],
            'all_scores': dict(zip(result['labels'], result['scores']))
            }

classified = []
confidence = []
from_addrs = []

for file in files[:1000]:
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
            category = classify_email(email['Subject'], clean_text_from_body(txt_frm_html))
            classified.append(category['category'])
            confidence.append(category['confidence'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            print(f"{re.sub("\n\\s*\n", "\n", clean_text_from_body(txt_frm_html))}")
        else:
            category = classify_email(email['Subject'], \
                    clean_text_from_body(email['Body']))
            classified.append(category['category'])
            confidence.append(category['confidence'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            print(f"{re.sub("\n\\s*\n", "\n", clean_text_from_body(email['Body']))}")
        print(f" ===== ===== ===== ")
    except Exception as err:
        print(f"Failed: {err}")

with open("output_2000_ctx_new_classes_adv_only_gt_0_5.csv", "w", newline='\n') as fp:
    writer = csv.writer(fp)
    writer.writerow(['From address', 'Class', 'Confidence'])
    for item1, item2, item3 in zip(from_addrs, classified, confidence):
        if item3 > 0.5:
            writer.writerow([item1, item2, item3])

    # writer.writerow(zip(from_addrs, classified))

