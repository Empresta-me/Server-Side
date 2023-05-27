import base58 # for human friendly encoding
import os
from dotenv import load_dotenv
import requests
import base64
import jwt

class AuthenticationBase:

    def generate_token(self) -> str:
        # generates random unique association token
        random_bytes = bytearray(os.urandom(self.ASSOCIATION_TOKEN_LENGTH))
        token = base58.b58encode(random_bytes).decode('utf-8')
        # returns token as base58
        return token

class DirectApproximation(AuthenticationBase):
    """Strategy implementation for direct approximation (password)"""

    def __init__(self, password : str, assoc_token_length):
        self.password = password
        self.ASSOCIATION_TOKEN_LENGTH = assoc_token_length

    def authenticate(self, password : str) -> str:
        """Takes a password and, if valid, returns a token"""

        # if the password matches
        if self.password == password:
            
            return self.generate_token()

        # password does not match. return none
        else: 
            return None

class IDP(AuthenticationBase):
    """Strategy implementation for IDP"""

    def __init__(self, password : str, assoc_token_length):
        #NOTE: caso precise passar dados durante a inicialização do objeto, como o link para o IDP idk
        self.AUTH_CODE = password
        self.ua_oauth_auth_uri = os.environ.get("UA_OAUTH_AUTH_URI")
        self.ua_oauth_redirect_uri = os.environ.get("UA_OAUTH_REDIRECT_URI")
        self.ua_oauth_scope = os.environ.get("UA_OAUTH_SCOPE")
        self.ua_oauth_response_type = os.environ.get("UA_OAUTH_RESPONSE_TYPE")
        self.ua_oauth_client_id = os.environ.get("UA_OAUTH_CLIENT_ID")
        self.ua_oauth_client_secret = os.environ.get("UA_OAUTH_CLIENT_SECRET")
        self.ua_oauth_token_uri = os.environ.get("UA_OAUTH_TOKEN_URI")
        print("DEBUG: Initiating IDP Handshake to get access token")

    # Auxiliary function
    def get_base64(self, some_string, encoding='utf-8'):
        string_bytes = some_string.encode(encoding)
        base64_bytes = base64.b64encode(string_bytes)
        return base64_bytes.decode(encoding)

    def authenticate(self, data : str) -> str:
        """Takes a password and, if valid, returns a token"""
        #NOTE: a implementação do IDP fica aqui

        basic_auth = self.get_base64(f"{self.ua_oauth_client_id}:{self.ua_oauth_client_secret}")

        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "code": self.AUTH_CODE,
            "redirect_uri": self.ua_oauth_redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(url=self.ua_oauth_token_uri, headers=headers, data=payload)

        if response.status_code != 200:
            print(response.status_code)

        json_data = response.json()

        # Retrieve the 'id_token' from the JSON data
        id_token = json_data["id_token"]

        # Decode the JWT token without verification (assuming it's an unsigned JWT)
        decoded_jwt = jwt.decode(id_token, options={"verify_signature": False})

        # Get the 'sub' field from the decoded JWT
        sub = decoded_jwt["sub"]

        print(sub)

        return f'User: {sub}'



