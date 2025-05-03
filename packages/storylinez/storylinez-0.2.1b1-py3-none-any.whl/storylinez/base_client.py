import requests
import time
from typing import Dict, Any

class BaseClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str, default_org_id: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.default_org_id = default_org_id

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json",
        }

    def _make_request(self, method: str, url: str, params: Dict = None, 
                    json_data: Dict = None, data: Any = None, 
                    files: Dict = None, headers: Dict = None,
                    max_retries: int = 3, retry_delay: float = 1.0) -> Dict:
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)
            
        retries = 0
        while True:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    data=data,
                    files=files,
                    headers=request_headers
                )
                
                if response.status_code >= 400:
                    error_message = f"API request failed with status {response.status_code}"
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_message = f"{error_message}: {error_data['error']}"
                    except:
                        if response.text:
                            error_message = f"{error_message}: {response.text}"
                    raise Exception(error_message)
                return response.json()
                
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout, 
                    requests.exceptions.RequestException) as e:
                retries += 1
                if retries > max_retries:
                    raise Exception(f"Maximum retry attempts reached after network errors: {str(e)}")
                
                # Exponential backoff
                wait_time = retry_delay * (2 ** (retries - 1))
                time.sleep(wait_time)
                continue
