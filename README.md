# SaaS Job Application Email Sender

This is a SaaS platform where job seekers can automate email job applications using their own personal email (Gmail, Outlook, Yahoo, Zoho, etc.), manage email templates, upload or link to a CV, and send to region-specific email lists — all while respecting per-provider sending limits.

## Backend

The backend is built with FastAPI and MongoDB.

### Running the backend with Docker

1.  **Build the Docker image:**

    ```bash
    docker build -t email-sender-backend .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -d -p 80:80 --env-file backend/.env email-sender-backend
    ```

    Make sure to create a `.env` file in the `backend` directory with the following environment variables:

    ```
    MONGODB_URI="your_mongodb_uri"
    FIREBASE_CREDENTIALS_PATH="path/to/your/firebase/credentials.json"
    SECRET_KEY="your_secret_key"
    UI_PASSWORD="your_ui_password"
    CREDENTIALS_BASE64="your_credentials_base64"
    TOKEN_BASE64="your_token_base64"
    ENCRYPTION_KEY="your_encryption_key"
    OUTLOOK_CLIENT_ID="your_outlook_client_id"
    OUTLOOK_CLIENT_SECRET="your_outlook_client_secret"
    STRIPE_API_KEY="your_stripe_api_key"
    STRIPE_WEBHOOK_SECRET="your_stripe_webhook_secret"
    ```

    To generate an encryption key, you can use the following Python code:

    ```python
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    print(key.decode())
    ```

## Frontend

The frontend is built with Next.js and Tailwind CSS.

### Running the frontend with Docker

1.  **Build the Docker image:**

    ```bash
    docker build -t email-sender-frontend ./frontend
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -d -p 3000:3000 email-sender-frontend
    ```
