# app/utils/auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.utils.config import get_settings
import uuid
import logging

# 設置日誌
logger = logging.getLogger(__name__)

settings = get_settings()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    創建 access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    # 添加額外的安全聲明
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # 令牌簽發時間
        "jti": str(uuid.uuid4()),  # 唯一標識符
        "type": "access"  # 令牌類型
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    創建 refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    # 添加額外的安全聲明
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "type": "refresh"
    })
    
    logger.info(f"Creating refresh token with expiration: {expire}")
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Tuple[str, Optional[datetime]]:
    """
    驗證 token，返回 email 和過期時間（如果是 refresh token）
    """
    try:
        # 解碼並驗證 token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # 驗證令牌類型
        token_type_from_payload = payload.get("type")
        if token_type_from_payload != token_type:
            logger.error(f"Invalid token type. Expected {token_type}, got {token_type_from_payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type} token."
            )
        
        # 驗證過期時間
        exp = payload.get("exp")
        if not exp:
            logger.error("Token missing expiration time")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing expiration time"
            )
            
        current_time = datetime.utcnow()
        expiration_time = datetime.fromtimestamp(exp)
        
        if current_time >= expiration_time:
            logger.error(f"Token expired. Current time: {current_time}, Expiration time: {expiration_time}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token has expired. Expired at {expiration_time}"
            )
            
        # 驗證必要欄位
        email: str = payload.get("sub")
        if email is None:
            logger.error("Token missing subject (email)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: missing subject"
            )
            
        # 如果是 refresh token，返回過期時間；如果是 access token，返回 None
        return email, expiration_time if token_type == "refresh" else None
        
    except JWTError as e:
        logger.error(f"JWT verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

def refresh_tokens(refresh_token: str) -> Dict[str, str]:
    """
    使用 refresh token 刷新 access token 和 refresh token
    實現滾動更新機制：如果 refresh token 還有超過一半的有效期，則保持不變；
    否則生成新的 refresh token
    """
    try:
        email, expiration_time = verify_token(refresh_token, "refresh")
        
        # 計算 refresh token 剩餘有效期
        current_time = datetime.utcnow()
        time_until_expiry = expiration_time - current_time
        total_validity = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        # 創建新的 access token
        access_token = create_access_token({"sub": email})
        
        # 如果 refresh token 剩餘有效期小於一半，創建新的 refresh token
        if time_until_expiry < (total_validity / 2):
            logger.info("Creating new refresh token due to approaching expiration")
            refresh_token = create_refresh_token({"sub": email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        logger.error(f"Error refreshing tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) 