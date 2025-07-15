import os
import msal
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import RedirectResponse
from backend.database import save_outlook_tokens
from backend.auth import get_current_user

router = APIRouter()

AUTHORITY = "https://login.microsoftonline.com/common"
CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID")
CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET")
REDIRECT_PATH = "/outlook/callback"
SCOPES = ["Mail.Send", "User.Read"]


def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET, token_cache=cache
    )


@router.get("/login")
async def login(request: Request):
    auth_url = build_msal_app().get_authorization_request_url(
        SCOPES, redirect_uri=str(request.url_for("callback"))
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(request: Request, code: str, current_user: str = Depends(get_current_user)):
    result = build_msal_app().acquire_token_by_authorization_code(
        code, SCOPES, redirect_uri=str(request.url_for("callback"))
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result.get("error_description"))

    save_outlook_tokens(current_user, result["access_token"], result["refresh_token"])

    return {"message": "Outlook credentials saved successfully"}
