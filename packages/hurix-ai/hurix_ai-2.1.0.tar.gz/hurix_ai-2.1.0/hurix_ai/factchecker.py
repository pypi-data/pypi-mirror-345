import requests
import json
from typing import Optional, List

class FactChecker:
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url

    def fact_check(self, text: str, excluded_domains: Optional[List[str]] = None):
        headers = {"Authorization": self.api_key}
        payload = {"model": self.model_name, "text": text, "excluded_domains": excluded_domains}

        response = requests.post(f"{self.base_url}/factverification", json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
        
    def fact_check_streaming(self, text: str, excluded_domains: Optional[List[str]] = None):
        headers = {"Authorization": self.api_key}
        payload = {"model": self.model_name, "text": text, "excluded_domains": excluded_domains}

        with requests.post(f"{self.base_url}/factverification-streaming", json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                yield {"error": response.text, "status_code": response.status_code}
            else:
                for line in response.iter_lines(decode_unicode=True):
                    if line.strip():
                        yield json.loads(line.strip())
    #----------------------                    
    # File Upload Methods
    #----------------------
    def fact_check_file(self, file_path: str, excluded_domains: Optional[List[str]] = None):
        headers = {"Authorization": self.api_key}
        excluded_str = ",".join(excluded_domains) if excluded_domains else ""
        files = {
            "file": (file_path, open(file_path, "rb")),
            "model": (None, self.model_name),  # Send model as form-data field
            "excluded_domains": (None, excluded_str)
        }

        response = requests.post(f"{self.base_url}/factverification-file", files=files, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
        
    def fact_check_file_streaming(self, file_path: str, excluded_domains: Optional[List[str]] = None):
        headers = {"Authorization": self.api_key}
        excluded_str = ",".join(excluded_domains) if excluded_domains else ""
        files = {
            "file": (file_path, open(file_path, "rb")),
            "model": (None, self.model_name),  # Send model as form-data field
            "excluded_domains": (None, excluded_str)
        }

        with requests.post(f"{self.base_url}/factverification-file-streaming", files=files, headers=headers, stream=True) as response:
            if response.status_code != 200:
                yield {"error": response.text, "status_code": response.status_code}
            else:
                for line in response.iter_lines(decode_unicode=True):
                    if line.strip():
                        yield json.loads(line.strip())

    #----------------------                    
    # Batch Method
    #----------------------
    def fact_check_batch(self, text: str, excluded_domains: Optional[List[str]] = None):
        headers = {"Authorization": self.api_key}
        payload = {"model": self.model_name, "text": text, "excluded_domains": excluded_domains}

        response = requests.post(f"{self.base_url}/factverification-batch", json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}

    def fact_check_file_batch(self, file_path: str, excluded_domains: Optional[List[str]] = None):
        headers = {"Authorization": self.api_key}
        excluded_str = ",".join(excluded_domains) if excluded_domains else ""
        files = {
            "file": (file_path, open(file_path, "rb")),
            "model": (None, self.model_name),  # Send model as form-data field
            "excluded_domains": (None, excluded_str)
        }

        response = requests.post(f"{self.base_url}/factverification-file-batch", files=files, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}