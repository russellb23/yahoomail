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

stage_I_categories = [
    "bulk-generated email sent by an organization or service",
    "individually written email from a person",
        ]

stage_II_automated = [
        "newsletter",
        "marketing email",
        "social media notification",
        "sales promotion",
        ]

stage_II_human = [
        "personal correspondence",
        "group discussion",
        ]

def classify_email(subject, body, email_categories):
    """
    Classify e-mail into any one the specified category using subject line and
    first 500 characters of e-mail body
    """
    email = f"""SUBJECT: 
    {subject} 
    
    BODY:
    {body[:2000]}"""

    result = email_classifier(email, email_categories, \
            hypothesis_template="This e-mail should be categorized as {}.", \
            multi_label=False)
    # print(f"RESULT: {result}")

    return {
            'category': result['labels'][0],
            'confidence': result['scores'][0],
            'all_scores': dict(zip(result['labels'], result['scores']))
            }

classified = []
confidence = []
from_addrs = []

patterns = [
        "If you no longer wish to recieve",
        "unsubscribe",
        "update your contact information",
        "copyright",
        "Customer service",
        "Beowulf mailing list",
        "Rakuten",
        "insideHPC"
        ]


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
            body_ = re.sub("\n\\s*\n", "\n", clean_text_from_body(txt_frm_html))
            body = body_
            for p in patterns:
                idx = body_.lower().find(p.lower())
                if idx != -1:
                    body = body_[:idx]
                    break
            category = classify_email(email['Subject'], body, \
                    stage_I_categories)
            delta = category['all_scores'][stage_I_categories[0]]- \
            category['all_scores'][stage_I_categories[1]]
            if category['category'] == stage_I_categories[0] and delta < 0.15:
                categ = classify_email(email['Subject'], body, \
                                       stage_II_automated)
                classified.append(categ['category'])
                confidence.append(categ['confidence'])
            elif category['category'] == stage_I_categories[1] and delta < 0.15:
                categ = classify_email(email['Subject'], body, \
                        stage_II_human)
                classified.append(categ['category'])
                confidence.append(categ['confidence'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            print(f"{body}")
        else:
            body_ = re.sub("\n\\s*\n", "\n", clean_text_from_body(txt_frm_html))
            body = body_
            for p in patterns:
                idx = body_.lower().find(p.lower())
                if idx != -1:
                    body = body_[:idx]
                    break
            category = classify_email(email['Subject'], body, \
                                      stage_I_categories )
            if category['category'] == "automated email":
                categ = classify_email(email['Subject'], body, \
                        stage_II_automated)
                classified.append(categ['category'])
                confidence.append(categ['confidence'])
            elif category['category'] == "human written email":
                categ = classify_email(email['Subject'], body, stage_II_human)
                classified.append(categ['category'])
                confidence.append(categ['confidence'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            print(f"{body}")
        print(f" ===== ===== ===== ")
    except Exception as err:
        print(f"Failed: {err}")

with open("multi_statge.csv", "w", newline='\n') as fp:
    writer = csv.writer(fp)
    writer.writerow(['From address', 'Class', 'Confidence'])
    for item1, item2, item3 in zip(from_addrs, classified, confidence):
        if item3 > 0.5:
            writer.writerow([item1, item2, item3])

    # writer.writerow(zip(from_addrs, classified))
