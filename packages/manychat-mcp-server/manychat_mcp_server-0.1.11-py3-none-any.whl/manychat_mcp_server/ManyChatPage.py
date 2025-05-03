import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import httpx

load_dotenv()


class ManyChatPage:
    BASE_URL = "https://api.manychat.com/"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("MANYCHAT_API_KEY")
        if not self.api_key:
            raise ValueError("MANYCHAT_API_KEY is missing in environment variables.")
        self.client = httpx.AsyncClient()
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    async def get_page_info(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/fb/page/getInfo"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return {
                    "status": 200,
                    "data": response.json()
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def create_tag(self, name: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/fb/page/createTag"
        payload = {"name": name}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, headers=self.headers, json=payload, timeout=30.0
                )
                response.raise_for_status()
                return {
                    "status": 200,
                    "data": response.json()
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
    
    async def get_tags(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/fb/page/getTags"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url, headers=self.headers, timeout=30.0
                )
                response.raise_for_status()
                return {
                    "status": 200,
                    "data": response.json()
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
    
    async def remove_tag(self, tag_id: int = None, tag_name: str = None) -> dict[str, Any]:
        if tag_id:
            url = f"{self.BASE_URL}/fb/page/deleteTag"
            data = {"tag_id": tag_id}
        elif tag_name:
            url = f"{self.BASE_URL}/fb/page/deleteTagByName"
            data = {"tag_name": tag_name}
        else:
            return {
                "status": 400,
                "error": "Either 'tag_id' or 'tag_name' must be provided."
            }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, headers=self.headers, json=data, timeout=30.0
                )
                response.raise_for_status()
                return {
                    "status": 200,
                    "message": f"Tag removed successfully using {'tag_id' if tag_id else 'tag_name'}.",
                    "data": response.json()
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }    

    async def create_custom_field(self, caption: str, field_type: str, description: str = "") -> dict:
        """
        Create a custom field in ManyChat.

        Parameters:
            caption (str): The display name of the custom field.
            field_type (str): Type of field. Valid types: text, number, date, datetime, boolean, etc.
            description (str): Optional description for the custom field.

        Returns:
            dict: API response from ManyChat.
        """
        url = f"{self.BASE_URL}/fb/customField/createField"
        payload = {
            "caption": caption,
            "type": field_type,
            "description": description
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return {
                    "status": 200,
                    "message": "Custom field created successfully.",
                    "data": response.json()
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def get_growth_tools(self) -> dict:
        """
        Fetch all Growth Tools associated with the page.

        Returns:
            dict: A response containing a list of growth tools or error info.
        """
        url = f"{self.BASE_URL}/fb/page/getGrowthTools"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return {
                    "status": 200,
                    "data": response.json().get("data", [])
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def get_flows(self) -> dict:
        """
        Retrieve all flows and folders from the ManyChat page.

        Returns:
            dict: Contains list of flows and folders or error details.
        """
        url = f"{self.BASE_URL}/fb/page/getFlows"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json().get("data", {})
                return {
                    "status": 200,
                    "flows": data.get("flows", []),
                    "folders": data.get("folders", [])
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def get_custom_fields(self) -> dict:
        """
        Fetch all custom fields from the ManyChat page.

        Returns:
            dict: A response containing a list of custom fields or error info.
        """
        url = f"{self.BASE_URL}/fb/page/getCustomFields"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return {
                    "status": 200,
                    "data": response.json().get("data", [])
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def get_otn_topics(self) -> dict:
        """
        Fetch all OTN topics from the ManyChat page.

        Returns:
            dict: A response containing a list of OTN topics or error info.
        """
        url = f"{self.BASE_URL}/fb/page/getOtnTopics"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return {
                    "status": 200,
                    "data": response.json().get("data", [])
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def get_bot_fields(self) -> dict:
        """
        Fetch all bot fields from the ManyChat page.

        Returns:
            dict: A response containing a list of bot fields or error info.
        """
        url = f"{self.BASE_URL}/fb/page/getBotFields"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return {
                    "status": 200,
                    "data": response.json().get("data", [])
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def create_bot_field(self, name: str, field_type: str, description: str = "", value: str = "") -> dict:
        """
        Create a bot field in ManyChat.

        Parameters:
            name (str): The name of the bot field.
            field_type (str): The type of the field (text, number, boolean, etc.).
            description (str): A description of the field.
            value (str): The value for the field (can be string, number, boolean, or datetime).

        Returns:
            dict: API response from ManyChat, containing the created field details.
        """
        url = f"{self.BASE_URL}/fb/page/createBotField"
        payload = {
            "name": name,
            "type": field_type,
            "description": description,
            "value": value
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return {
                    "status": 200,
                    "message": "Bot field created successfully.",
                    "data": response.json().get("data", {})
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def update_bot_field_value(self, field_id: int, field_value: Any) -> dict:
        """
        Update the value of an existing bot field in ManyChat.

        Parameters:
            field_id (int): The ID of the bot field to update.
            field_value (str | int | bool): The value to set for the field.
                - For text: a string (e.g., "some text")
                - For number: integer or float (e.g., 123, 1.23)
                - For boolean: true or false
                - For date: string in the format "YYYY-MM-DD"
                - For date and time: string in the format "YYYY-MM-DDTHH:MM:SS+timezone"
        
        Returns:
            dict: API response from ManyChat.
        """
        url = f"{self.BASE_URL}/fb/page/updateBotField"
        payload = {
            "field_id": field_id,
            "field_value": field_value
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return {
                    "status": 200,
                    "message": "Bot field value updated successfully.",
                    "data": response.json().get("data", {})
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def update_bot_field_by_name(self, field_name: str, field_value: Any) -> dict:
        """
        Update the value of an existing bot field by its name in ManyChat.

        Parameters:
            field_name (str): The name of the bot field to update.
            field_value (str | int | bool): The value to set for the field.
                - For text: a string (e.g., "some text")
                - For number: integer or float (e.g., 123, 1.23)
                - For boolean: true or false
                - For date: string in the format "YYYY-MM-DD"
                - For date and time: string in the format "YYYY-MM-DDTHH:MM:SS+timezone"
        
        Returns:
            dict: API response from ManyChat.
        """
        url = f"{self.BASE_URL}/fb/page/updateBotFieldByName"
        payload = {
            "field_name": field_name,
            "field_value": field_value
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return {
                    "status": 200,
                    "message": "Bot field value updated successfully.",
                    "data": response.json().get("data", {})
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }
                
    async def update_multiple_bot_fields(self, fields: list) -> dict:
        """
        Update multiple bot fields in a single request.

        Parameters:
            fields (list): List of dictionaries, where each dictionary contains
                            the 'field_id' or 'field_name' and 'field_value'.
        
        Returns:
            dict: API response from ManyChat.
        """
        url = f"{self.BASE_URL}/fb/page/updateBotFields"
        payload = {
            "fields": fields
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return {
                    "status": 200,
                    "message": "Bot fields updated successfully.",
                    "data": response.json().get("data", {})
                }
            except httpx.HTTPStatusError as e:
                return {
                    "status": e.response.status_code,
                    "error": e.response.json()
                }
            except Exception as e:
                return {
                    "status": 500,
                    "error": str(e)
                }