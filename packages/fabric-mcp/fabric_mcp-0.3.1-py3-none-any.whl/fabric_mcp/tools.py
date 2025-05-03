"""Definitions of the tools provided by the Fabric MCP server."""

from .mcp_protocol import MCPToolDefinition, MCPToolParameter

# Define the tools based on the project plan (tasks.json)
# Stubs for now, parameters will be refined later.

FABRIC_TOOLS: list[MCPToolDefinition] = [
    MCPToolDefinition(
        name="fabric_list_patterns",
        description="Lists available Fabric patterns.",
        parameters=[],  # No parameters for listing
    ),
    MCPToolDefinition(
        name="fabric_run_pattern",
        description="Runs a specified Fabric pattern with given input.",
        parameters=[
            MCPToolParameter(
                name="pattern_name",
                description="The name of the pattern to run.",
                type="string",
                required=True,
            ),
            MCPToolParameter(
                name="input_text",
                description="The primary text input for the pattern.",
                type="string",
                required=True,
            ),
            MCPToolParameter(
                name="variables",
                description="Key-value pairs for pattern variables.",
                type="object",
                required=False,
            ),
            MCPToolParameter(
                name="attachments",
                description="List of attachments for the pattern.",
                type="array",
                required=False,
            ),
            MCPToolParameter(
                name="stream",
                description="Whether to stream the response.",
                type="boolean",
                required=False,
            ),
        ],
    ),
    MCPToolDefinition(
        name="fabric_get_pattern_details",
        description="Retrieves detailed information about a specific Fabric pattern.",
        parameters=[
            MCPToolParameter(
                name="pattern_name",
                description="The name of the pattern.",
                type="string",
                required=True,
            ),
        ],
    ),
    MCPToolDefinition(
        name="fabric_list_models",
        description="Lists available models configured in Fabric.",
        parameters=[],
    ),
    MCPToolDefinition(
        name="fabric_list_strategies",
        description="Lists available strategies configured in Fabric.",
        parameters=[],
    ),
    MCPToolDefinition(
        name="fabric_get_configuration",
        description="Retrieves the current Fabric configuration.",
        parameters=[],
    ),
    # Add other tools as needed
]


def get_tools() -> list[MCPToolDefinition]:
    """Returns the list of available Fabric tools."""
    return FABRIC_TOOLS
