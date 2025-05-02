import requests
from threading import Lock

class APIConsumer:
    _instance = None
    _lock = Lock()

    def __new__(cls, user_id, token):
        if cls._instance is None:
            print(f"new instance userid: {user_id}, token: {token}")
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(APIConsumer, cls).__new__(cls)
                    cls._instance.user_id = user_id
                    cls._instance.base_url = "https://www.gailbot.ai"
                    cls._instance.headers = {'Authorization': f'Token {token}'}
        return cls._instance
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError("Must initialize first")
        return cls._instance

    @classmethod
    def reset_instance(cls):
        with cls._lock:
            cls._instance = None

    def fetch_plugin_info(self, plugin_id, version=None):
        user_id = self.user_id
        if user_id is None:
            raise ValueError("User ID must be set via setUserId or passed explicitly.")

        endpoint = f"{self.base_url}/api/plugin/retrieve"
        payload = {"plugin_id": plugin_id, "user_id": user_id}
        if version:
            payload["version"] = version
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            if response_json['success']:
                return response_json['plugin']
        except requests.RequestException as e:
            print(f"Error fetching plugin info: {e}")
            return None

    def fetch_suite_info(self, suite_id, version=None):
        user_id = self.user_id
        if user_id is None:
            raise ValueError("User ID must be set via setUserId or passed explicitly.")

        endpoint = f"{self.base_url}/api/suites/retrieve"
        payload = {"suite_id": suite_id, "user_id": user_id}
        if version:
            payload["version"] = version
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            if response_json['success']:
                return response_json['suite']
        except requests.RequestException as e:
            print(f"Error fetching suite info: {e}")
            return None
