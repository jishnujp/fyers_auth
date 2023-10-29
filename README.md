# Fyers API Token Generator

This Python script automatically generates Fyers API tokens (For Fyers API v3) and stores them in a Redis cache until midnight. 

## Dependencies

- Python 3.6 or higher
- Redis
- Python packages: `redis`, `totp`, `requests`

## Installation

1. Install Redis on your machine. You can find the installation instructions for different operating systems on the [official Redis website](https://redis.io/download). 
    `sudo apt install redis-server` on Ubuntu

2. Install the necessary Python packages using pip:

```bash
pip install redis pyotp requests
```
3. Install the package using pip:

```bash
pip install git+https://github.com/jishnujp/fyers_auth.git
```

## Usage

```python
from fyers_auth import FyAuth
import redis

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
credentials = {
    "app_id": "<your_app_id>",               # App ID from myapi dashboard is in the form appId-appType.
    # "app_type": "100",
    # "app_id_type": "2",
    "redirect_uri": "<your_redirect_uri>",  # The provided redirct url while creating the app (None if you don't have one)
    "fyers_id": "<your_fyers_id>",          # Your fyers ID
    "totp_key": "<your_totp_key>",          # TOTP key is generated when we enable 2Factor TOTP from myaccount portal
    "pin": "<your_pin>",                    # User pin for fyers account
    "app_id_hash": "<your_app_id_hash>"     # SHA-256 hash of appId-appType:appSecret
}
auth = FyAuth(redis_client=redis_client, logging_on = True, **credentials)
creds = auth.get_creds()
print(creds.app_id)
print(creds.client_id)
print(creds.token)
```
The script stores the tokens in a Redis cache until midnight. The next day, it automatically generates new tokens and stores them in the cache. If you want to refersh the token before midnight, you can use  `creds = auth.refresh_token()`.
You can mention a log file path in the `log_file` parameter of `FyAuth` class. If you don't mention it, the logs will be printed on the console. If you dont want the logs to be neither printed nor saved, set `logging_on` to `False`.

Now you can use the `creds` object to make API calls via fyers_apiv3 package. For example, to get the profile details, you can use the following code:

```python
from fyers_apiv3 import fyersModel
fyers = fyersModel.FyersModel(client_id=creds.client_id, is_async=False, token=creds.token, log_path="")
response = fyers.get_profile()
print(response)
```