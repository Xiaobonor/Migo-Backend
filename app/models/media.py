from typing import Optional
from mongoengine import Document, EmbeddedDocument, StringField, ObjectIdField
from pydantic import BaseModel, Field

class Media(Document):
    type = StringField(required=True)
    url = StringField(required=True)
    description = StringField(default="")

    meta = {
        'collection': 'medias'
    }

class EmbeddedMedia(EmbeddedDocument):
    id = ObjectIdField(default=None, primary_key=True)
    type = StringField(required=True)
    url = StringField(required=True)
    description = StringField(default="")

class MediaCreate(BaseModel):
    type: str
    url: str
    description: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "type": "image",
                "url": "https://example.com/image.jpg",
                "description": "The beautiful sunset I saw today"
            }
        }

class MediaResponse(BaseModel):
    id: str = Field(alias="_id")
    type: str
    url: str
    description: str = ""

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "type": "image",
                "url": "https://example.com/image.jpg",
                "description": "The beautiful sunset I saw today"
            }
        } 