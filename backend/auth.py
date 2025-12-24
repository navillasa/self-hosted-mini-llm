from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Header
from jose import JWTError, jwt
import httpx

from config import settings


async def exchange_github_code_for_token(code: str) -> dict:
    """Exchange GitHub OAuth code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Failed to exchange code for token"
            )

        data = response.json()
        if "error" in data:
            raise HTTPException(
                status_code=400,
                detail=data.get("error_description", "GitHub OAuth error"),
            )

        return data


async def get_github_user(access_token: str) -> dict:
    """Get GitHub user information using access token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Failed to get GitHub user info"
            )

        return response.json()


def create_jwt_token(user_data: dict) -> str:
    """Create JWT token with user data"""
    expiration = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)

    payload = {
        "sub": str(user_data["id"]),  # GitHub user ID
        "username": user_data["login"],
        "avatar_url": user_data.get("avatar_url"),
        "exp": expiration,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def verify_jwt_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}") from e
