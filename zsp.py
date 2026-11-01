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
# model_path = "/home/russellb/.cache/huggingface/hub/models--FacebookAI--roberta-large-mnli/snapshots/2a8f12d27941090092df78e4ba6f0928eb5eac98"
email_classifier = pipeline(
        "zero-shot-classification",
        model=model_path,
        device=0 if T.cuda.is_available() else -1)

stage_I_categories = [
    "automated email",
    "human written email",
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

email_categs = [
        "Personal correspondence",
        "Discussion forum",
        "Newsletter",
        "Marketing promotion",
        "Account notification",
        "socialmedia communication",
        "Job or career communication",
        "computer technology"
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
            hypothesis_template="The context of the email is {}.", \
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
            body_ = re.sub("\n\\s*\n", "\n", clean_text_from_body(txt_frm_html))
            body = body_

            # for p in patterns:
            #     idx = body_.lower().find(p.lower())
            #     if idx != -1:
            #         body = body_[:idx]
            #         break
            category = classify_email(email['Subject'], body, \
                    email_categs)
            classified.append(category['category'])
            confidence.append(category['confidence'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            print(f"{body}")
        else:
            body_ = re.sub("\n\\s*\n", "\n", clean_text_from_body(txt_frm_html))
            body = body_
            # for p in patterns:
            #     idx = body_.lower().find(p.lower())
            #     if idx != -1:
            #         body = body_[:idx]
            #         break
            category = classify_email(email['Subject'], body, \
                                      email_categs )
            classified.append(category['category'])
            confidence.append(category['confidence'])
            print(f"Classification details: {category}")
            print(f"{'$'*50}")
            print(f"{body}")
        print(f" ===== ===== ===== ")
    except Exception as err:
        print(f"Failed: {err}")

with open("single_statge_mnli_mod.csv", "w", newline='\n') as fp:
    writer = csv.writer(fp)
    writer.writerow(['From address', 'Class', 'Confidence'])
    for item1, item2, item3 in zip(from_addrs, classified, confidence):
        if item3 > 0.0:
            writer.writerow([item1, item2, item3])

    # writer.writerow(zip(from_addrs, classified))
