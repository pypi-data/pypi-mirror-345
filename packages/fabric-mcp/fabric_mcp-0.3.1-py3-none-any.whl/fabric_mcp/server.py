"""Core MCP server logic for Fabric integration."""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional, Union

from pydantic import ValidationError

from .mcp_protocol import (
    FabricRunPatternParams,
    FabricRunPatternResult,
    MCPError,
    MCPListToolsResponse,
    MCPRequest,
    MCPResponse,
)
from .tools import get_tools

# --- Error Codes (Example) ---
# Follow JSON-RPC 2.0 spec: https://www.jsonrpc.org/specification#error_object
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
# Application specific errors: -32000 to -32099


# --- Request Handlers ---


async def handle_list_tools(request: MCPRequest) -> MCPResponse:
    """Handles the list_tools request."""
    logging.info("Handling list_tools request")
    try:
        tools = get_tools()
        result = MCPListToolsResponse(tools=tools)
        return MCPResponse(result=result, id=request.id)
    except Exception as e:
        logging.exception("Error handling list_tools")
        error = MCPError(code=INTERNAL_ERROR, message=f"Internal server error: {e}")
        return MCPResponse(error=error, id=request.id)


async def handle_fabric_run_pattern(request: MCPRequest) -> MCPResponse:
    """Handles the fabric_run_pattern request."""
    logging.info("Handling fabric_run_pattern request")
    if request.params is None:
        error = MCPError(
            code=INVALID_PARAMS, message="Missing parameters for fabric_run_pattern"
        )
        return MCPResponse(error=error, id=request.id)

    try:
        params = FabricRunPatternParams.model_validate(request.params)
        logging.debug("Validated params: %s", params)

        # --- Placeholder for actual Fabric logic ---
        logging.info("Simulating run of pattern: %s", params.pattern_name)
        await asyncio.sleep(0.1)  # Simulate some work
        # Shorten the input string preview logic
        input_preview = params.input_text
        if len(params.input_text) > 20:
            input_preview = f"{params.input_text[:20]}..."

        output_text = (
            f"Ran pattern '{params.pattern_name}' with input: '{input_preview}'"
        )
        # --- End Placeholder ---

        result = FabricRunPatternResult(output=output_text)
        return MCPResponse(result=result, id=request.id)

    except ValidationError as e:
        logging.error("Invalid parameters for fabric_run_pattern: %s", e)
        error = MCPError(code=INVALID_PARAMS, message=f"Invalid parameters: {e}")
        return MCPResponse(error=error, id=request.id)
    except Exception as e:
        logging.exception("Error handling fabric_run_pattern")
        error = MCPError(code=INTERNAL_ERROR, message=f"Internal server error: {e}")
        return MCPResponse(error=error, id=request.id)


# --- Add handlers for other methods here ---
# async def handle_fabric_run_pattern(request: MCPRequest) -> MCPResponse:
#     pass # Implement later

# --- Request Dispatcher ---

METHOD_HANDLERS = {
    "list_tools": handle_list_tools,
    "fabric_run_pattern": handle_fabric_run_pattern,
}


async def dispatch_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parses, validates, and dispatches an incoming request."""
    request_id: Optional[Union[str, int]] = request_data.get("id")
    try:
        request = MCPRequest.model_validate(request_data)
    except ValidationError as e:
        logging.error("Invalid request format: %s", e)
        error = MCPError(code=INVALID_REQUEST, message=f"Invalid request: {e}")
        # ID might be null if parsing failed early
        return MCPResponse(error=error, id=request_id).model_dump(exclude_none=True)

    handler = METHOD_HANDLERS.get(request.method)
    if not handler:
        logging.warning("Method not found: %s", request.method)
        error = MCPError(
            code=METHOD_NOT_FOUND,
            message=f"Method '{request.method}' not found",
        )
        return MCPResponse(error=error, id=request.id).model_dump(exclude_none=True)

    try:
        response = await handler(request)
        return response.model_dump(exclude_none=True)
    except Exception as e:
        # Catch unexpected errors in handlers
        logging.exception("Unhandled error during method execution: %s", request.method)
        error = MCPError(
            code=INTERNAL_ERROR,
            message=f"Internal server error during method execution: {e}",
        )
        return MCPResponse(error=error, id=request.id).model_dump(exclude_none=True)


# --- Main Server Loop (stdio) ---


async def run_server_stdio():
    """Runs the MCP server, reading from stdin and writing to stdout."""
    logging.info("MCP Server starting (stdio transport)")
    loop = asyncio.get_running_loop()

    def read_stdin():
        return sys.stdin.readline()

    while True:
        line = await loop.run_in_executor(None, read_stdin)
        if not line:
            logging.info("EOF received, shutting down.")
            break

        logging.debug("Received line: %s", line.strip())
        try:
            request_data = json.loads(line)
            if not isinstance(request_data, dict):
                raise ValueError("Request must be a JSON object")
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON: %s", line.strip())
            error_response = MCPResponse(
                error=MCPError(
                    code=PARSE_ERROR, message="Failed to parse JSON request"
                ),
                id=None,  # ID is unknown if parsing failed
            ).model_dump(exclude_none=True)
            print(json.dumps(error_response), flush=True)
            continue
        except ValueError as e:
            logging.error("Invalid request structure: %s", e)
            error_response = MCPResponse(
                error=MCPError(code=INVALID_REQUEST, message=str(e)),
                id=request_data.get("id") if isinstance(request_data, dict) else None,
            ).model_dump(exclude_none=True)
            print(json.dumps(error_response), flush=True)
            continue

        response_data = await dispatch_request(request_data)
        response_json = json.dumps(response_data)
        logging.debug("Sending response: %s", response_json)
        print(response_json, flush=True)

    logging.info("MCP Server stopped.")
