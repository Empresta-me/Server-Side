from src.crypto import Crypto # cryptographic functions
import base58 # for human friendly encoding

class Community:

    CHALLENGE_LENGTH = 16

    def __init__(self):
        # TODO: for now, it generates a new key each time. Implement persistance.
        self.private_key, self.public_key = Crypto.asym_gen()
        self.address = base58.b58encode(Crypto.serialize(self.public_key)).decode('utf-8') # public key encoded as base58 string

        # TODO : fow now, hardcoded data. Implement persistance
        self.title = "DETI Community"
        self.bio = "Univeristy of Aveiro's first EMPRESTA.ME community!"

        # dictonary for associates. the value represents whether the member has acknowledge the association
        self.associates = {}

    def get_info(self) -> dict:
        return {'title' : self.title, 'bio' : self.bio, 'public_key' : self.address }

    def verify_key(self, challenge : str) -> dict:
        """Answears to challenge with signature"""

        # sign it and encode it to base58
        signature = base58.b58encode(Crypto.sign(self.private_key, challenge)).decode('utf-')

        # return to the associate the public key plus the signature plus the session token
        return { 'public_key' : self.address, 'response' : signature }

    def association_ack(self):
        """Acknowledges the member's acknowledgemenet; If everything's correct, the member is now associated"""
        pass
