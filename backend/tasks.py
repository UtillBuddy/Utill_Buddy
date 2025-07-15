from backend.celery_app import celery_app
from backend.email_sender import send_emails as send_emails_func
from backend.socketio_app import sio

@celery_app.task
def send_emails_task(user, template, recipients):
    for recipient in recipients:
        send_emails_func(user, template, [recipient])
        sio.emit("email_sent", {"user_id": user["_id"]})
