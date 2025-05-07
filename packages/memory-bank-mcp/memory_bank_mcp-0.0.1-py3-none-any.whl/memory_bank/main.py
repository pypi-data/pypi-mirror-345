"""
Memory Bank - FastMCP application entry point.

This application provides a memory storage system for projects and files
using FastMCP and SQLite.
"""
from fastmcp import FastMCP
from memory_bank.config import settings
from memory_bank.db_init import init_db
from memory_bank.database.database import Database
from memory_bank.api.tools import register_tools


def main():
    """Initialize and run the Memory Bank FastMCP server."""
    # Initialize database and ensure tables exist
    init_db()

    # Create database connection
    db = Database(settings.db_path)

    # Initialize FastMCP server
    mcp = FastMCP(
        name="MemoryBankFastMCP",
        dependencies=["fastmcp", "pydantic-settings"]
    )

    # Register all tools with the MCP instance
    register_tools(mcp, db)

    # Start the server
    print(
        f"Starting Memory Bank Server (FastMCP) with DB at: {settings.db_path.resolve()}")

    # Default: run on stdio
    # mcp.run()

    # To run on SSE (Server-Sent Events) over network:
    mcp.run(transport="sse", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()