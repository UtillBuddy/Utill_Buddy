import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["hremail"]
users_collection = db["users"]
recipients_collection = db["recipients"]
email_logs_collection = db["email_logs"]
email_templates_collection = db["email_templates"]


def get_user(email: str):
    return users_collection.find_one({"email": email})


def create_user(email: str, hashed_password: str):
    users_collection.insert_one({"email": email, "hashed_password": hashed_password})


def get_distinct_regions():
    return recipients_collection.distinct("region")


def get_recipients_by_region(region: str):
    return list(recipients_collection.find({"region": region}))


def save_template(template):
    email_templates_collection.insert_one(template.dict())


def update_existing_template(template):
    email_templates_collection.update_one(
        {"user_id": template.user_id},
        {"$set": template.dict()}
    )


def get_template(user_id: str):
    return email_templates_collection.find_one({"user_id": user_id})


def get_email_counts_for_user(user_id: str):
    total_count = recipients_collection.count_documents({})
    sent_count = email_logs_collection.count_documents({"user_id": user_id, "status": "Sent"})
    pending_count = total_count - sent_count
    return {"total": total_count, "sent": sent_count, "pending": pending_count}


def save_email_config(user_id: str, config):
    users_collection.update_one(
        {"email": user_id},
        {"$set": {"email_config": config.dict()}}
    )


def update_user_cv_link(user_id: str, cv_link: str):
    users_collection.update_one(
        {"email": user_id},
        {"$set": {"cv_link": cv_link}}
    )


def update_user_plan(user_id: str, plan: str):
    users_collection.update_one(
        {"email": user_id},
        {"$set": {"plan": plan}}
    )
