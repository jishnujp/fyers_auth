from datetime import datetime

class AuthCache:
        
    def __init__(self, redis_client, client_id, logger):
        
        self._redis_client = redis_client
        self._logger = logger
        self._verify_redis_client()
        self.__key = f"fyers:token:{client_id}"
        self.__token = None
        
    def _verify_redis_client(self):
        
        if self._redis_client is None:
            self._logger.log_error("Redis client not found for caching token.")
            raise Exception("Redis client not found for caching token.")
        elif not self._redis_client.ping():
            self._logger.log_error("Redis client not connected for caching token.")
            raise Exception("Redis client not connected for caching token.")
        
        
    def _expiry(self):
            
            now = datetime.now()
            midnight = now.replace(hour=23, minute=59, second=59, microsecond=0)
            return (midnight - now).seconds
        
    def save_token(self, token):
        
        expiry = self._expiry()
        self._redis_client.set(self.__key, token, ex=expiry)
        
    def clear_token(self):
        
        self._redis_client.delete(self.__key)
        
    def get_token(self):
        
        if self.__token is None:
            self.__token = self._redis_client.get(self.__key)
            self.__token = self.__token if self.__token is None else self.__token.decode("utf-8")
            if self.__token is None:
                self._logger.log_warning("Token not found in cache")
            else:
                self._logger.log_info("Token found in cache")
        return self.__token
        

        
    
        
