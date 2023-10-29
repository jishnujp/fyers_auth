import json
import requests
import random
import pyotp
from urllib import parse
from .cache import AuthCache
from .logger import AuthLogger

class Creds:
    def __init__(self, app_id, client_id, token):
        self.__app_id = app_id
        self.__client_id = client_id
        self.__token = token
        
    def __repr__(self):
        return f"app_id: {self.__app_id} \nclient_id: {self.__client_id} \ntoken: {self.__token}"
    
    @property
    def app_id(self):
        return self.__app_id
    
    @property
    def client_id(self):
        return self.__client_id
    
    @property
    def token(self):
        return self.__token
class Auth:
    
    AUTH_CODE_URL = "https://api-t1.fyers.in/api/v3/token"
    ACCESS_TOKEN_URL = "https://api-t1.fyers.in/api/v3/validate-authcode"
    LOGIN_OTP_URL = "https://api-t2.fyers.in/vagator/v2/send_login_otp"
    TOTP_VALIDATION_URL = "https://api-t2.fyers.in/vagator/v2/verify_otp"
    PIN_VALIDATION_URL = "https://api-t2.fyers.in/vagator/v2/verify_pin"
    DEFAULT_REDIRECT_URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"
     
    def __init__(self,fyers_id,  app_id, app_id_hash, totp_key, pin, redis_client,
                     app_type="100", app_id_type="2", redirect_uri=None, **kwargs):
                
        self.__fyers_id = fyers_id
        self.__app_id = app_id
        self.__app_id_type = app_id_type
        self.__app_id_hash = app_id_hash
        self.__totp_key = totp_key
        self.__pin = pin
        self.__app_type = app_type
        self.__redirect_uri = redirect_uri or self.DEFAULT_REDIRECT_URI
        self.__client_id = f"{self.__app_id}-{app_type}"
        self._logger = AuthLogger(**kwargs)
        self.__cache = AuthCache(redis_client, self.__client_id, self._logger) 
        self.__token = self.__cache.get_token()
        
        try:
            if self.__token is None:
                self.__token = self.__authenticate()
                self.__cache.save_token(self.__token)
        except Exception as e:
            self._logger.log_error("Authentication failed", e)
            raise Exception(e)
        
    def __generate_otp(self):
        
        try:
            otp = pyotp.TOTP(self.__totp_key).now()
            self._logger.log_info("TOTP generated successfully")
            return otp
        except Exception as e:
            raise Exception(f"TOTP generation failed with {e}")

    def __totp_validation(self):

        ##sending login otp
        payload = {"fy_id": self.__fyers_id, "app_id": self.__app_id_type}
        result0 = requests.post(url=self.LOGIN_OTP_URL, json=payload)
        if result0.status_code != 200:
            raise Exception(f"{self.LOGIN_OTP_URL} failed with {result0.status_code}, {result0.text}")
        else:
            self._logger.log_info("Sending login otp successfull")
        request_key = json.loads(result0.text)["request_key"]
        
        ##verifying totp
        payload = {"request_key": request_key, "otp": self.__generate_otp()}
        result1 = requests.post(url=self.TOTP_VALIDATION_URL, json=payload)
        if result1.status_code != 200:
            raise Exception(f"{self.TOTP_VALIDATION_URL} failed with {result1.status_code}, {result1.text}")
        else:
            self._logger.log_info("Verifying totp successfull")
        request_key = json.loads(result1.text)["request_key"]
        return request_key

    def __pin_validation(self, request_key):

        ##verifying pin
        payload = {"request_key": request_key, "identity_type": "pin", "identifier": self.__pin}
        result = requests.post(url=self.PIN_VALIDATION_URL, json=payload)
        if result.status_code != 200:
            raise Exception(f"{self.PIN_VALIDATION_URL} failed with {result.status_code}, {result.text}")
        else:
            self._logger.log_info("Verifying pin successfull")
        request_key = json.loads(result.text)["data"]["access_token"]
        return request_key

    def __get_auth_code(self, access_token):

        ##getting auth code from redirect url
        self.__state = str(random.randint(1000000000, 9999999999))
        payload = {
            "fyers_id": self.__fyers_id,
            "app_id": self.__app_id,
            "redirect_uri": self.__redirect_uri,
            "appType": self.__app_type,
            "code_challenge": "",
            "state": self.__state,
            "scope": "",
            "nonce": "",
            "response_type": "code",
            "create_cookie": True,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        result = requests.post(url=self.AUTH_CODE_URL, json=payload, headers=headers)
        if result.status_code != 308:
            raise Exception(f"{self.AUTH_CODE_URL} failed with {result.status_code}, {result.text}")
        else:
            self._logger.log_info("Getting auth code url successfull")
        url = json.loads(result.text)["Url"]
        return self.__extract_auth_code_from_url(url)
    
    def __extract_auth_code_from_url(self, url):
        
        auth_code = parse.parse_qs(parse.urlparse(url).query)["auth_code"][0]
        state = parse.parse_qs(parse.urlparse(url).query)["state"][0]
        if state != self.__state:
            raise Exception("POTENTIAL SECURITY RISK: STATE MISMATCH!!")
        return auth_code   
        

    def __get_access_token(self, auth_code):

        # function to get access token
        payload = {
            "grant_type": "authorization_code",
            "appIdHash": self.__app_id_hash,
            "code": auth_code,
        }
        result = requests.post(url=self.ACCESS_TOKEN_URL, json=payload)
        if result.status_code != 200:
            raise Exception(f"{self.ACCESS_TOKEN_URL} failed with {result.status_code}, {result.text}")
        else:
            self._logger.log_info("Getting access token successfull")
        access_token = json.loads(result.text)["access_token"]
        return access_token

    def __authenticate(self):

        request_key = self.__totp_validation()
        access_token = self.__pin_validation(request_key)
        auth_code = self.__get_auth_code(access_token)
        return self.__get_access_token(auth_code)
        

    def get_creds(self):
        
        return Creds(self.__app_id, self.__client_id, self.__token)
    
    def refresh_token(self):
        
        self.__cache.clear_token()
        self.__token = self.__authenticate()
        return Creds(self.__app_id, self.__client_id, self.__token)
