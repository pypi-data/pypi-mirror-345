"""
FastMCP tool definitions for Memory Bank API.
"""
from typing import List, Optional
from pydantic import Field
from fastmcp import Context


def register_tools(mcp, db):
    """Register all FastMCP tools with the provided MCP instance.
    
    Args:
        mcp: FastMCP instance
        db: Database instance
    """
    
    @mcp.tool()
    async def list_projects(ctx: Context) -> List[str]:
        """List all projects available in the memory bank."""
        await ctx.info("Listing projects from SQLite DB...")
        try:
            projects = db.list_projects()
            await ctx.info(f"Found {len(projects)} projects.")
            return projects
        except Exception as e:
            await ctx.error(f"Error listing projects: {e}")
            raise  # Re-raise error so client knows

    @mcp.tool()
    async def list_project_files(
        ctx: Context, 
        project_name: str = Field(description="Name of the project to list files from.")
    ) -> List[str]:
        """List all files in a specific project."""
        await ctx.info(f"Listing files for project '{project_name}'...")
        if not db.project_exists(project_name):
            await ctx.warning(f"Project '{project_name}' does not exist.")
            return []  # Or could raise NotFoundError
        try:
            files = db.list_files(project_name)
            await ctx.info(f"Found {len(files)} files in project '{project_name}'.")
            return files
        except Exception as e:
            await ctx.error(f"Error listing files for project '{project_name}': {e}")
            raise

    @mcp.tool()
    async def memory_bank_read(
        ctx: Context,
        project_name: str = Field(description="Name of the project containing the file."),
        file_name: str = Field(description="Name of the file to read.")
    ) -> Optional[str]:
        """Read the content of a memory bank file from a specific project."""
        await ctx.info(f"Reading file '{file_name}' from project '{project_name}'...")
        try:
            content = db.read_file(project_name, file_name)
            if content is None:
                await ctx.warning(f"File '{file_name}' not found in project '{project_name}'.")
                # Return None or could raise NotFoundError as desired
                return None
            else:
                await ctx.info(f"Successfully read file '{file_name}'.")
                return content
        except Exception as e:
            await ctx.error(f"Error reading file '{file_name}' from project '{project_name}': {e}")
            raise

    @mcp.tool()
    async def memory_bank_write(
        ctx: Context,
        project_name: str = Field(description="Name of the project to write file to."),
        file_name: str = Field(description="Name of the new file to create."),
        content: str = Field(description="Content of the new file.")
    ) -> str:
        """Create a new memory bank file in a specific project."""
        await ctx.info(f"Writing new file '{file_name}' to project '{project_name}'...")
        try:
            success = db.write_file(project_name, file_name, content)
            if success:
                await ctx.info(f"Successfully wrote file '{file_name}' to project '{project_name}'.")
                return f"Successfully wrote file '{file_name}' to project '{project_name}'."
            else:
                await ctx.warning(f"File '{file_name}' already exists in project '{project_name}'. Not overwriting.")
                # Could raise error if overwriting is not allowed and file exists
                # raise ValueError(f"File '{file_name}' already exists in project '{project_name}'.")
                return f"Error: File '{file_name}' already exists in project '{project_name}'. Not overwriting."
        except Exception as e:
            await ctx.error(f"Error writing file '{file_name}' to project '{project_name}': {e}")
            raise

    @mcp.tool()
    async def memory_bank_update(
        ctx: Context,
        project_name: str = Field(description="Name of the project containing the file to update."),
        file_name: str = Field(description="Name of the existing file to update."),
        content: str = Field(description="New content for the file.")
    ) -> str:
        """Update the content of an existing memory bank file."""
        await ctx.info(f"Updating file '{file_name}' in project '{project_name}'...")
        try:
            success = db.update_file(project_name, file_name, content)
            if success:
                await ctx.info(f"Successfully updated file '{file_name}' in project '{project_name}'.")
                return f"Successfully updated file '{file_name}' in project '{project_name}'."
            else:
                await ctx.warning(f"File '{file_name}' not found in project '{project_name}'. Cannot update.")
                # Could raise NotFoundError
                # raise NotFoundError(f"File '{file_name}' not found in project '{project_name}'.")
                return f"Error: File '{file_name}' not found in project '{project_name}'. Cannot update."
        except Exception as e:
            await ctx.error(f"Error updating file '{file_name}' in project '{project_name}': {e}")
            raise

    return {
        "list_projects": list_projects,
        "list_project_files": list_project_files,
        "memory_bank_read": memory_bank_read,
        "memory_bank_write": memory_bank_write,
        "memory_bank_update": memory_bank_update
    }