import os
from typing import Any
import asyncio
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import logging
logging.basicConfig(level=logging.INFO)

# Create an MCP server
server = Server("mcp-jamie-test2")

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable is not set")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出可用的工具。
    每个工具使用 JSON Schema 验证来指定其参数。
    """
    return [
        types.Tool(
            name="add",
            description="Add two numbers together123",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"}
                },
                "required": ["a"]
            }
        ),
        types.Tool(
            name="text_processing",
            description="- 支持转化英文单词的大小写 \n - 支持统计英文单词的数量",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "str", "description": "等待转化的英文单词"},
                    "operation": {"type": "str", "description": "转换类型，可选upper/lower/count"}
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="img_processing",
            description="处理图片请求",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "str",
                                "description": "图片地址"
                            }
                        },
                        "description": "图片参数，object类型",
                        "required": ["url"]
                    }
                },
                "required": ["source"]
            }
        )
    ]

async def add(a: int, b: int = 0) -> dict:
    logging.info(f"------Adding {a} and {b}")
    """Add two numbers together."""

    return {"result": a + b }

async def text_processing(text: str, operation: str = "count") -> str:
    """- 支持转化英文单词的大小写 - 支持统计英文单词的数量
    operation可选: upper/lower/count
    """
    if operation == "upper":
        return text.upper()
    elif operation == "lower":
        return text.lower()
    elif operation == "count":
        return str(len(text))
    else:
        raise ValueError("Invalid operation")

async def img_processing(source: dict) -> str:
    """图片压缩工具"""
    url = "https://api.tinify.com/shrink"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    # logging.info(f"------Processing image {image_url}")
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=source)
        return response.json()

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    处理工具执行请求。
    """
    if not arguments:
        raise ValueError("缺少参数")
    if name == "add":
        result = await add(**arguments)
        return [types.TextContent(type="text", text=f"{result}")]
    if name == "text_processing":
        result = await text_processing(**arguments)
        return [types.TextContent(type="text", text=f"{result}")]
    if name == "img_processing":
        result = await img_processing(**arguments)
        return [types.TextContent(type="text", text=f"{result}")]
    else:
        raise NotImplementedError(f"工具 {name} 不支持")



async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-demo",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())