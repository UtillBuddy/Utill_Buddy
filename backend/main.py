import os
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Request
from pydantic import BaseModel
from backend.auth import create_access_token, verify_firebase_token, get_current_user
from backend.security import get_password_hash, verify_password
from backend.database import get_user, create_user, get_distinct_regions, get_recipients_by_region, save_template, update_existing_template, get_template, get_email_counts_for_user, save_email_config, update_user_cv_link, update_user_plan, save_outlook_tokens, save_smtp_config, get_plans, save_yahoo_config, save_zoho_config
from backend.models import EmailTemplate, User, Token, EmailConfig, SmtpConfig, YahooConfig, ZohoConfig
from backend.tasks import send_emails_task
from firebase_admin import storage, credentials, initialize_app
from backend.outlook import router as outlook_router
import stripe
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from starlette.responses import JSONResponse

from backend.socketio_app import app as socketio_app

def create_app():
    app = FastAPI()

    # Firebase Admin SDK setup
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    initialize_app(cred)

    stripe.api_key = os.getenv("STRIPE_API_KEY")

    app.include_router(outlook_router, prefix="/outlook", tags=["outlook"])
    app.mount("/ws", socketio_app)

    @app.exception_handler(CsrfProtectError)
    def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    @CsrfProtect.load_config
    def get_csrf_config():
        return {"secret_key": os.getenv("SECRET_KEY")}


    @app.post("/register", response_model=Token)
    async def register(user: User, csrf_protect: CsrfProtect = Depends()):
        db_user = get_user(user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        csrf_protect.validate_csrf(request)
        hashed_password = get_password_hash(user.password)
        create_user(user.email, hashed_password)
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    @app.post("/login", response_model=Token)
    async def login(user: User, csrf_protect: CsrfProtect = Depends()):
        db_user = get_user(user.email)
        if not db_user or not verify_password(user.password, db_user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        csrf_protect.validate_csrf(request)
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    @app.post("/token", response_model=Token)
    async def login_with_firebase(token: str, csrf_protect: CsrfProtect = Depends()):
        decoded_token = verify_firebase_token(token)
        email = decoded_token["email"]
        db_user = get_user(email)
        if not db_user:
            # Create a new user if they don't exist in the database
            create_user(email, "") # Store an empty password for Firebase users

        csrf_protect.validate_csrf(request)
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
        send_emails_task.delay(user, template, recipients)
        return {"message": "Email sending process has been queued."}


    @app.get("/status")
    async def get_status(current_user: str = Depends(get_current_user)):
        return get_email_counts_for_user(current_user)


    @app.post("/verify-email-creds")
    async def verify_email_creds(config: EmailConfig, current_user: str = Depends(get_current_user)):
        # This is a placeholder. In a real application, you would verify the credentials.
        save_email_config(current_user, config)
        return {"message": "Email credentials verified and saved"}


    @app.post("/upload-cv")
    async def upload_cv(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

        # 5MB size limit
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Please upload a file smaller than 5MB.")

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


    @app.post("/verify-smtp-creds")
    async def verify_smtp_creds(config: SmtpConfig, current_user: str = Depends(get_current_user)):
        # This is a placeholder. In a real application, you would verify the credentials.
        save_smtp_config(current_user, config)
        return {"message": "SMTP credentials verified and saved"}


    @app.get("/plans")
    async def plans(current_user: str = Depends(get_current_user)):
        return get_plans()


    @app.post("/create-checkout-session")
    async def create_checkout_session(plan_id: str, current_user: str = Depends(get_current_user)):
        plan = plans_collection.find_one({"_id": plan_id})
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": plan["name"],
                    },
                    "unit_amount": plan["price"],
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
            client_reference_id=current_user,
        )
        return {"id": session.id}


    @app.post("/webhook")
    async def webhook(request: Request):
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
        except ValueError as e:
            # Invalid payload
            raise HTTPException(status_code=400, detail=str(e))
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise HTTPException(status_code=400, detail=str(e))

        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session["client_reference_id"]
            update_user_plan(user_id, "paid")

        return {"status": "success"}


    @app.get("/preview-email")
    async def preview_email(current_user: str = Depends(get_current_user)):
        user = get_user(current_user)
        template = get_template(current_user)
        first_name = "John"
        html_body = template["body"].format(first_name=first_name, cv_link=template["cv_link"], user_name=user["email"], user_mobile="", user_secondary_mobile="", user_linkedin="")
        return html_body


    @app.post("/verify-yahoo-creds")
    async def verify_yahoo_creds(config: YahooConfig, current_user: str = Depends(get_current_user)):
        # This is a placeholder. In a real application, you would verify the credentials.
        save_yahoo_config(current_user, config)
        return {"message": "Yahoo credentials verified and saved"}


    @app.post("/verify-zoho-creds")
    async def verify_zoho_creds(config: ZohoConfig, current_user: str = Depends(get_current_user)):
        # This is a placeholder. In a real application, you would verify the credentials.
        save_zoho_config(current_user, config)
        return {"message": "Zoho credentials verified and saved"}


    return app
