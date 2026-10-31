#!/usr/bin/env python3

import json
import glob
import re
import os
from email.parser import BytesParser
from email import policy

from bs4 import BeautifulSoup as bs

files_ = glob.glob("./../../../documents/yahoomail/inbox/*")
files = sorted(files_)


def parse_email_file(file_path):
    """
    Reads and parses an email file containing headers and body.
    Returns a dictionary with metadata and body content.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Read file as bytes (important for correct parsing)
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        # Extract headers safely
        email_data = {
            "From": msg.get("From", ""),
            "To": msg.get("To", ""),
            "Cc": msg.get("Cc", ""),
            "Bcc": msg.get("Bcc", ""),
            "Subject": msg.get("Subject", ""),
            "Date": msg.get("Date", ""),
            "Body": get_email_body(msg)
        }
        return email_data

    except Exception as e:
        raise RuntimeError(f"Error parsing email file: {e}")

def get_email_body(msg):
    """
    Extracts the plain text body from an email message.
    Handles multipart messages and falls back to HTML if no plain text is found.
    """
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                return part.get_content()
        # Fallback: return HTML if plain text not found
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return part.get_content()
        return ""
    else:
        return msg.get_content()


def is_html(text):
    """
     Check if the given text contains HTML code using only regex.
     Returns True if HTML tags are detected, False otherwise.
    """
    if not isinstance(text, str) or not text.strip():
        return False  # Invalid or empty input
    # Regex pattern to detect common HTML tags
    html_tag_pattern = re.compile(
        r"<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>(.*?)</\1>|<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*/?>",
        re.DOTALL
    )
    return bool(html_tag_pattern.search(text))


def get_text_from_html(html):
    """
    Extract text from html. Returns empty string if no text is supplied
    """
    if not isinstance(html, str) or not html.strip():
        return " "
    else:
        soup = bs(html, 'html.parser')
        data = soup.get_text()
        return re.sub(r"\n\s*\n", "\n", data)

def clean_text_from_body(threaded_text):
    """
    Remove threaded replies from the content
    Remove lines that start with ">"
    """
    cleaned_body = re.sub(r'>.*(?:\n|$)', '', threaded_text, flags=re.MULTILINE)
    return cleaned_body

