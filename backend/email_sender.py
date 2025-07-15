from __future__ import print_function
import os
import base64
import time
import random
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# Load environment variables from .env
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["hremail"]
collection = db["emailuae"]
error_col = db["email_errors"]

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def decode_base64_to_file(base64_string, file_path):
    with open(file_path, "wb") as file:
        file.write(base64.b64decode(base64_string))

def get_gmail_service(credentials_base64, token_base64):
    creds = None
    decrypted_credentials = decrypt(credentials_base64)
    decode_base64_to_file(decrypted_credentials, "credentials.json")
    if token_base64:
        decrypted_token = decrypt(token_base64)
        decode_base64_to_file(decrypted_token, "token.json")

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def log_email_status(email, status):
    collection.update_one(
        {"email": email},
        {"$set": {"status": status, "updated_at": datetime.datetime.utcnow()}},
        upsert=False
    )

def log_error(email, error):
    error_col.insert_one({
        "email": email,
        "error": str(error),
        "timestamp": datetime.datetime.utcnow()
    })

def create_message(sender, to, subject, html_body):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(html_body, 'html'))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, user_id, message_body):
    return service.users().messages().send(userId=user_id, body=message_body).execute()

def load_recipients(region):
    return list(collection.find({"region": region}))

def get_email_counts():
    total_count = collection.count_documents({})
    sent_count = collection.count_documents({"status": "Sent"})
    pending_count = collection.count_documents({"status": {"$ne": "Sent"}})
    return total_count, sent_count, pending_count


import requests

def get_outlook_service(user):
    access_token = decrypt(user["email_config"]["credentials"]["access_token"])
    return access_token

def send_outlook_email(user, to_email, subject, body):
    access_token = get_outlook_service(user)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    email_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email
                    }
                }
            ]
        }
    }
    response = requests.post("https://graph.microsoft.com/v1.0/me/sendMail", headers=headers, json=email_data)
    response.raise_for_status()

def get_yahoo_service():
    # Placeholder for Yahoo service
    pass

import smtplib

def get_provider_limit(provider):
    if provider == "gmail":
        return 300
    elif provider == "outlook":
        return 300
    elif provider == "yahoo":
        return 200
    else:
        return 100

from backend.encryption import decrypt

def send_smtp_email(user, to_email, subject, body):
    smtp_config = user["email_config"]["credentials"]
    decrypted_password = decrypt(smtp_config["password"])
    message = f"Subject: {subject}\n\n{body}"
    with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
        server.starttls()
        server.login(smtp_config["username"], decrypted_password)
        server.sendmail(user["email"], to_email, message)
