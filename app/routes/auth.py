# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime, timedelta
import logging
from app.utils.config import get_settings
from app.models.user import Token, User, UserResponse
from app.utils.auth import create_access_token, create_refresh_token, verify_token
from pydantic import BaseModel, Field
from typing import Dict, Any

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSignInRequest(BaseModel):
    id_token: str = Field(..., description="Google ID Token from iOS client")

class ErrorResponse(BaseModel):
    detail: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

router = APIRouter(tags=["authentication"])
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/google/signin", response_model=TokenResponse, responses={
    401: {"model": ErrorResponse, "description": "Authentication failed"},
    400: {"model": ErrorResponse, "description": "Invalid request"}
})
async def google_signin(request: GoogleSignInRequest, raw_request: Request):
    try:
        # 記錄請求內容
        body = await raw_request.json()
        logger.info(f"Received sign-in request with body: {body}")
        
        if not request.id_token:
            raise ValueError("ID token is required")
            
        # Verify the ID token with clock skew tolerance
        logger.info("Verifying Google ID token...")
        idinfo = id_token.verify_oauth2_token(
            request.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        
        # 記錄驗證結果
        logger.info(f"Token verified successfully. Email: {idinfo.get('email')}")
        
        # Get user info from verified token
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        picture = idinfo.get('picture')
        
        # Create or update user in database
        user = User.objects(email=email).first()
        if not user:
            logger.info(f"Creating new user for email: {email}")
            user = User(
                email=email,
                name=name,
                picture=picture,
                created_at=datetime.utcnow()
            )
            user.save()
        else:
            logger.info(f"User found: {email}")
        
        # Update last login and active time
        user.last_login = datetime.utcnow()
        user.last_active = datetime.utcnow()
        user.save()
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user.email}
        )
        
        logger.info(f"Login successful for user: {email}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 轉換為秒
        )
        
    except ValueError as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during sign-in: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sign-in failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    try:
        # 驗證 refresh token
        email, expiration_time = verify_token(refresh_token, token_type="refresh")
        
        # 創建新的 tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email},
            expires_delta=access_token_expires
        )
        
        # 檢查是否需要更新 refresh token
        current_time = datetime.utcnow()
        time_until_expiry = expiration_time - current_time
        total_validity = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        # 如果剩餘有效期小於一半，創建新的 refresh token
        if time_until_expiry < (total_validity / 2):
            logger.info("Creating new refresh token due to approaching expiration")
            new_refresh_token = create_refresh_token(data={"sub": email})
        else:
            new_refresh_token = refresh_token
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        logger.error(f"Error refreshing tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        # 驗證 access token
        email, _ = verify_token(token, token_type="access")
        user = User.objects(email=email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse, responses={
    401: {"model": ErrorResponse, "description": "Authentication failed"},
    404: {"model": ErrorResponse, "description": "User not found"}
})
async def read_users_me(current_user: User = Depends(get_current_user)):
    # Update last active time
    current_user.last_active = datetime.utcnow()
    current_user.save()
    
    # Convert to dict and update _id
    user_dict = current_user.to_mongo().to_dict()
    user_dict['_id'] = str(user_dict['_id'])  # Convert ObjectId to string
    
    return UserResponse(**user_dict) 