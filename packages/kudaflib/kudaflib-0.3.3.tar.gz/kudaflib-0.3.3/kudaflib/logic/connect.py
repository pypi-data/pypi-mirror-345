import httpx
import json
from rich.console import Console
from typing import Dict, Any, Tuple, List, Optional
from copy import deepcopy

from kudaflib.config.settings import settings


console = Console()


class KudafMetadataConnect:
    def __init__(
        self,
    ) -> None:
        self.basic_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "kudaflib-CLI",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate, br",
        }

    def get(
        self,
        target_environment: str,
        url_path: str,
        api_key_required: bool = False,
        api_key: str = "",
    ) -> Tuple[bool, List | Dict]:
        """
        Download JSON response from URL
        Returns a tuple of an error boolean and a dict
        """
        errors = []
        
        headers = deepcopy(self.basic_headers)
        if api_key_required:
            headers.update({"Authorization": f"API-Key {api_key}"})

        base_url = settings.KUDAF_METADATA_BACKEND_BASE_URLS[target_environment]
        url = f"{base_url}{url_path}"

        try:
            response = httpx.get(url=url, headers=headers)
            response.raise_for_status()
        except httpx.TimeoutException as e:
            msg = f"A Timeout error occurred querying URL at: {e.request.url!r}"
            console.print(f"[red]:poop: {msg}[/red]")
            errors.append(msg)
        except httpx.NetworkError as e:
            msg = f"A Network error occurred querying URL at: {e.request.url!r}"
            console.print(f"[red]:poop: {msg}[/red]")
            errors.append(msg)
        except httpx.HTTPStatusError as e:
            if response.status_code == 404:
                msg = f"Resource not found at URL: {e.request.url!r}"
                console.print(f"[red]:poop: {msg}[/red]")
                return False, {}
            elif response.status_code != 200:
                msg = f"HTTP error: {e.response.status_code} occurred at URL: {e.request.url!r} -> Error: {response.json().get('detail', 'Unknown')})"   
                console.print(f"[red]:poop: {msg}[/red]")
                errors.append(msg)
        except Exception as e:
            msg = f"An exception occurred querying URL: {e.args}"
            console.print(f"[red]:poop: {msg}[/red]")
            errors.append(msg)
        else:
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                msg = f"Error decoding JSON response: {e} - Text: {response.text}"
                console.print(f"[red]:poop: {msg}[/red]")
                errors.append(msg)
            else:
                if response.status_code != 200:
                    msg = f"Error code: {response.status_code}, Details: {response.json().get('detail', 'N/A')}"
                    console.print(f"[red]:poop: {msg}[/red]")
                    errors.append(msg)

        if errors:
            return True, {"error": errors}  
        else:
            return False, response_json

    def post(
        self,
        target_environment: str,
        resource: str,
        input_json: Dict[str, Any],
        api_key_required: bool = True,
        api_key: str = "",
    ) -> Dict[str, Any]:
        """
        Send a POST request to the URL with the input JSON
        """
        errors = []

        headers = deepcopy(self.basic_headers)
        if api_key_required:
            headers.update({"Authorization": f"API-Key {api_key}"})

        base_url = settings.KUDAF_METADATA_BACKEND_BASE_URLS.get(target_environment, "")
        url_path = settings.KUDAF_METADATA_BACKEND_URLS.get(resource, "")

        try:
            response = httpx.post(
                    url=f"{base_url}{url_path}",
                    headers=headers,
                    json=input_json
                )
            response.raise_for_status()
        except httpx.TimeoutException as e:
            msg = f"A Timeout error occurred querying URL at: {e.request.url!r}"
            console.print(f"[red]:poop: {msg}[/red]")
            errors.append(msg)
        except httpx.NetworkError as e:
            msg = f"A Network error occurred querying URL at: {e.request.url!r}"
            console.print(f"[red]:poop: {msg}[/red]")
            errors.append(msg)
        except httpx.HTTPStatusError as e:
            msg = f"HTTP error: {e.response.status_code} occurred at URL: {e.request.url!r} -> Error: {response.json().get('detail', 'Unknown')})"   
            console.print(f"[red]:poop: {msg}[/red]")
            errors.append(msg)
        except Exception as e:
            msg = f"An exception occurred querying URL: {e.args}"
            console.print(f"[red]:poop: {msg}[/red]")
            errors.append(msg)
        else:
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:
                msg = f"Error decoding JSON response: ut_api_response.get{e} - Text: {response.text}"
                console.print(f"[red]:poop: {msg}[/red]")
                errors.append(msg)
            else:
                if response.status_code != 200:
                    msg = f"Error code: {response.status_code}, Details: {response.json().get('detail', 'N/A')}"
                    console.print(f"[red]:poop: {msg}[/red]")
                    errors.append(msg)

        if errors:
            return True, {"error": errors}  
        else:
            return False, response_json


kudaf_metadata_connect = KudafMetadataConnect()
