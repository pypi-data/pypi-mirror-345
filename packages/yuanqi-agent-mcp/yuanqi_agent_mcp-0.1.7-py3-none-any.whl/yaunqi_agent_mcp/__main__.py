from . import server
# import server
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
# os.environ["API_KEY"] = "HyENsa3tNVoIAb0HBLJTcVSAb2fdsN7l"
# os.environ["ASSISTANT_ID"] = "ay9y3OW4Pjkddd"
# os.environ["TOOL_DESC"] = "chat with yuanqi agent"
# os.environ["TOOL_NAME"] = "chat"
# arguments = {
#     "userID": "123",
#     "userPrompt":"你是谁"
# }
# server.yuanqi_chat(arguments)