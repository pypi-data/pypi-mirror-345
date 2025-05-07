"""
Core Recruitee API client.
"""

import requests
from typing import Union, List, Dict, Any, Optional
from brynq_sdk_brynq import BrynQ


class Recruitee(BrynQ):
    """
    Core client for interacting with the Recruitee API.

    This is the base client that provides low-level access to the Recruitee API.
    For specific API endpoints, use the specialized classes like Candidates, Offers, and Organization.

    Args:
        label: Label or list of labels for credentials
        api_type: Type of API to use (default: "API")
    """
    def __init__(self, label: Union[str, List], api_type: str = "API"):
        super().__init__()
        credentials = self.get_system_credential(system='recruitee', label=label)
        self.base_url = f'https://api.recruitee.com/c/{credentials["company_id"]}/'
        self.headers = {
            "Authorization": f"Bearer {credentials['token']}",
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make a GET request to the Recruitee API.

        Args:
            endpoint: API endpoint to call
            params: Optional parameters to include in the request

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url=url,
                                headers=self.headers,
                                params=params,
                                timeout=self.timeout)
        response.raise_for_status()
        return response

    def post(self, endpoint: str, json: Optional[Dict] = None) -> requests.Response:
        """
        Make a POST request to the Recruitee API.

        Args:
            endpoint: API endpoint to call
            json: Optional JSON data to include in the request

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        return requests.post(url=url,
                             headers=self.headers,
                             json=json,
                             timeout=self.timeout)

    def patch(self, endpoint: str, json: Optional[Dict] = None) -> requests.Response:
        """
        Make a PATCH request to the Recruitee API.

        Args:
            endpoint: API endpoint to call
            json: Optional JSON data to include in the request

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        return requests.patch(url=url,
                              headers=self.headers,
                              json=json,
                              timeout=self.timeout)

    def delete(self, endpoint: str) -> requests.Response:
        """
        Make a DELETE request to the Recruitee API.

        Args:
            endpoint: API endpoint to call

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        return requests.delete(url=url,
                               headers=self.headers,
                               timeout=self.timeout)