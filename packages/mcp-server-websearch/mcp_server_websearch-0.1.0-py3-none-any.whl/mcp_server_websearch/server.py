from enum import Enum
import json
from typing import Sequence
import httpx

from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS


class WebSearchTools(str, Enum):
    WEB_SEARCH = "web_search"


class WebSearchInput(BaseModel):
    query: str = Field(description="搜尋關鍵字，建議 1~3 個詞組")
    image: bool = Field(default=False, description="是否需要搜尋圖片")
    video: bool = Field(default=False, description="是否需要搜尋影片")
    safesearch: str = Field(default="0", description="安全搜尋等級 (0: 關閉, 1: 開啟)")
    time_range: str = Field(default="", description="時間範圍 (例如 past_week, past_month)")
    language: str = Field(default="zh-TW", description="搜尋語言")
    categories: list[str] = Field(default=[], description="搜尋分類 (可選: general, news 等)")


async def serve() -> None:
    server = Server("mcp-websearch")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=WebSearchTools.WEB_SEARCH.value,
                description="提供一般網頁、圖片與影片的搜尋能力，適用於如『請搜尋』、『天氣如何』、『找圖片』、『找影片』等『線上』或『即時』資源查詢需求。",
                inputSchema=WebSearchInput.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if name != WebSearchTools.WEB_SEARCH.value:
            raise ValueError(f"未知工具名稱: {name}")

        try:
            args = WebSearchInput(**arguments)
        except Exception as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        query_url = "https://searxng.unieai.com/search"
        accept_language = f"{args.language};q=0.9,en;q=0.8"

        async def fetch_results(category: str, engines: list[str]):
            params = {
                "q": args.query,
                "format": "json",
                "pageno": 1,
                "safesearch": args.safesearch,
                "time_range": args.time_range,
                "categories": category,
                "theme": "simple",
                "image_proxy": 0,
                "engines": ",".join(engines),
                "language": args.language,
            }

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept-Language": accept_language,
            }

            async with httpx.AsyncClient() as client:
                resp = await client.get(query_url, params=params, headers=headers, timeout=30)
                resp.raise_for_status()
                return resp.json().get("results", [])

        results = []

        if args.image:
            image_results = await fetch_results("images", ["google images", "bing images"])
            for r in image_results[:5]:
                if "img_src" in r:
                    results.append(ImageContent(url=r["img_src"], alt=r.get("title", "")))

        if args.video:
            video_results = await fetch_results("videos", ["youtube"])
            for r in video_results[:3]:
                text = f"🎥 [{r.get('title')}]({r.get('url')}) by {r.get('author', 'unknown')}"
                if r.get("thumbnail"):
                    results.append(ImageContent(url=r["thumbnail"], alt=r.get("title", "")))
                results.append(TextContent(type="text", text=text))

        if not args.image and not args.video:
            text_results = await fetch_results("general", ["google"])
            for r in text_results[:5]:
                snippet = r.get("content", "")
                link = r.get("url", "")
                title = r.get("title", "")
                text = f"🔗 [{title}]({link})\n{snippet}"
                results.append(TextContent(type="text", text=text))

        return results or [TextContent(type="text", text="沒有找到相關結果。")]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)