from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from app.models.note import Note, NoteCreate, NoteResponse
from app.models.user import User
from app.models.media import EmbeddedMedia, MediaResponse
from bson import ObjectId
import logging

router = APIRouter(
    tags=["notes"],
)

@router.post("/", response_description="Add new note", status_code=status.HTTP_201_CREATED, response_model=NoteResponse)
def create_note(note_data: NoteCreate):
    try:
        # 驗證用戶存在
        user = User.objects(id=note_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 創建媒體對象
        media_objects = []
        for media_data in note_data.medias:
            media = EmbeddedMedia(
                id=ObjectId(),
                type=media_data.type,
                url=media_data.url,
                description=media_data.description
            )
            media_objects.append(media)
        
        # 創建筆記
        note = Note(
            user_id=user,
            content=note_data.content,
            content_type=note_data.content_type,
            emotions=note_data.emotions,
            medias=media_objects,
            location=note_data.location
        )
        note.save()
        
        return create_note_response(note)
    except Exception as e:
        logging.error(f"Error creating note: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_description="List all notes", response_model=List[NoteResponse])
def list_notes(skip: int = 0, limit: int = 100):
    try:
        notes = Note.objects().skip(skip).limit(limit)
        return [create_note_response(note) for note in notes]
    except Exception as e:
        logging.error(f"Error listing notes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def create_note_response(note: Note) -> NoteResponse:
    """創建筆記響應對象"""
    return NoteResponse(
        _id=str(note.id),
        user_id=str(note.user_id.id),
        content=note.content,
        content_type=note.content_type,
        emotions=note.emotions,
        medias=[
            MediaResponse(
                _id=str(m.id) if hasattr(m, 'id') else None,
                type=m.type,
                url=m.url,
                description=m.description
            ) for m in note.medias
        ],
        created_at=note.created_at,
        location=note.location
    ) 