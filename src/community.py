from src.crypto import Crypto # cryptographic functions
import base58 # for human friendly encoding
import os # TODO explain
import configparser # TODO explain

class Community:

    CHALLENGE_LENGTH = 16
    ASSOCIATION_TOKEN_LENGTH = 16

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('config/config.ini') 

        # TODO: for now, it generates a new key each time. Implement persistance.
        self.private_key, self.public_key = Crypto.asym_gen()
        self.address = base58.b58encode(Crypto.serialize(self.public_key)).decode('utf-8') # public key encoded as base58 string

        self.title = config['DETAILS']['title']           
        self.bio = config['DETAILS']['bio']               
        self.password = config['DETAILS']['password']      

        # set of association tokens issued. removed as soon as they are used
        # NOTE: as the existing association tokens are stored in memory, server reboots will clean it. have to keep in mind when doing the frontend that "lost" tokens can exist
        # TODO: move this to redis
        self.association_tokens = set()

        # TODO: move this to redis
        self.register_challenges = {}

    def get_info(self) -> dict:
        """Shares community public information"""
        return {'title' : self.title, 'bio' : self.bio, 'public_key' : self.address }

    def reply_challenge(self, challenge : str) -> dict:
        """Answers to base58 challenge with signature"""

        # challenge in bytes
        challenge_b = base58.b58decode(bytes(challenge,'utf-8'))

        # length should match
        if len(challenge_b) != self.CHALLENGE_LENGTH:
            return None

        # sign it and encode it to base58
        signature = base58.b58encode(Crypto.sign(self.private_key, challenge_b)).decode('utf-8')

        # return to the associate the public key plus the signature plus the session token
        return { 'public_key' : self.address, 'response' : signature }

    def issue_association_token(self, password : str) -> bool:
        """Verifies association attempt from member and returns token"""
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
            return token

        # password does not match. return none
        else: 
            return None

    def issue_authentication_challenge(self, token : str, public_key : str) -> str:
        """Verifies the key and issues a registration challenge"""

        # TODO: Redis - must not be alerady registered
        
        # token must be valid
        # TODO: Redis
        if token not in self.association_tokens:
            return None

        # discard token
        self.association_tokens.remove(token)

        # verifies if the public key is valid
        if len(base58.b58decode(public_key)) == 33:

            # overrides the previous challenge if there's already one
            # NOTE: chould this allow a DoS attack? spamming for new challenges so that someone cant respond to the challenge

            # generate challenges and store it (tied to the public key)
            challenge = bytearray(os.urandom(self.CHALLENGE_LENGTH))
            self.register_challenges[public_key]= challenge

            # returns token as base58
            return base58.b58encode(challenge).decode('utf-8')
        # invalid key, return nothing
        else:
            return None

    def register_account(self, account : dict) -> bool:
        """Registers an account if the challenge response was valid. Returns true or false"""

        # get fields from account
        try:
            # TODO: validate proper field length
            public_key = account['public_key']
            alias = account['alias']
            bio = account['bio']
            contact = account['contact']
            custom = account['custom']

            # not part of the account, but necessary for registering
            response = account['response']
        # account is missing a field. registration failed
        except:
            return False

        # there must be a valid challenge pending for this account
        if public_key not in self.register_challenges.keys():
            return False

        challenge = self.register_challenges[public_key]

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))

        if not Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8'))):
            return False

        #TODO: Redis - store account here

        return True
