# API documentation

## auth

```http
POST /auth/login
```

用 jwt 認證身分

## file

```http
POST /file/upload
```

```http
GET /file
```

取得所有檔案

```http
GET /file/<file_name>
```

回傳檔案的資訊

- `file_name`
- `size`
- `content`

```http
PUT /file/<file_name>
```

更新某個檔案的內容

```http
DELETE /file/<file_name>
```

## task

```http
GET /task
```

取得所有任務的 uuid

```http
POST /task/<file_name>/run
```

執行 `file_name` 腳本

```http
POST /task/<uuid>/stop
```

暫停任務

```http
POST /task/<uuid>/cont
```

繼續執行任務

```http
POST /task/<uuid>/term
```

終止任務

```http
GET /task/<uuid>/status
```

取得任務狀態，會有以下欄位：

- `uuid`
- `file_name`
- `state`
    - `CREATED`
    - `RUNABLE`
    - `RUNNING`
    - `WAITING`
    - `TERMINATED`
- `return_code`
- `stdout`
- `stderr`
- `start_time`
- `pause_time`
