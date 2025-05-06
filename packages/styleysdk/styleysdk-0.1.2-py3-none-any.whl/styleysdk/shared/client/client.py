import requests

class Client:

    api_key: str = ''
    mm_url: str = ''


    def __init__(self, api_key: str,mm_url: str):
        self._api_key = api_key
        self._mm_url = mm_url


    def get(self, path: str):
        try:
            response = requests.get(self._mm_url + path, headers={
                'Content-Type': 'application/json',
                'x-mediamagic-key': self._api_key,
                'Accept': 'application/json',
            })
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return "A HTTP error occured: %s" % e


    def post(self, path: str, body: dict):
        try:
            response = requests.post(self._mm_url + path, json=body, headers={
                'Content-Type': 'application/json',
                'x-mediamagic-key': self._api_key,
                'Accept': 'application/json',
            })
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return "A HTTP error occured: %s" % e
