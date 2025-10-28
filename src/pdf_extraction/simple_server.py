#!/usr/bin/env python3

import asyncio
import json
import sys
from typing import Any, Dict, List

async def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP requests"""
    method = request.get("method")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "pdf-extraction-server",
                    "version": "0.1.0"
                }
            }
        }
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0", 
            "id": request.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "extract-pdf-contents",
                        "description": "Extract contents from a local PDF file, given page numbers separated in comma. Negative page index number supported.",
                        "inputSchema": {
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
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        tool_name = request.get("params", {}).get("name")
        arguments = request.get("params", {}).get("arguments", {})
        
        if tool_name == "extract-pdf-contents":
            pdf_path = arguments.get("pdf_path")
            pages = arguments.get("pages")
            
            if not pdf_path:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32602,
                        "message": "Missing pdf_path argument"
                    }
                }
            
            try:
                # Simple mock response for testing
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Mock PDF content extracted from {pdf_path}"
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Error: {str(e)}"
                    }
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

async def main():
    """Main server loop"""
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = await handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())