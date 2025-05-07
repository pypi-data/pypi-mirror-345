from . import server
import asyncio
import os


def main():
    """Main entry point for the package."""
    tool_name = os.getenv("TOOL_NAME", "")
    if tool_name == "":
        raise ValueError("environment TOOL_NAME not exists")
    tool_desc = os.getenv("TOOL_DESC", "")
    if tool_desc == "":
        raise ValueError("environment TOOL_DESC not exists")
    asyncio.run(server.main(tool_name, tool_desc))


# Optionally expose other important items at package level
__all__ = ["main", "server"]