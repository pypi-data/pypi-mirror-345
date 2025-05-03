import hashlib
import hmac
import requests
from datetime import datetime
from urllib.parse import urlencode

class ERepublikAPIClient:
    def __init__(self, public_key: str, private_key: str):
        self.public_key = public_key
        self.private_key = private_key

    def api_call(self, resource: str, action: str, query: dict = None):
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
        message = f"{resource.lower()}:{action}"
        if query:
            message += f":{urlencode(query)}"
        message += f":{date}"

        digest = hmac.new(
            self.private_key.encode(), 
            message.encode(), 
            hashlib.sha256
        ).hexdigest()

        headers = {
            "Date": date,
            "Auth": f"{self.public_key}/{digest}"
        }

        url = f"https://api.erepublik.com/{resource}/{action}"
        if query:
            url += f"?{urlencode(query)}"

        response = requests.get(url, headers=headers)
        return response.text
