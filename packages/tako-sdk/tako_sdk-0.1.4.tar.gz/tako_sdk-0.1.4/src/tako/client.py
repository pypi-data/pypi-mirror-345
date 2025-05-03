from typing import List, Optional
import requests

from tako.types.common.errors import BaseAPIError
from tako.types.common.exceptions import raise_exception_from_error
from tako.types.knowledge_search.types import KnowledgeSearchResults, KnowledgeSearchSourceIndex

DEFAULT_SERVER_URL = "https://trytako.com/"
DEFAULT_API_VERSION = "v1"

class TakoClient:
    def __init__(self, api_key: str, server_url: Optional[str] = None, api_version: Optional[str] = None):
        assert api_key is not None, "API key is required"
        self.api_key = api_key
        self.server_url = server_url or DEFAULT_SERVER_URL
        self.api_version = api_version or DEFAULT_API_VERSION

    def knowledge_search(self, text: str, source_indexes: Optional[List[KnowledgeSearchSourceIndex]] = None) -> KnowledgeSearchResults:
        """
        Search for knowledge cards based on a text query.

        Args:
            text: The text to search for.
            source_indexes: The source indexes to search for.

        Returns:
            A list of knowledge search results.

        Raises:
            APIException: If the API returns an error.
        """
        url = f"{self.server_url}/api/{self.api_version}/knowledge_search"
        payload = {
            "inputs": {
                "text": text,
            },
        }
        if source_indexes:
            payload["source_indexes"] = source_indexes

        response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {self.api_key}"})
        if response.status_code != 200:
            raise_exception_from_error(BaseAPIError.model_validate(response.json()))
        return KnowledgeSearchResults.model_validate(response.json())
    
    def get_image(self, card_id: str) -> bytes:
        url = f"{self.server_url}/api/{self.api_version}/image/{card_id}"
        response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        return response.content
    
    
    