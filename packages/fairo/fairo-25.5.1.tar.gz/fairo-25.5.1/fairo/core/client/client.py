# base_client.py
import requests
from requests.auth import HTTPBasicAuth

class BaseClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.headers.update({
            "Content-Type": "application/json",
        })

    def get(self, endpoint: str, params=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data=None, json=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, data=data, json=json)
        response.raise_for_status()
        return response.json()
