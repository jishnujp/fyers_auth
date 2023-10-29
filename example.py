from fyers_auth import FyAuth
import redis
import json

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
with open(".creds.json") as f:
    credentials = json.load(f)
auth = FyAuth(redis_client=redis_client, logging_on = True, **credentials)
creds = auth.get_creds()
print(creds.app_id)
print(creds.client_id)
print(creds.token)

