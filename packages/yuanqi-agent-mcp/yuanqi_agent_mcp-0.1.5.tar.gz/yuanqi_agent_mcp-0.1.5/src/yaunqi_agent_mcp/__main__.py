from . import server
import asyncio
import os


def main():
    """Main entry point for the package."""
    tool_name = os.getenv("TOOL_NAME", None)
    if tool_name is None:
        raise ValueError("environment TOOL_NAME not exists")
    tool_desc = os.getenv("TOOL_DESC", None)
    if tool_desc is None:
        raise ValueError("environment TOOL_DESC not exists")
    asyncio.run(server.main(tool_name, tool_desc))


# Optionally expose other important items at package level
main()
