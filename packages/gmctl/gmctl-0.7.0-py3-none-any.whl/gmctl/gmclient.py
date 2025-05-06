# -----------------------------------------------------------------------------
# Copyright (c) 2025 SKAI Software Corporation. All rights reserved.
#
# This software and associated documentation files (the "Software") are the
# exclusive property of SKAI Software Corporation. Unauthorized copying,
# modification, distribution, resale, or use of this software or its components,
# in whole or in part, is strictly prohibited.
#
# The Software is licensed, not sold. All rights, title, and interest in and to
# the Software, including all associated intellectual property rights, remain
# with SKAI Software Corporation.
# -----------------------------------------------------------------------------

import requests
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)

class GitmoxiClient:
    """
    A client for the Gitmoxi server.

    Attributes:
        endpoint_url: The Gitmoxi FastAPI endpoint URL.
        session_token: The session token for the client.
        api_version: The API version for the client.
    """

    def __init__(self, endpoint_url: str, session_token: str = "", api_version: str = "/api/v1"):
        self.endpoint_url = endpoint_url
        self.session_token = session_token
        self.api_version = api_version

    def post(self, resource_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Makes a POST request to the specified resource path with the given data.

        Args:
            resource_path: The resource path to append to the endpoint URL.
            data: The dictionary to send in the body of the POST request.

        Returns:
            A dictionary with the response data.
        """
        url = f"{self.endpoint_url}{self.api_version}{resource_path}"
        # headers = {"Authorization": f"Bearer {self.session_token}"}
        try:
            response = requests.post(url, json=data) #todo, headers=headers)
            logger.info(f"POST request to {url} with data {data} returned {response}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request to {url} failed: {e} for data {data}")
            return {}
    
    def get(self, resource_path: str) -> Dict[str, Any]:
        """
        Makes a GET request to the specified resource path.

        Args:
            resource_path: The resource path to append to the endpoint URL.

        Returns:
            A dictionary with the response data.
        """
        url = f"{self.endpoint_url}{self.api_version}{resource_path}"
        # headers = {"Authorization": f"Bearer {self.session_token}"}
        try:
            response = requests.get(url) #todo, headers=headers)
            logger.info(f"GET request to {url} returned {response}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request to {url} failed: {e}")
            return {}

    def delete(self, resource_path: str) -> Dict[str, Any]:
        """
        Makes a DELETE request to the specified resource path.

        Args:
            resource_path: The resource path to append to the endpoint URL.

        Returns:
            A dictionary with the response data.
        """
        url = f"{self.endpoint_url}{self.api_version}{resource_path}"
        # headers = {"Authorization": f"Bearer {self.session_token}"}
        try:
            response = requests.delete(url) #todo, headers=headers)
            logger.info(f"DELETE request to {url} returned {response}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"DELETE request to {url} failed: {e}")
            return {}