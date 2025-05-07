# Memory Bank

A FastMCP-based service for storing and retrieving project files in a SQLite database.

## Overview

Memory Bank provides a simple file storage system organized by projects, allowing you to:

- List all available projects
- List files within a project
- Read file contents
- Write new files
- Update existing files

All data is stored in a SQLite database for persistence.

## Installation

### From PyPI

```bash
pip install memory-bank-mcp
```

### From Source

1. Clone this repository
2. Install dependencies:

```bash
uv sync --dev
```

## Configuration

Environment variables can be set in a `.env` file in the project root:

```
# .env file
DB_PATH=./data/memory_bank.db
```

## Running the Server

```bash
python main.py
```

By default, the server runs on stdio. To run on SSE (Server-Sent Events) over network, modify `main.py`:

```python
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

## API Tools

### List Projects

Lists all projects in the memory bank.

### List Project Files

Lists all files in a specific project.

### Read File

Reads the content of a specific file from a project.

### Write File

Creates a new file in a project. Will not overwrite existing files.

### Update File

Updates the content of an existing file in a project.

## Project Structure

```
memory_bank/
├── .env                    # Environment variables configuration
├── README.md               # Project documentation 
├── main.py                 # Application entry point
├── db_init.py              # Database initialization scripts
├── config.py               # Configuration settings
├── database/
│   └── database.py         # Database connection and operations
└── api/
    ├── __init__.py         # API package initialization
    └── tools.py            # FastMCP tool definitions
```
