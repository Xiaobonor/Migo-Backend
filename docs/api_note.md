# Note API 文檔

## 創建隨手記

```
POST /notes
```

### 請求體

```json
{
    "user_id": "user_object_id",
    "content": "I met an interesting customer today at the coffee shop...",
    "content_type": "text",
    "emotions": ["curious", "happy"],
    "medias": [
        {"type": "image", "url": "https://example.com/coffee.jpg"}
    ],
    "location": "Starbucks, Main Street"
}
```

### 響應

- 201 Created
- 400 Bad Request

## 獲取隨手記列表

```
GET /notes
```

### 參數

- `skip`: 跳過的隨手記數量，默認為0
- `limit`: 返回的隨手記數量，默認為100

### 響應

- 200 OK

```json
[
    {
        "_id": "note_object_id",
        "user_id": "user_object_id",
        "content": "I met an interesting customer today at the coffee shop...",
        "content_type": "text",
        "emotions": ["curious", "happy"],
        "medias": [
            {"_id": "media_object_id", "type": "image", "url": "https://example.com/coffee.jpg"}
        ],
        "location": "Starbucks, Main Street",
        "created_at": "2023-06-01T10:30:00"
    }
]
``` 