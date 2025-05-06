import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic

from .utils import get_timeplus_env_config


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 1000

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=get_timeplus_env_config()
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def get_available_tools(self):
        """Get list of available tools in the format required by Claude API"""
        response = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools with reactive pattern support"""
        # Initialize conversation with the user query
        messages = [{"role": "user", "content": query}]

        # Get available tools
        available_tools = await self.get_available_tools()

        # Track all responses for final output
        all_responses = []

        # Continue conversation until Claude has no more tool calls to make
        while True:
            # Call Claude with current conversation state
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=messages,
                tools=available_tools,
            )

            # Process the response
            has_tool_calls = False
            assistant_message_content = []

            for content in response.content:
                if content.type == "text":
                    # Store text response
                    all_responses.append(content.text)
                    assistant_message_content.append(content)

                elif content.type == "tool_use":
                    # Found a tool call
                    has_tool_calls = True
                    tool_name = content.name
                    tool_args = content.input

                    # Log the tool call
                    tool_call_msg = f"[Calling tool {tool_name} with args {tool_args}]"
                    all_responses.append(tool_call_msg)

                    # Execute the tool call
                    result = await self.session.call_tool(tool_name, tool_args)

                    # Append the assistant's message with the tool call
                    assistant_message_content.append(content)

                    # Update messages with this assistant response
                    messages.append(
                        {"role": "assistant", "content": assistant_message_content}
                    )

                    # Add tool result as user message
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": result.content,
                                }
                            ],
                        }
                    )

                    # We've handled this tool call, break to process next Claude response
                    break

            # If no tool calls were made, add assistant's message and exit the loop
            if not has_tool_calls:
                # If there's any remaining text content to add, add it to messages
                if assistant_message_content:
                    messages.append(
                        {"role": "assistant", "content": assistant_message_content}
                    )
                break

            # Loop continues if there were tool calls, allowing Claude to make multiple calls

        return "\n".join(all_responses)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
