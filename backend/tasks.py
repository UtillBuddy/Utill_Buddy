from backend.celery_app import celery_app
from backend.email_sender import send_smtp_email, send_outlook_email, send_yahoo_email, send_zoho_email, create_message, send_message, get_gmail_service, log_email_status, log_error
from backend.socketio_app import sio
import time
import random
from googleapiclient.errors import HttpError
import bleach

@celery_app.task
def send_emails_task(user, template, recipients):
    provider = user["email_config"]["provider"]
    if provider == "gmail":
        service = get_gmail_service(user["email_config"]["credentials"]["credentials_base64"], user["email_config"]["credentials"]["token_base64"])

    sender = user["email"]

    for recipient in recipients:
        recipient_email = recipient['email'].strip()
        first_name = recipient_email.split('@')[0].capitalize()
        subject = template["subject"].format(first_name=first_name)
        html_body = bleach.clean(
            template["body"].format(first_name=first_name, cv_link=template["cv_link"], user_name=user["email"], user_mobile="", user_secondary_mobile="", user_linkedin=""),
            tags=bleach.sanitizer.ALLOWED_TAGS + ["p", "a", "img", "strong", "em", "u", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "br"],
            attributes={**bleach.sanitizer.ALLOWED_ATTRIBUTES, "a": ["href", "title"], "img": ["src", "alt"]},
        )

        try:
            if provider == "smtp":
                send_smtp_email(user, recipient_email, subject, html_body)
            elif provider == "outlook":
                send_outlook_email(user, recipient_email, subject, html_body)
            elif provider == "yahoo":
                send_yahoo_email(user, recipient_email, subject, html_body)
            elif provider == "zoho":
                send_zoho_email(user, recipient_email, subject, html_body)
            else:
                message = create_message(sender, recipient_email, subject, html_body)
                send_message(service, sender, message)

            print(f"Email Sent to {recipient_email}")
            log_email_status(recipient_email, "Sent")
            sio.emit("email_sent", {"user_id": user["_id"]})
        except Exception as e:
            print(f"Failed to send to {recipient_email}: {e}")
            log_email_status(recipient_email, "failed")
            log_error(recipient_email, e)

        time.sleep(random.randint(60, 300))
