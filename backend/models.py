from pydantic import BaseModel
from typing import List, Optional


class Template(BaseModel):
    subject: str
    body: str
    cv_link: str


class EmailConfig(BaseModel):
    provider: str
    credentials: dict


class User(BaseModel):
    email: str
    plan: str
    quota_used: int
    email_config: EmailConfig
    template: Template
    region: str


class Recipient(BaseModel):
    email: str
    region: str
    status: str
    sent_by_user: str
    timestamp: str


class EmailLog(BaseModel):
    user_id: str
    email: str
    status: str
    provider: str
    error: Optional[str] = None


class EmailTemplate(BaseModel):
    user_id: str
    subject: str
    body: str
    cv_link: str
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
