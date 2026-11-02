#!/usr/bin/env python3

import os
import sqlite3
from datetime import datetime


# DB file
DB_NAME = "yahoomail.db"

# Create DB table
def create_table():
    """
    Create e-mail table if doesn't exist
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        recipient TEXT NOT NULL,
        category TEXT NOT NULL,
        confidence FLOAT NOT NULL,
        status INT NOT NULL CHECK (status in (1, 0)),
        cc TEXT,
        bcc TEXT,
        subject TEXT,
        body TEXT,
        email_date TEXT NOT NULL
        )
        """)
    conn.commit()
    conn.close()

def insert_email(sender, recipient, category, confidence, status, cc=None, bcc=None, subj=None, body=None, email_date=None):
    """
    Insert e-mail record into database.
    sent_datetime should be a datetime object or None (defaults to now)
    """

    # Input validation
    if not sender or not recipient:
        raise ValueError("Sender and Recipient field cannot be empty")

    if not category or not confidence or not status:
        raise ValueError("Category, Confidence score and status cannot be empty")

    if email_date is None:
        email_date = str(datetime.now())
    # elif not isinstance(email_date, datetime):
    #     raise TypeError("email_date must be a datetime object")

    # Convert email_datetime to ISO 8601 string for storage
    # email_sent_date = email_date.isoformat()

    try:
        connxn = sqlite3.connect(DB_NAME)
        cursor = connxn.cursor()
        cursor.execute("""
            INSERT INTO emails (sender, recipient, category, confidence, \
            status, cc, bcc, subject, body, email_date) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (sender,
                                                                recipient,
                                                                category,
                                                                confidence,
                                                                status,
                                                                cc, bcc,
                                                                subj,
                                                                body,
                                                                email_date))
        connxn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connxn.close()

