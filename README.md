# Migo Backend

Migo 是一個基於 FastAPI 的後端服務，為 iOS Migo App 提供 API 支持。

## 文檔

### API 文檔
- [認證 API 文檔](docs/api_auth.md) - 包含登入和用戶認證相關的 API

## 開發環境設置

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 設置環境變數：
```bash
cp .env.example .env
# 編輯 .env 文件，填入必要的配置
```

3. 運行服務器：
```bash
python run.py
```

## 技術棧
- FastAPI
- MongoDB
- Google OAuth
- JWT Authentication

## 開發指南
詳細的開發指南請參考各個 API 文檔。

## 貢獻指南
1. Fork 本專案
2. 創建新的分支
3. 提交更改
4. 發起 Pull Request

## 授權
本專案採用 MIT 授權。

## 數據庫配置

應用程序使用 MongoDB 作為數據庫。要連接到 MongoDB，需要設置 `MONGODB_URI` 環境變量。

### 設置 `MONGODB_URI` 環境變量

1. 創建一個名為 `.env` 的文件，放在項目根目錄下。

2. 在 `.env` 文件中，添加以下內容：

   ```
   MONGODB_URI=mongodb://localhost:27017/migo
   ```

   將 `localhost` 替換為 MongoDB 服務器的主機名，`27017` 替換為 MongoDB 的端口號，`migo` 替換為要使用的數據庫名稱。

3. 保存 `.env` 文件。

### 連接到 MongoDB

應用程序在啟動時會自動連接到 MongoDB。連接邏輯在 `app/utils/database.py` 文件中的 `init_db()` 函數中定義。

`init_db()` 函數會從 `.env` 文件中加載 `MONGODB_URI` 環境變量，並使用該變量作為連接字符串來連接到 MongoDB。如果 `MONGODB_URI` 環境變量未設置，則使用默認的連接字符串 `mongodb://localhost:27017/migo`。

在連接到 MongoDB 之前，`init_db()` 函數會先斷開任何現有的連接，以確保每次啟動應用程序時都使用新的連接。
