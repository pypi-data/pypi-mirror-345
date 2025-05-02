from enum import Enum
import json
from typing import Sequence
import re
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, EmbeddedResource, ImageContent
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS


class NhentaiTools(str, Enum):
    GET_NHENTAI = "get_nhentai"


class NhentaiInput(BaseModel):
    code: int = Field(description="6-digit nhentai code", ge=100000, le=999999)


async def serve() -> None:
    server = Server("mcp-nhentai")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=NhentaiTools.GET_NHENTAI.value,
                description="Extract images and metadata from a nhentai gallery using its 6-digit code.",
                inputSchema=NhentaiInput.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        if name != NhentaiTools.GET_NHENTAI.value:
            raise ValueError(f"未知工具名稱: {name}")

        try:
            args = NhentaiInput(**arguments)
        except Exception as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

        url = f"https://nhentai.net/g/{args.code}/"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state('networkidle')
            html = await page.content()
            await browser.close()

        soup = BeautifulSoup(html, "html.parser")

        matched_links = soup.find_all("a", href=re.compile(f"/g/{args.code}/\\d+/"))
        image_urls = []
        for a_tag in matched_links:
            imgs = a_tag.find_all("img")
            for img in imgs:
                src = img.get("src")
                if src:
                    image_urls.append(src)

        if not image_urls:
            return [TextContent(type="text", text=f"No images found for code {args.code}.")]

        markdown_images = "\n".join([f"![IMG]({src})" for src in image_urls])

        info_block = soup.find("div", id="info")
        title_en = info_block.find("h1", class_="title").get_text(strip=True)
        title_jp = info_block.find("h2", class_="title").get_text(strip=True)
        gallery_id = info_block.find("h3", id="gallery_id").get_text(strip=True)

        sections = info_block.find_all("div", class_="tag-container")
        metadata = {}

        for section in sections:
            label_tag = section.find(text=True, recursive=False)
            label = label_tag.strip().rstrip(":") if label_tag else "Unknown"

            tags = []
            for tag in section.select("a.tag"):
                name = tag.select_one("span.name").get_text(strip=True)
                href = tag.get("href", "")
                full_url = f"https://nhentai.net{href}"
                tags.append({"name": name, "url": full_url})

            metadata[label] = tags

        upload_time_tag = info_block.find("time")
        upload_time = upload_time_tag.get("title") if upload_time_tag else "Unknown"
        metadata["Uploaded"] = [{"name": upload_time, "url": ""}]

        info_text = f"""**Gallery Info**\n**Title (EN):** {title_en}\n**Title (JP):** {title_jp}\n**ID:** {gallery_id}\n"""

        for label, items in metadata.items():
            tag_list = ", ".join([f"[{t['name']}]({t['url']})" for t in items]) if items else "None"
            info_text += f"**{label}:** {tag_list}\n"

        return [
            TextContent(type="text", text=info_text),
            TextContent(type="text", text=f"Image URLs for code {args.code}:\n{markdown_images}")
        ]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
