import asyncio
import os
from typing import Any, Optional, List, Dict
from mcp.server.fastmcp import FastMCP
from manychat_mcp_server.manychat import ManyChatClient
from manychat_mcp_server.ManyChatPage import ManyChatPage

# Initialize MCP server
mcp = FastMCP("manychat_tools")
manychat_page = ManyChatPage()

@mcp.tool()
async def send_instagram_message(
    subscriber_id: int,
    message: str,
    message_tag: str = "ACCOUNT_UPDATE",
) -> str:
    """Send a basic Instagram message using ManyChat API."""
    return await ManyChatClient.send_text_message(subscriber_id, message, message_tag)

@mcp.tool()
async def send_instagram_flow(
    subscriber_id: str,
    flow_ns: str,
) -> dict[str, Any]:
    """Send a flow to an Instagram subscriber using ManyChat API."""
    return await ManyChatClient.send_flow(subscriber_id, flow_ns)

@mcp.tool()
async def get_page_info() -> Dict[str, Any]:
    """
    Get information about the connected ManyChat page.
    
    Returns:
        dict: ManyChat page information or error details.
    """
    return await manychat_page.get_page_info()

@mcp.tool()
async def create_tag(
    name: str
) -> Dict[str, Any]:
    """
    Create a new tag in ManyChat.
    
    Parameters:
        name (str): The name of the tag to create.
        
    Returns:
        dict: API response from ManyChat.
    """
    return await manychat_page.create_tag(name)

@mcp.tool()
async def get_tags() -> Dict[str, Any]:
    """
    Fetch all tags from the ManyChat page.
    
    Returns:
        dict: A response containing a list of tags or error info.
    """
    return await manychat_page.get_tags()

@mcp.tool()
async def remove_tag(
    tag_id: Optional[int] = None,
    tag_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Remove a tag from ManyChat by ID or name.
    
    Parameters:
        tag_id (int, optional): The ID of the tag to remove.
        tag_name (str, optional): The name of the tag to remove.
        
    Returns:
        dict: API response from ManyChat.
    """
    return await manychat_page.remove_tag(tag_id, tag_name)

@mcp.tool()
async def create_custom_field(
    caption: str,
    field_type: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a custom field in ManyChat.
    
    Parameters:
        caption (str): The display name of the custom field.
        field_type (str): Type of field. Valid types: text, number, date, datetime, boolean, etc.
        description (str): Optional description for the custom field.
        
    Returns:
        dict: API response from ManyChat.
    """
    return await manychat_page.create_custom_field(caption, field_type, description)

@mcp.tool()
async def get_growth_tools() -> Dict[str, Any]:
    """
    Fetch all Growth Tools associated with the page.
    
    Returns:
        dict: A response containing a list of growth tools or error info.
    """
    return await manychat_page.get_growth_tools()

@mcp.tool()
async def get_flows() -> Dict[str, Any]:
    """
    Retrieve all flows and folders from the ManyChat page.
    
    Returns:
        dict: Contains list of flows and folders or error details.
    """
    return await manychat_page.get_flows()

@mcp.tool()
async def get_custom_fields() -> Dict[str, Any]:
    """
    Fetch all custom fields from the ManyChat page.
    
    Returns:
        dict: A response containing a list of custom fields or error info.
    """
    return await manychat_page.get_custom_fields()

@mcp.tool()
async def get_otn_topics() -> Dict[str, Any]:
    """
    Fetch all OTN topics from the ManyChat page.
    
    Returns:
        dict: A response containing a list of OTN topics or error info.
    """
    return await manychat_page.get_otn_topics()

@mcp.tool()
async def get_bot_fields() -> Dict[str, Any]:
    """
    Fetch all bot fields from the ManyChat page.
    
    Returns:
        dict: A response containing a list of bot fields or error info.
    """
    return await manychat_page.get_bot_fields()

@mcp.tool()
async def create_bot_field(
    name: str,
    field_type: str,
    description: str = "",
    value: str = ""
) -> Dict[str, Any]:
    """
    Create a bot field in ManyChat.
    
    Parameters:
        name (str): The name of the bot field.
        field_type (str): The type of the field (text, number, boolean, etc.).
        description (str): A description of the field.
        value (str): The value for the field (can be string, number, boolean, or datetime).
        
    Returns:
        dict: API response from ManyChat.
    """
    return await manychat_page.create_bot_field(name, field_type, description, value)

@mcp.tool()
async def update_bot_field_value(
    field_id: int,
    field_value: Any
) -> Dict[str, Any]:
    """
    Update the value of an existing bot field in ManyChat.
    
    Parameters:
        field_id (int): The ID of the bot field to update.
        field_value (Any): The value to set for the field.
            - For text: a string (e.g., "some text")
            - For number: integer or float (e.g., 123, 1.23)
            - For boolean: true or false
            - For date: string in the format "YYYY-MM-DD"
            - For date and time: string in the format "YYYY-MM-DDTHH:MM:SS+timezone"
    
    Returns:
        dict: API response from ManyChat.
    """
    return await manychat_page.update_bot_field_value(field_id, field_value)

@mcp.tool()
async def update_bot_field_by_name(
    field_name: str,
    field_value: Any
) -> Dict[str, Any]:
    """
    Update the value of an existing bot field by its name in ManyChat.
    
    Parameters:
        field_name (str): The name of the bot field to update.
        field_value (Any): The value to set for the field.
            - For text: a string (e.g., "some text")
            - For number: integer or float (e.g., 123, 1.23)
            - For boolean: true or false
            - For date: string in the format "YYYY-MM-DD"
            - For date and time: string in the format "YYYY-MM-DDTHH:MM:SS+timezone"
    
    Returns:
        dict: API response from ManyChat.
    """
    return await manychat_page.update_bot_field_by_name(field_name, field_value)

@mcp.tool()
async def update_multiple_bot_fields(
    fields: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Update multiple bot fields in a single request.
    
    Parameters:
        fields (List[Dict]): List of dictionaries, where each dictionary contains
                        the 'field_id' or 'field_name' and 'field_value'.
    
    Returns:
        dict: API response from ManyChat.
    """
    return await manychat_page.update_multiple_bot_fields(fields)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()