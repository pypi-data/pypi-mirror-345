# erepublik-api

Python wrapper for the eRepublik API with HMAC authentication.
https://api.erepublik.com/doc/

## Install

```bash
pip install erepublik-api
```

## Usage
```py
from erepublik_api import ERepublikAPIClient

client = ERepublikAPIClient(public_key="your_key", private_key="your_secret")
response = client.api_call("citizen", "profile", {"citizenid": "2"})
print(response)
```


