#!/usr/bin/env python3

import asyncio
import logging
from typing import Any
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from .pdf_extractor import PDFExtractor

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建服务器实例
server = Server("pdf-extraction-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="extract-pdf-contents",
            description="Extract contents from a local PDF file, given page numbers separated in comma. Negative page index number supported.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the PDF file"
                    },
                    "pages": {
                        "type": "string",
                        "description": "Page numbers separated by comma (optional)"
                    }
                },
                "required": ["pdf_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if name != "extract-pdf-contents":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    pdf_path = arguments.get("pdf_path")
    pages = arguments.get("pages")

    if not pdf_path:
        raise ValueError("Missing pdf_path argument")

    try:
        extractor = PDFExtractor()
        extracted_text = extractor.extract_content(pdf_path, pages)

        return [
            types.TextContent(
                type="text",
                text=extracted_text
            )
        ]
    except Exception as e:
        logger.error(f"Error extracting PDF content: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

async def main():
    """Main entry point for the MCP server."""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pdf-extraction-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())