"""

    PROJECT: flex_toolbox
    FILENAME: retry.py
    AUTHOR: David NAISSE
    DATE: August 5th, 2024

    DESCRIPTION: session class
"""

from typing import List, Union
import requests
from requests.models import HTTPBasicAuth

from src._encryption import decrypt_pwd
import json


class Session:

    url: str
    session: requests.Session

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        headers: dict = {"Content-Type": "application/vnd.nativ.mio.v1+json"},
    ) -> None:
        self.url = url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(
            username=username, password=decrypt_pwd(password)
        )
        self.session.headers.update(headers)
        self.http_requests_count = 0

    def request(
        self, method: str, url: str, data: Union[dict, None] = None
    ) -> Union[dict, List]:
        """
        Requests a given environment.

        :param method: method to use
        :param url: url to request
        :param data: data to send along the request
        """

        response = self.session.request(
            method=method,
            url=url,
            data=json.dumps(data) if data is not None else None,
        )

        # response is json
        try:
            response = response.json()
            self.http_requests_count += 1
        except Exception as ex:
            # response is list
            if isinstance(response, list):
                pass
            elif response.status_code == 204:
                return {}
            else:
                raise TypeError(f"{ex}: {response}")

        # exception handler
        if isinstance(response, dict) and "errors" in response:
            has_flex_request_id = response.get("flex.request.id")
            error_message = f"\n\nError while sending {method} {url}. \nError message: {str(response['errors'])}\n"
            if has_flex_request_id:
                error_message += f"Flex request ID: {has_flex_request_id}\n"
            raise AttributeError(error_message)

        return response
