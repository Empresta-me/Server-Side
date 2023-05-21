import base58 # for human friendly encoding
import os # TODO explain

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

    def __init__():
        #NOTE: caso precise passar dados durante a inicialização do objeto, como o link para o IDP idk
        pass

    def authenticate(self, data : str) -> str:
        """Takes a password and, if valid, returns a token"""
        #NOTE: a implementação do IDP fica aqui
        pass
