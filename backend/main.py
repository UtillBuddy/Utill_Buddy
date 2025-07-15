from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from backend.auth import create_access_token, verify_firebase_token, get_password_hash, verify_password, get_current_user
from backend.database import get_user, create_user, get_distinct_regions, get_recipients_by_region, save_template, update_existing_template, get_template, get_email_counts_for_user, save_email_config, update_user_cv_link, update_user_plan
from backend.models import EmailTemplate, User, Token, EmailConfig
from backend.email_sender import send_emails
from firebase_admin import storage

app = FastAPI()

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/register", response_model=Token)
async def register(user: User):
    db_user = get_user(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    create_user(user.email, hashed_password)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login(user: User):
    db_user = get_user(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_with_firebase(token: str):
    decoded_token = verify_firebase_token(token)
    email = decoded_token["email"]
    db_user = get_user(email)
    if not db_user:
        # Create a new user if they don't exist in the database
        create_user(email, "") # Store an empty password for Firebase users
    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/regions")
async def get_regions(current_user: str = Depends(get_current_user)):
    return get_distinct_regions()


@app.get("/recipients")
async def get_recipients(region: str, current_user: str = Depends(get_current_user)):
    return get_recipients_by_region(region)


@app.post("/setup-template")
async def setup_template(template: EmailTemplate, current_user: str = Depends(get_current_user)):
    template.user_id = current_user
    save_template(template)
    return {"message": "Template saved successfully"}


@app.put("/update-template")
async def update_template(template: EmailTemplate, current_user: str = Depends(get_current_user)):
    template.user_id = current_user
    update_existing_template(template)
    return {"message": "Template updated successfully"}


@app.post("/send-emails")
async def send_emails_endpoint(region: str, current_user: str = Depends(get_current_user)):
    user = get_user(current_user)
    template = get_template(current_user)
    recipients = get_recipients_by_region(region)
    # This should be a background task
    send_emails(user, template, recipients)
    return {"message": "Email sending process started"}


@app.get("/status")
async def get_status(current_user: str = Depends(get_current_user)):
    return get_email_counts_for_user(current_user)


from fastapi import File, UploadFile

@app.post("/verify-email-creds")
async def verify_email_creds(config: EmailConfig, current_user: str = Depends(get_current_user)):
    # This is a placeholder. In a real application, you would verify the credentials.
    save_email_config(current_user, config)
    return {"message": "Email credentials verified and saved"}


@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    bucket = storage.bucket()
    blob = bucket.blob(f"cvs/{current_user}/{file.filename}")
    blob.upload_from_file(file.file)

    update_user_cv_link(current_user, blob.public_url)

    return {"message": "CV uploaded successfully", "cv_link": blob.public_url}


@app.post("/promo")
async def validate_promo_code(promo_code: str, current_user: str = Depends(get_current_user)):
    if promo_code == "LETSGO":
        update_user_plan(current_user, "paid")
        return {"message": "Promo code validated successfully. You are now on the paid plan."}
    else:
        raise HTTPException(status_code=400, detail="Invalid promo code")
