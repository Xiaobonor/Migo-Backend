# Diary API 文檔

## 創建或更新日記條目

```
POST /diaries
```

### 請求體
創建新條目時不需要提供 `_id`；更新現有條目時需要提供 `_id`。
所有字段都是可選的，支持部分更新。

```json
{
    "user_id": "user_object_id",
    "date": "2024-03-21",  // 可選，默認為當天
    "title": "Morning Thoughts",
    "content": "Started my day with meditation...",
    "emotions": ["peaceful", "focused"],
    "medias": [
        {"type": "image", "url": "https://example.com/morning.jpg"}
    ],
    "tags": ["morning", "meditation"],
    "writing_time_seconds": 600,
    "imported_data": {
        "meditation_minutes": 20
    }
}
```

### 響應

- 201 Created
```json
{
    "_id": "diary_object_id",
    "user_id": "user_object_id",
    "date": "2024-03-21",
    "entries": [
        {
            "_id": "entry_object_id_1",
            "title": "Morning Thoughts",
            "content": "Started my day with meditation...",
            "emotions": ["peaceful", "focused"],
            "medias": [
                {"type": "image", "url": "https://example.com/morning.jpg"}
            ],
            "tags": ["morning", "meditation"],
            "writing_time_seconds": 600,
            "imported_data": {
                "meditation_minutes": 20
            },
            "created_at": "2024-03-21T09:00:00",
            "updated_at": "2024-03-21T09:00:00"
        },
        {
            "_id": "entry_object_id_2",
            "title": "Afternoon Adventures",
            "content": "Had a great lunch with friends...",
            "emotions": ["happy", "excited"],
            "medias": [
                {"type": "image", "url": "https://example.com/lunch.jpg"}
            ],
            "tags": ["friends", "food"],
            "writing_time_seconds": 900,
            "imported_data": {
                "steps": 8000
            },
            "created_at": "2024-03-21T14:00:00",
            "updated_at": "2024-03-21T14:00:00"
        }
    ],
    "is_public": false,
    "created_at": "2024-03-21T09:00:00",
    "updated_at": "2024-03-21T14:00:00"
}
```
- 400 Bad Request

## 獲取日記列表

```
GET /diaries
```

### 參數

- `skip`: 跳過的日記數量，默認為0
- `limit`: 返回的日記數量，默認為100
- `start_date`: 開始日期（可選）
- `end_date`: 結束日期（可選）
- `user_id`: 用戶ID（必須）

### 響應

- 200 OK

## 獲取指定日期的日記

```
GET /diaries/by-date/{date}
```

### 參數

- `date`: 日期，格式為 YYYY-MM-DD
- `user_id`: 用戶ID（必須）

### 響應

- 200 OK
- 404 Not Found

## 獲取單個日記

```
GET /diaries/{id}
```

### 參數

- `id`: 日記的ID

### 響應

- 200 OK
- 404 Not Found

## 刪除日記

```
DELETE /diaries/{id}
```

### 參數

- `id`: 日記的ID

### 響應

- 204 No Content
- 404 Not Found

## 刪除日記條目

```
DELETE /diaries/{diary_id}/entries/{entry_id}
```

### 參數

- `diary_id`: 日記的ID
- `entry_id`: 條目的ID

### 響應

- 204 No Content
- 404 Not Found

## AI情感分析

```
POST /diaries/{id}/analyze
```

### 參數

- `id`: 日記的ID

### 響應

- 200 OK

## 獲取日記統計

```
GET /diaries/stats
```

### 參數

- `user_id`: 用戶ID（必須）
- `start_date`: 開始日期（可選）
- `end_date`: 結束日期（可選）

### 響應

- 200 OK

```json
{
    "emotion_distribution": {
        "happy": 0.6,
        "excited": 0.3,
        "sad": 0.1
    },
    "monthly_report": [
        {
            "month": "2024-03",
            "total_entries": 45,
            "entries_per_day": 1.5,
            "top_emotions": ["happy", "relaxed"]
        }
    ]
} 