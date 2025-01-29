from fastapi import APIRouter, Body, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Dict, Any
from app.models.diary import (
    Diary, DiaryEntry, DiaryResponse, DiaryEntryResponse,
    DiaryCreate, DiaryEntryCreate
)
from app.models.user import User
from app.models.media import EmbeddedMedia, MediaResponse
from datetime import datetime, date
from bson import ObjectId
import logging

router = APIRouter(
    tags=["diaries"],
)

@router.post("/", response_description="Add new diary entry", status_code=status.HTTP_201_CREATED, response_model=DiaryResponse)
def create_or_update_diary(diary_data: DiaryCreate):
    """
    創建或更新日記條目。
    如果該日期的日記不存在，會自動創建；如果已存在，則添加新條目或更新現有條目。
    """
    try:
        # 驗證用戶存在
        user = User.objects(id=diary_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        entry_date = diary_data.date or datetime.utcnow()
        
        # 查找或創建該日的日記
        diary = Diary.objects(user_id=user, date=entry_date).first()
        if not diary:
            diary = Diary(user_id=user, date=entry_date)
        
        # 處理每個條目
        for entry_data in diary_data.entries:
            # 創建媒體對象
            media_objects = []
            for media_data in entry_data.medias:
                media = EmbeddedMedia(
                    id=ObjectId(),
                    type=media_data.type,
                    url=media_data.url,
                    description=media_data.description
                )
                media_objects.append(media)
            
            # 創建日記條目
            entry = DiaryEntry(
                id=ObjectId(),
                title=entry_data.title,
                content=entry_data.content,
                emotions=entry_data.emotions,
                medias=media_objects,
                tags=entry_data.tags,
                writing_time_seconds=entry_data.writing_time_seconds,
                imported_data=entry_data.imported_data
            )
            diary.entries.append(entry)
        
        diary.is_public = diary_data.is_public
        diary.updated_at = datetime.utcnow()
        diary.save()
        
        return create_diary_response(diary)
            
    except Exception as e:
        logging.error(f"Error creating/updating diary entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid diary data: {str(e)}"
        )

@router.get("/", response_description="List all diaries", response_model=List[DiaryResponse])
def list_diaries(
    skip: int = 0,
    limit: int = 100,
    start_date: date = Query(None, description="Start date for diary list"),
    end_date: date = Query(None, description="End date for diary list"),
    user_id: str = Query(..., description="Filter diaries by user ID")
):
    """獲取日記列表，支持日期範圍篩選"""
    try:
        # 驗證用戶存在
        user = User.objects(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        query = {"user_id": user}
        if start_date and end_date:
            query["date__gte"] = start_date
            query["date__lte"] = end_date
        elif start_date:
            query["date__gte"] = start_date
        elif end_date:
            query["date__lte"] = end_date
        
        diaries = Diary.objects(**query).order_by("-date").skip(skip).limit(limit)
        return [create_diary_response(diary) for diary in diaries]
    except Exception as e:
        logging.error(f"Error listing diaries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{id}", response_description="Get a single diary", response_model=DiaryResponse)
def get_diary(id: str):
    """獲取單個日記的詳細信息"""
    try:
        diary = Diary.objects(id=id).first()
        if not diary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diary {id} not found"
            )
        return create_diary_response(diary)
    except Exception as e:
        logging.error(f"Error getting diary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/by-date/{date}", response_description="Get diary for a specific date", response_model=DiaryResponse)
def get_diary_by_date(
    date: date,
    user_id: str = Query(..., description="Filter diary by user ID")
):
    """獲取指定日期的日記"""
    try:
        user = User.objects(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        diary = Diary.objects(user_id=user, date=date).first()
        if not diary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Diary for date {date} not found"
            )
        return create_diary_response(diary)
    except Exception as e:
        logging.error(f"Error getting diary by date: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def create_diary_response(diary: Diary) -> DiaryResponse:
    """創建日記響應對象"""
    return DiaryResponse(
        _id=str(diary.id),
        user_id=str(diary.user_id.id),
        date=diary.date,
        entries=[
            DiaryEntryResponse(
                _id=str(entry.id),
                title=entry.title,
                content=entry.content,
                emotions=entry.emotions,
                medias=[
                    MediaResponse(
                        _id=str(m.id),
                        type=m.type,
                        url=m.url,
                        description=m.description
                    ) for m in entry.medias
                ],
                created_at=entry.created_at,
                updated_at=entry.updated_at,
                tags=entry.tags,
                writing_time_seconds=entry.writing_time_seconds,
                imported_data=entry.imported_data
            ) for entry in diary.entries
        ],
        is_public=diary.is_public,
        created_at=diary.created_at,
        updated_at=diary.updated_at
    )

@router.delete("/{id}", response_description="Delete a diary")
def delete_diary(id: str):
    """刪除指定的日記"""
    delete_result = Diary.objects(id=id).delete()
    if delete_result == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Diary {id} not found")

@router.delete("/{diary_id}/entries/{entry_id}", response_description="Delete a diary entry")
def delete_diary_entry(diary_id: str, entry_id: str):
    """刪除日記中的特定條目"""
    diary = Diary.objects(id=diary_id).first()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Diary {diary_id} not found")
    
    # 移除指定的條目
    diary.entries = [entry for entry in diary.entries if str(entry.id) != entry_id]
    diary.updated_at = datetime.utcnow()
    diary.save()
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{id}/analyze", response_description="Analyze a diary")
def analyze_diary(id: str):
    """
    對日記進行AI分析
    分析結果將保存在單獨的集合中，不會修改原始日記
    """
    # TODO: Call AI service to analyze the diary
    # Save the analysis result to a separate collection
    pass

@router.get("/stats", response_description="Get diary statistics")
def get_diary_stats(
    user_id: str = Query(..., description="Get stats for specific user"),
    start_date: date = Query(None, description="Start date for stats"),
    end_date: date = Query(None, description="End date for stats")
):
    """獲取日記統計信息，包括情感分佈、月度報告等"""
    # TODO: Calculate and return diary statistics
    pass 