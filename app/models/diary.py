from datetime import datetime, date
from typing import List, Optional, Dict
from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField, StringField, ListField, BooleanField, DateTimeField, IntField, DictField, ReferenceField, ObjectIdField
from pydantic import BaseModel, Field
from app.models.user import User
from app.models.emotion import Emotion
from app.models.media import Media, MediaResponse, MediaCreate, EmbeddedMedia

class DiaryEntry(EmbeddedDocument):
    """日記中的單個條目"""
    id = ObjectIdField(default=None, primary_key=True)
    title = StringField(default="")
    content = StringField(default="")
    emotions = ListField(StringField())
    medias = ListField(EmbeddedDocumentField(EmbeddedMedia))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    tags = ListField(StringField())
    writing_time_seconds = IntField(default=0)
    imported_data = DictField()

class Diary(Document):
    """代表一天的日記"""
    user_id = ReferenceField(User, required=True)
    date = DateTimeField(default=datetime.utcnow)
    entries = ListField(EmbeddedDocumentField(DiaryEntry))
    is_public = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'diaries'
    }

class DiaryEntryCreate(BaseModel):
    """日記條目的創建模型"""
    title: str = ""
    content: str = ""
    emotions: List[str] = []
    medias: List[MediaCreate] = []
    tags: List[str] = []
    writing_time_seconds: int = 0
    imported_data: Optional[Dict] = None

class DiaryEntryResponse(BaseModel):
    """日記條目的 API 響應模型"""
    id: str = Field(alias="_id")
    title: str = ""
    content: str = ""
    emotions: List[str] = []
    medias: List[MediaResponse] = []
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    writing_time_seconds: int = 0
    imported_data: Optional[Dict] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class DiaryCreate(BaseModel):
    """日記的創建模型"""
    user_id: str
    date: Optional[datetime] = None
    entries: List[DiaryEntryCreate] = []
    is_public: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_object_id",
                "date": "2024-03-21T00:00:00Z",
                "entries": [
                    {
                        "title": "Morning Thoughts",
                        "content": "Started my day with meditation...",
                        "emotions": ["peaceful", "focused"],
                        "medias": [{"type": "image", "url": "https://example.com/morning.jpg"}],
                        "tags": ["morning", "meditation"],
                        "writing_time_seconds": 600,
                        "imported_data": {"meditation_minutes": 20}
                    }
                ],
                "is_public": False
            }
        }

class DiaryResponse(BaseModel):
    """日記的 API 響應模型"""
    id: str = Field(alias="_id")
    user_id: str
    date: datetime
    entries: List[DiaryEntryResponse] = []
    is_public: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "user_id": "user_object_id",
                "date": "2024-03-21",
                "entries": [
                    {
                        "title": "Morning Thoughts",
                        "content": "Started my day with meditation...",
                        "emotions": ["peaceful", "focused"],
                        "medias": [{"type": "image", "url": "https://example.com/morning.jpg"}],
                        "tags": ["morning", "meditation"],
                        "writing_time_seconds": 600,
                        "imported_data": {"meditation_minutes": 20}
                    },
                    {
                        "title": "Afternoon Adventures",
                        "content": "Had a great lunch with friends...",
                        "emotions": ["happy", "excited"],
                        "medias": [{"type": "image", "url": "https://example.com/lunch.jpg"}],
                        "tags": ["friends", "food"],
                        "writing_time_seconds": 900,
                        "imported_data": {"steps": 8000}
                    }
                ],
                "is_public": False
            }
        } 