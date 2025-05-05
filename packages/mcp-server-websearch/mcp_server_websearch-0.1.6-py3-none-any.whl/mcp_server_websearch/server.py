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
    # query: str = Field(description="搜尋關鍵字，建議 1~3 個詞組")
    # image: bool = Field(default=False, description="是否需要搜尋圖片")
    # video: bool = Field(default=False, description="是否需要搜尋影片")
    # safesearch: str = Field(default="0", description="安全搜尋等級 (0: 關閉, 1: 開啟)")
    # time_range: str = Field(default="", description="時間範圍 (例如 past_week, past_month)")
    # language: str = Field(default="zh-TW", description="搜尋語言")
    # categories: list[str] = Field(default=[], description="搜尋分類 (可選: general, news 等)")
    query: str = Field(
        description=
        """
        Search query used to retrieve relevant results. This should consist of 1–3 concise and meaningful keywords, separated by spaces, similar to how one would search on Google. Avoid full natural-language questions or sentences. Focus on extracting the core concepts of the query.

        Examples:
        - Instead of 'Can you find the image where Trump uses AI to make himself look like the Pope?', use 'Trump Pope AI image'
        - Instead of 'What's the weather like in Hsinchu today?', use 'Hsinchu weather today'
        - Instead of 'Help me search for a cat playing piano video', use 'cat piano video'
        """
    )
    image: bool = Field(
        default=False, description="Whether to search for images."
    )
    video: bool = Field(
        default=False, description="Whether to search for videos."
    )
    safesearch: str = Field(
        default="0", description="Safe search level (0: off, 1: on)."
    )
    time_range: str = Field(
        default="", description="Time filter (e.g., past_week, past_month)."
    )
    language: str = Field(
        default="zh-TW", description="Search language. 如果是中文時一律使用zh-TW"
    )



async def serve() -> None:
    server = Server("mcp-websearch")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=WebSearchTools.WEB_SEARCH.value,
                description='This tool should be called when the user\'s message includes keywords like "search", "what\'s the weather", "find image", "lookup video", or any request related to real-time or online information.',
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
                src = r.get("img_src", "")
                title = r.get("title", "")
                href = r.get("url", "")
                text = f"🖼️ images: src: {src}, title: {title}, url: {href}"
                results.append(TextContent(type="text", text=text))

        if args.video:
            video_results = await fetch_results("videos", ["youtube"])
            for r in video_results[:3]:
                url = r.get("url", "")
                title = r.get("title", "")
                author = r.get("author", "")
                text = f"🎥 videos: url: {url}, title: {title}, author: {author}"
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
