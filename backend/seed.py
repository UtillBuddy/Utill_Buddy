import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["hremail"]
plans_collection = db["plans"]

plans_collection.delete_many({})

plans_collection.insert_one({
    "name": "Paid Plan",
    "price": 500,  # in cents
    "emails": 1000
})

print("Database seeded successfully!")
