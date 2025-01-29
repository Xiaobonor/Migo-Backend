# app/models/user.py
from datetime import datetime
from typing import Optional
from mongoengine import Document, EmailField, StringField, URLField, IntField, BooleanField, DateTimeField
from pydantic import BaseModel, EmailStr, HttpUrl, Field

class User(Document):
    # Basic Information
    email = EmailField(required=True, unique=True)
    name = StringField(required=True)
    picture = URLField()
    
    # Profile Information
    nickname = StringField()
    bio = StringField()
    birthday = DateTimeField()
    gender = StringField()
    phone = StringField()
    
    # Social Information
    followers_count = IntField(default=0)
    following_count = IntField(default=0)
    
    # Preferences
    language = StringField(default="en")
    notification_enabled = BooleanField(default=True)
    theme = StringField(default="light")
    
    # System Information
    created_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    last_active = DateTimeField()
    
    # Location Information
    country = StringField()

    meta = {
        'collection': 'users'
    }

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    name: str
    picture: Optional[HttpUrl] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    language: str = "en"
    notification_enabled: bool = True
    theme: str = "light"
    created_at: datetime
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class Token(BaseModel):
    access_token: str
    token_type: str 