from src.crypto import Crypto

class Community:

    CHALLENGE_LENGTH = 16

    def __init__(self):
        self.private_key, self.public_key = Crypto.asym_gen()
        self.address = Crypto.get_public_numbers(self.public_key)

    def reply_association(self, challenge : str):
        """Replies to association request with the response for the challenge issued"""
        # if the challenge if valid
        if challenge and len(bytes(challenge, 'utf-8')) == self.CHALLENGE_LENGTH:
            signature = Crypto.sign(self.private_key, challenge)
            return { 'public_key' : self.address, 'response' : str(signature) }
        # challenge missing or invalid
        else:
            return "Challenge missing or incorrect length.", 400
