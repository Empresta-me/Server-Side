from src.crypto import Crypto # cryptographic functions
import base58 # for human friendly encoding

class Community:

    CHALLENGE_LENGTH = 16

    def __init__(self):
        # TODO: for now, it generates a new key each time. Implement persistance.
        self.private_key, self.public_key = Crypto.asym_gen()
        self.address = base58.b58encode(Crypto.serialize(self.public_key)).decode('utf-8')

    def reply_association(self, challenge : str):
        """Replies to association request with the response for the challenge issued"""
        # if the challenge is valid...
        if challenge and len(bytes(challenge, 'utf-8')) == self.CHALLENGE_LENGTH:
            # sign it and encode it to base58
            signature = base58.b58encode(Crypto.sign(self.private_key, challenge)).decode('utf-8')
            # return to the associate the public key plus the signature
            return { 'public_key' : self.address, 'response' : signature }
        # challenge missing or invalid
        else:
            return f"Challenge missing or incorrect length. Should be {self.CHALLENGE_LENGTH} bytes long.", 400
