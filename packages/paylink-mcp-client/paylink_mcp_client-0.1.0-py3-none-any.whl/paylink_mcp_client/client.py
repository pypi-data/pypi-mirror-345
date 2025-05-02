"""
PayLink MCP Client - A client for interacting with the PayLink MCP API.
"""
from mcp import ClientSession
import asyncio
import nest_asyncio
from mcp.client.sse import sse_client
from dotenv import load_dotenv

class PayLinkMCPClient:
    """
    Client for interacting with the PayLink MCP API.
    
    This client provides methods to connect to the server and list available tools.
    """
    
    def __init__(self, server_url="http://paylink-app.eastus.azurecontainer.io:8050/sse"):
        """
        Initialize the PayLink MCP Client.
        
        Args:
            server_url (str, optional): The server URL. If not provided, it will
                                       be loaded from environment variables.
        """
        load_dotenv(override=True)
        self.url = server_url
        # Apply nest_asyncio to allow nested event loops
        nest_asyncio.apply()
        
    async def list_tools(self):
        """
        List all available tools from the server.
        
        Returns:
            list: A list of available tools.
        """
        async with sse_client(url=self.url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()

                # List available tools
                tools = await session.list_tools()
                
                return tools
        
    async def close(self):
        """
        Close the connection to the server.
        """
        # Connection is automatically closed when exiting the context manager
        pass


# Convenience function
async def list_tools(server_url="http://paylink-app.eastus.azurecontainer.io:8050/sse"):
    """
    Convenience function to list all available tools from the server.
    
    Args:
        server_url (str, optional): The server URL. Default is the PayLink development server.
        
    Returns:
        list: A list of available tools.
    """
    client = PayLinkMCPClient(server_url)
    return await client.list_tools()