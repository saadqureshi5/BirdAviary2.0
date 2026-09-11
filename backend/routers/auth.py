from __future__ import annotations
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Read credentials from environment variables
def _get_client_id() -> str:
    return os.environ.get("GOOGLE_CLIENT_ID", "")

def _get_client_secret() -> str:
    return os.environ.get("GOOGLE_CLIENT_SECRET", "")

def _get_redirect_uri() -> str:
    return os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:1420/auth/callback")


class TokenExchangeRequest(BaseModel):
    code: str
    code_verifier: str
    redirect_uri: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/token")
async def exchange_token(request: TokenExchangeRequest):
    """Exchange authorization code for tokens (keeps client_secret server-side)."""
    client_id = _get_client_id()
    client_secret = _get_client_secret()

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured on server")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": request.code,
                "redirect_uri": request.redirect_uri,
                "code_verifier": request.code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh an expired access token (keeps client_secret server-side)."""
    client_id = _get_client_id()
    client_secret = _get_client_secret()

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured on server")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
                "refresh_token": request.refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


@router.get("/client-id")
async def get_client_id():
    """Return the client ID so the frontend can initiate the OAuth flow."""
    client_id = _get_client_id()
    if not client_id:
        raise HTTPException(status_code=500, detail="Google Client ID not configured on server")
    return {"client_id": client_id}
