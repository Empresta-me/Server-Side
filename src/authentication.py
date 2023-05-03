import base58 # for human friendly encoding
import os # TODO explain

class AuthenticationBase:

    def authenticate(self, data : str) -> str:
        pass

class DirectApproximation(AuthenticationBase):
    """Strategy implementation for direct approximation (password)"""

    def __init__(self, password : str):
        self.password = password

    def authenticate(self, password : str) -> str:
        """Takes a password and, if valid, returns a token"""

        # if the password matches
        if self.password == password:
            
            # generates random unique association token
            token = None
            while token == None:
                random_bytes = bytearray(os.urandom(self.ASSOCIATION_TOKEN_LENGTH))
                token = base58.b58encode(random_bytes).decode('utf-8')
            
            # returns token as base58
            return token

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
