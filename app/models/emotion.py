from mongoengine import Document, StringField
from pydantic import BaseModel, Field

class Emotion(Document):
    name = StringField(required=True)

    meta = {
        'collection': 'emotions'
    }

class EmotionResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str

    class Config:
        from_attributes = True
        populate_by_name = True
        schema_extra = {
            "example": {
                "name": "happy"
            }
        } 