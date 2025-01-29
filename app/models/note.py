from datetime import datetime
from typing import List, Optional
from mongoengine import Document, ReferenceField, StringField, ListField, DateTimeField, EmbeddedDocumentField
from pydantic import BaseModel, Field
from app.models.user import User
from app.models.emotion import Emotion
from app.models.media import Media, MediaResponse, MediaCreate, EmbeddedMedia

class Note(Document):
    user_id = ReferenceField(User, required=True)
    content = StringField(required=True)
    content_type = StringField(required=True)
    emotions = ListField(StringField())
    medias = ListField(EmbeddedDocumentField(EmbeddedMedia))
    created_at = DateTimeField(default=datetime.utcnow)
    location = StringField()

    meta = {
        'collection': 'notes'
    }

class NoteCreate(BaseModel):
    user_id: str
    content: str
    content_type: str
    emotions: List[str] = []
    medias: List[MediaCreate] = []
    location: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_object_id",
                "content": "I met an interesting customer today at the coffee shop...",
                "content_type": "text",
                "emotions": ["curious", "happy"],
                "medias": [{"type": "image", "url": "https://example.com/coffee.jpg"}],
                "location": "Starbucks, Main Street"
            }
        }

class NoteResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    content: str
    content_type: str
    emotions: List[str] = []
    medias: List[MediaResponse] = []
    created_at: datetime
    location: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 