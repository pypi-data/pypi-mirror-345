import os
from typing import Any

from alation_ai_agent_sdk.sdk import AlationAIAgentSDK
from mcp.server.fastmcp import FastMCP


def create_server():
    # Initialize FastMCP server
    mcp = FastMCP(name="Alation MCP Server", version="0.1.0")

    # Load Alation credentials from environment variables
    base_url = os.getenv("ALATION_BASE_URL")
    user_id = int(os.getenv("ALATION_USER_ID"))
    refresh_token = os.getenv("ALATION_REFRESH_TOKEN")

    # Initialize Alation SDK
    alation_sdk = AlationAIAgentSDK(base_url, user_id, refresh_token)

    @mcp.tool(name=alation_sdk.context_tool.name)
    def alation_context(question: str, signature: dict[str, Any] | None = None) -> str:
        f"""{alation_sdk.context_tool.description}"""
        result = alation_sdk.get_context(question, signature)

        return str(result)

    return mcp


mcp = create_server()


def run_server():
    """Entry point for running the MCP server"""
    mcp.run()


if __name__ == "__main__":
    run_server()
