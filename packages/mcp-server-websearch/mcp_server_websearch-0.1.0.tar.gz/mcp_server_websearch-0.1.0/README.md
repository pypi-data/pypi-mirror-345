version = 1
requires-python = ">=3.10"

將 config.json 添加以下內容：
```bash
        "websearch": {
            "command": "uvx",
            "args": [
                "mcp-server-websearch"
            ]
        },
```

接著使用llm時
只要"有請求查詢網路資料的意圖" 即會自動觸發本爬蟲功能