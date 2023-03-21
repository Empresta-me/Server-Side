from src.crypto import Crypto # cryptographic functions
import base58 # for human friendly encoding
import os # TODO explain

class Community:

    CHALLENGE_LENGTH = 16
    ASSOCIATION_TOKEN_LENGTH = 16

    def __init__(self):
        # TODO: for now, it generates a new key each time. Implement persistance.
        self.private_key, self.public_key = Crypto.asym_gen()
        self.address = base58.b58encode(Crypto.serialize(self.public_key)).decode('utf-8') # public key encoded as base58 string

        # TODO : fow now, hardcoded data. Implement persistance
        self.title = "DETI Community"
        self.bio = "Univeristy of Aveiro's first EMPRESTA.ME community!"

        # TODO: direct aproximation hardcoded for now
        self.password = "batatinhas123"

        # set of association tokens issued. removed as soon as they are used
        # NOTE: as the existing association tokens are stored in memory, server reboots will clean it. have to keep in mind when doing the frontend that "lost" tokens can exist
        self.association_tokens = set()

    def get_info(self) -> dict:
        """Shares community public information"""
        return {'title' : self.title, 'bio' : self.bio, 'public_key' : self.address }

    def reply_challenge(self, challenge : str) -> dict:
        """Answers to challenge with signature"""
        # sign it and encode it to base58
        signature = base58.b58encode(Crypto.sign(self.private_key, challenge)).decode('utf-8')

        # return to the associate the public key plus the signature plus the session token
        return { 'public_key' : self.address, 'response' : signature }

    def get_association_token(self, password : str) -> bool:
        """Verifies association attemp from member and returns token"""
        # TODO: direct aproximation hardcoded for now
        # NOTE: what's stopping a member that knows the password to generate a bunch of tokens and them share them around?

        # if the password matches
        if self.password == password:
            
            # generates random unique association token
            token = None
            while token == None or token in self.association_tokens:
                random_bytes = bytearray(os.urandom(self.ASSOCIATION_TOKEN_LENGTH))
                token = base58.b58encode(random_bytes).decode('utf-8')
            self.association_tokens.add(token)

            # returns token as base58
            return base58.b58encode(token).decode('utf-8')

        # password does not match. return none
        else: 
            return None
