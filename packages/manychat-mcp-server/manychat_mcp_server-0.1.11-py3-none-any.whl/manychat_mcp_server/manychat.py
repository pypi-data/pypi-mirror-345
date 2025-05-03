import os
import json
from typing import Any, Optional
from dotenv import load_dotenv
import httpx

load_dotenv()


class ManyChatClient:
    BASE_URL = "https://api.manychat.com/"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("MANYCHAT_API_KEY")
        if not self.api_key:
            raise ValueError("MANYCHAT_API_KEY is missing in environment variables.")

    async def _post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=data, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"[ERROR] Failed request to {url}: {e}")
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    print(f"[DEBUG] Response content: {e.response.text}")
                return {"error": str(e)}

    async def send_text_message(self, subscriber_id: int, message: str, message_tag: str = "ACCOUNT_UPDATE") -> str:
        data = {
            "subscriber_id": subscriber_id,
            "data": {
                "version": "v2",
                "content": {
                    "type": "instagram",
                    "messages": [{"type": "text", "text": message}],
                    "actions": [],
                    "quick_replies": []
                }
            },
            "message_tag": message_tag
        }
        response = await self._post("fb/sending/sendContent", data)
        return self._handle_response(response, subscriber_id)

    async def send_flow(self, subscriber_id: str, flow_ns: str) -> dict[str, Any]:
        data = {
            "subscriber_id": subscriber_id,
            "flow_ns": flow_ns
        }
        return await self._post("/fb/sending/sendFlow", data)
    
    async def get_flows(self) -> dict[str, Any]:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _handle_response(self, response: dict[str, Any], subscriber_id: int) -> dict[str, Any]:
        if response is None or "error" in response:
            return {
                "status": 500,
                "message": response.get("error", "Unknown error") if response else "Failed to send message",
                "subscriber_id": subscriber_id,
                "response": response
            }
        return {
            "status": 200,
            "message": f"Message sent successfully to subscriber ID {subscriber_id}.",
            "subscriber_id": subscriber_id,
            "response": response
        }

