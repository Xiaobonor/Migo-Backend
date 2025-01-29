# Migo Backend Authentication API 文檔

## 基本資訊
```
Base URL: http://your-server:8000
Content-Type: application/json
版本: 1.0.0
```

## API 端點

### 1. Google 登入
使用 Google ID Token 進行登入或註冊。

```http
POST /auth/google/signin
```

#### 請求體
```json
{
    "id_token": "Google-ID-Token-String"
}
```

#### 請求標頭
```
Content-Type: application/json
```

#### 成功響應 (200 OK)
```json
{
    "access_token": "eyJhbGciOiJIUzUxMi...",
    "refresh_token": "eyJhbGciOiJIUzUxMi...",
    "token_type": "bearer",
    "expires_in": 60  // access token 過期時間（秒）
}
```

#### 錯誤響應
- 401 Unauthorized
```json
{
    "detail": "Authentication failed: {error_message}"
}
```
- 400 Bad Request
```json
{
    "detail": "Sign-in failed: {error_message}"
}
```

### 2. 刷新 Token
使用 refresh token 獲取新的 access token。
如果 refresh token 剩餘有效期不足一半，也會返回新的 refresh token。

```http
POST /auth/refresh
```

#### 請求標頭
```
Authorization: Bearer {refresh_token}
```

#### 成功響應 (200 OK)
```json
{
    "access_token": "eyJhbGciOiJIUzUxMi...",
    "refresh_token": "eyJhbGciOiJIUzUxMi...",  // 可能與原 refresh_token 相同
    "token_type": "bearer",
    "expires_in": 60
}
```

#### 錯誤響應
- 401 Unauthorized
```json
{
    "detail": "Invalid token type. Expected refresh token."
}
```
或
```json
{
    "detail": "Token has expired. Expired at 2024-03-21T10:30:00"
}
```

### 3. 獲取當前用戶資料
獲取已登入用戶的詳細資料。

```http
GET /auth/me
```

#### 請求標頭
```
Authorization: Bearer {access_token}
```

#### 成功響應 (200 OK)
```json
{
    "email": "user@example.com",
    "name": "User Name",
    "picture": "https://example.com/picture.jpg",
    "nickname": "nickname",
    "bio": "User bio",
    "birthday": "1990-01-01T00:00:00Z",
    "gender": "male",
    "phone": "+886912345678",
    "followers_count": 0,
    "following_count": 0,
    "language": "en",
    "notification_enabled": true,
    "theme": "light",
    "created_at": "2024-03-20T12:00:00Z",
    "last_login": "2024-03-20T12:00:00Z",
    "last_active": "2024-03-20T12:00:00Z",
    "country": "TW"
}
```

#### 錯誤響應
- 401 Unauthorized
```json
{
    "detail": "Could not validate credentials"
}
```
- 404 Not Found
```json
{
    "detail": "User not found"
}
```

## Token 機制說明

### Token 類型與有效期
1. Access Token
   - 用於訪問 API
   - 有效期：300 分鐘（5小時）
   - 使用 HS512 演算法加密
   - 每次過期需要使用 refresh token 獲取新的

2. Refresh Token
   - 用於獲取新的 access token
   - 有效期：43200 分鐘（30天）
   - 使用 HS512 演算法加密
   - 滾動更新機制：
     - 當剩餘有效期小於一半時（約15天），刷新時會自動更新
     - 剩餘有效期大於一半時，保持不變
     - 完全過期後需要重新登入

### Token 使用流程
1. 使用 Google 登入獲取 access_token 和 refresh_token
2. 使用 access_token 訪問 API（有效期 5 小時）
3. access_token 過期後，使用 refresh_token 獲取新的 token：
   - 如果 refresh_token 剩餘有效期 > 15天：獲取新的 access_token，refresh_token 保持不變
   - 如果 refresh_token 剩餘有效期 < 15天：同時獲取新的 access_token 和 refresh_token
4. 如果 refresh_token 完全過期（30天後），需要重新登入

### 建議的時長設置
- 當前設置：
  - ACCESS_TOKEN_EXPIRE_MINUTES=300 (5小時)
  - REFRESH_TOKEN_EXPIRE_MINUTES=43200 (30天)

## 實作說明

### Swift 實現

```swift
class AuthManager {
    static let shared = AuthManager()
    private let baseURL = "http://your-server:8000"
    
    // Google 登入
    func signInWithGoogle() async throws -> TokenResponse {
        let idToken = // 從 Google Sign-In SDK 獲取
        let body = ["id_token": idToken]
        
        var request = URLRequest(url: URL(string: "\(baseURL)/auth/google/signin")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
    
    // 刷新 Token
    func refreshToken(refreshToken: String) async throws -> TokenResponse {
        var request = URLRequest(url: URL(string: "\(baseURL)/auth/refresh")!)
        request.httpMethod = "POST"
        request.setValue("Bearer \(refreshToken)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
}

// 資料模型
struct TokenResponse: Codable {
    let access_token: String
    let refresh_token: String
    let token_type: String
    let expires_in: Int
}
```

## 安全建議
1. 使用 Keychain 安全存儲 tokens
2. 監控 access token 過期時間，在過期前主動刷新
3. 處理所有可能的錯誤情況
4. 實作重試機制
5. 使用 HTTPS 進行所有通信

## 錯誤處理
1. Token 過期
   - Access Token 過期：使用 refresh token 獲取新的 token
   - Refresh Token 過期：引導用戶重新登入

2. 網絡錯誤
   - 實作重試機制
   - 提供適當的錯誤提示

3. 驗證錯誤
   - 清除本地 tokens
   - 引導用戶重新登入

## 最佳實踐
1. 在每次請求前檢查 token 是否即將過期
2. 使用 Keychain 而不是 UserDefaults 存儲 tokens
3. 實作適當的錯誤處理和重試機制
4. 定期更新 Google Sign-In SDK
5. 監控和記錄認證相關的錯誤

## 注意事項
1. 所有請求都應使用 HTTPS
2. Access Token 應安全存儲（建議使用 Keychain）
3. 請勿在客戶端儲存敏感資訊
4. 定期檢查 Token 是否過期
5. 錯誤處理應考慮網路問題和服務器錯誤

## 安全建議
1. 在生產環境中使用 HTTPS
2. 不要在客戶端記錄敏感資訊
3. 使用 Keychain 存儲 tokens
4. 實作 token 刷新機制
5. 定期更新 Google Sign-In SDK 