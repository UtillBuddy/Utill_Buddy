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
import gradio as gr
import threading

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

def get_gmail_service():
    creds = None
    credentials_base64 = os.getenv("CREDENTIALS_BASE64")
    token_base64 = os.getenv("TOKEN_BASE64")
    decode_base64_to_file(credentials_base64, "credentials.json")
    decode_base64_to_file(token_base64, "token.json")

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

subject_template = "Hi {first_name}, IT System Engineer with 7 Years of Experience"
body_template = """<p>Hi {first_name},</p>
<p>Good day to you,</p>
<p>I have more than seven years of experience in the IT field, where I have developed skills in hardware, networking, and Microsoft technologies, particularly Azure cloud. Here's a quick look at what I can offer:</p>
<p><strong>Skills:</strong></p>
<ul>
    <li><strong>Operating Systems &amp; Cloud:</strong> Well-versed in Windows (both Desktop and Server), Azure, Microsoft 365, Office 365, and various cloud services (SaaS, PaaS, IaaS).</li>
    <li><strong>Networking &amp; Security:</strong> Experienced with VLANs, NAT, IPS/IDS, pfSense, Sophos, IPsec, Firewall, QoS, Routing, and Switching.</li>
    <li><strong>Systems Management:</strong> Proficient in SCCM, DNS, Active Directory, Group Policy Objects (GPO), Hyper-V, ServiceNow, and Intune.</li>
    <li><strong>Data Protection &amp; Recovery:</strong> Knowledgeable in IDS, DLP, RAID, NAS, SAN, and backup and recovery tools like Acronis, Veeam, Datto, and Citrix.</li>
    <li><strong>Infrastructure:</strong> Familiar with cluster setups, high availability configurations, and data center operations.</li>
</ul>
<p>I'm excited about the opportunity to contribute my skills to your company's growth and success. I look forward to the possibility of discussing how I can contribute to your team.</p>
<p>You can view and download my resume from this link: 
<a href=\"https://drive.google.com/file/d/1G_IbqmCOPx0rsCCp9IQ8g39NFbGB2eb0/view?usp=sharing\">Resume - Saranga Thenuwara</a></p>
<p>Thank You!</p>
<p>Kind Regards,</p>
<p><strong>Saranga Thenuwara</strong><br>
Mobile: +971 56 806 1308 | +94 77 38 32 416 <br>
<a href=\"http://linkedin.com/in/sthenuwara\">LinkedIn - Saranga Thenuwara</a></p>
"""

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

def load_recipients():
    return list(collection.find())

def get_email_counts():
    total_count = collection.count_documents({})
    sent_count = collection.count_documents({"status": "Sent"})
    pending_count = collection.count_documents({"status": {"$ne": "Sent"}})
    return total_count, sent_count, pending_count

def main():
    service = get_gmail_service()
    sender = "me"
    daily_limit = 300
    emails_sent_today = 0
    start_hour = datetime.datetime.now().hour
    emails_sent_this_hour = 0
    hourly_limit = random.randint(14, 20)

    while True:
        if emails_sent_today >= daily_limit:
            print("Daily limit reached. Waiting until next check...")
            time.sleep(3600 * 6)
            continue

        current_hour = datetime.datetime.now().hour
        if current_hour != start_hour:
            start_hour = current_hour
            emails_sent_this_hour = 0
            hourly_limit = random.randint(14, 20)

        recipients = load_recipients()
        for recipient in recipients:
            recipient_email = recipient['email'].strip()
            status = str(recipient.get('status', '')).lower().strip()

            if status == 'sent':
                continue

            if emails_sent_this_hour >= hourly_limit:
                print("Hourly limit reached. Waiting 1 hour...")
                time.sleep(3600)
                break

            first_name = recipient_email.split('@')[0].capitalize()
            subject = subject_template.format(first_name=first_name)
            html_body = body_template.format(first_name=first_name)

            try:
                message = create_message(sender, recipient_email, subject, html_body)
                send_message(service, sender, message)
                print(f"Email Sent to {recipient_email}")
                log_email_status(recipient_email, "Sent")
                emails_sent_today += 1
                emails_sent_this_hour += 1
            except HttpError as e:
                print(f"Failed to send to {recipient_email}: {e}")
                log_email_status(recipient_email, "failed")
                log_error(recipient_email, e)

            time.sleep(random.randint(60, 300))

# Password protection for starting email sending
AUTHORIZED_PASSWORD = os.getenv("UI_PASSWORD") or "my_secure_password"

def secure_start(password):
    if password.strip() == AUTHORIZED_PASSWORD:
        thread = threading.Thread(target=main)
        thread.start()
        return "✅ Email sending started in the background."
    else:
        return "❌ Incorrect password. Access denied."

def status_check():
    total, sent, pending = get_email_counts()
    return f"Total Emails: {total}\nSent: {sent}\nPending: {pending}"

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("### 🔐 Secure Email Sender (Saranga Thenuwara)")
    gr.Markdown("Enter the password to start the email campaign.")
    
    password_input = gr.Textbox(label="Password", type="password", placeholder="Enter password...")
    start_btn = gr.Button("Start Sending Emails")
    output = gr.Textbox(label="Status")
    email_counts = gr.Textbox(label="Email Counts", interactive=False)
    
    start_btn.click(fn=secure_start, inputs=password_input, outputs=output)
    
    status_btn = gr.Button("Check Email Status")
    status_btn.click(fn=status_check, outputs=email_counts)

demo.queue().launch()
