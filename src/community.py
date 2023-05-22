from src.crypto import Crypto # cryptographic functions
from src.pub_sub import pub_sub
from src.redis_interface import Redis_interface
import base58 # for human friendly encoding
import os # TODO explain
import configparser # TODO explain
from src.protocol import *
from src.authentication import DirectApproximation

class Community:

    CHALLENGE_LENGTH = 16
    ASSOCIATION_TOKEN_LENGTH = 16
    POW_LENGTH = 8

    def __init__(self, key_encryption_password : str):
     
        # gets public and private key from PEM file
        with open("config/key.pem", "rb") as key_file: 
            self.private_key = Crypto.PEM_to_private_key(key_file.read(), bytes(key_encryption_password,'utf-8'))
            self.public_key =  self.private_key.public_key()
        self.address = base58.b58encode(Crypto.serialize(self.public_key)).decode('utf-8')

        # gets community data from config file
        config = configparser.ConfigParser()
        config.read('config/config.ini') 

        self.title = config['DETAILS']['title']           
        self.bio = config['DETAILS']['bio']               

        self.challenges = Redis_interface()

        # set of association tokens issued. removed as soon as they are used
        # NOTE: as the existing association tokens are stored in memory, server reboots will clean it. have to keep in mind when doing the frontend that "lost" tokens can exist
        self.association_tokens = Redis_interface(db=1) # set is called "association_tokens"

        self.accounts = Redis_interface(db=2)

        # NOTE: Inês, é aqui que é definido se vai usar a strategy do IDP ou por senha
        self.auth = DirectApproximation(config['SECURITY']['password'], self.ASSOCIATION_TOKEN_LENGTH)


        # TODO: remove later, this is for testing
        self.handle_vouch(Proto.parse('{"header": "VOUCH", "state": "FOR", "clock": 0, "sender": "ohpr4EZuEepgEQp6Ne897K8BTmPTXSE62Jo2ukGo9NyA", "receiver": "yLj9ATsVwBogUZEB2QTbPh7eu77QgppaiMQP97YVeq3L", "message": "Test message", "nonce": 8, "hash": "1VvbYB6G8hgciobvpceEE8boyxBNwUpGeYhiLRuTY3a", "signature": "AN1rKoYGLmkKX2iaLmLoZmLm79ADpP8kzjbuhMGJAqtFbHJuEqpUetgBvUbD88Nk8UnvuEUqjTkpXguqWZ1zRQ7MdD9HxSxhS"}'))

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

    def issue_association_token(self, data : str) -> bool:
        """Verifies association attempt from member and returns token"""
        token = None
        
        # repeats until token is not null and not already existing
        while (not token) or (self.association_tokens.isInSet("association_tokens", token)):
            token = self.auth.authenticate(data)

        # save token
        if token:
            self.association_tokens.addToSet("association_tokens",token)

        # returns either a token or none
        return token


    def issue_authentication_challenge(self, token : str, public_key : str) -> str:
        """Verifies the key and issues a registration challenge"""

        # TODO: Redis - must not be alerady registered
        
        # token must be valid
        if self.association_tokens.isInSet("association_tokens", token) == False:
            print(':(')
            return None

        # discard token
        self.association_tokens.delFromSet("association_tokens", token)

        # verifies if the public key is valid
        if len(base58.b58decode(public_key)) == 33:

            # overrides the previous challenge if there's already one
            # NOTE: chould this allow a DoS attack? spamming for new challenges so that someone cant respond to the challenge

            # generate challenges and store it (tied to the public key)
            challenge = os.urandom(self.CHALLENGE_LENGTH)
            self.challenges.set(public_key, challenge)

            # returns token as base58
            return base58.b58encode(challenge).decode('utf-8')
        # invalid key, return nothing
        else:
            return None

    def register(self, account : dict) -> bool:
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
        if self.challenges.get(public_key) == None:
            return False
        print('challenge:' + str(self.challenges.get(public_key)))

        # gets challenge and removes it
        challenge = self.challenges.pop(public_key)

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))

        print('pk:' + str(base58.b58decode(bytes(public_key,'utf-8'))))
        print('challenge: ' + str(challenge))
        print('response: ' + str(base58.b58decode(bytes(response,'utf-8'))))

        if not Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8'))):
            return False

        # store new account in db
        self.accounts.newHashSet(public_key, account) 

        # subscribe to the users exchange (queue) 
        pub_sub.start_listening(user_pub_key=public_key, on_message=self.handle_message)

        return True

    def login(self, public_key : str, response : str) -> bool:
        """Verifies that an account is registered and that the challenge response is valid"""

        # TODO: Redis - public key must be registered

        # there must be a valid challenge pending for this account
        if self.challenges.get(public_key) == None:
            return False

        # gets challenge and removes it
        challenge = self.challenges.pop(public_key)

        # challenge, key and response should match
        # if the challenge is valid, then the login is successful
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))
        return Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8')))

    def store_key(self, public_key : str, private_key : str, response : str) -> bool:
        """Stores a (encrypted) version of an user's private key on their behalf if the user is registerd and the response matches the challange and public key"""

        # TODO: validate size
        # TODO: Redis - public key must be registered

        # there must be a valid challenge pending for this account
        if self.challenges.get(public_key) == None:
            return False

        # gets challenge and removes it
        challenge = self.challenges.pop(public_key)

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))
        if not Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8'))):
            return False

        # TODO: Redis - store key here

        return True

    def delete_key(self, public_key : str, private_key : str, response : str) -> bool:
        """Stores a (encrypted) version of an user's private key on their behalf if the user is registerd and the response matches the challange and public key"""

        # TODO: validate size

        # TODO: Redis - public key must be registered

        # there must be a valid challenge pending for this account
        if self.challenges.get(public_key) == None:
            return False

        # gets challenge and removes it
        challenge = self.challenges.pop(public_key)

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))
        if not Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8'))):
            return False

        # TODO: Redis - if the private key is not in storage...
        if False:
            raise ResourceWarning(f'There were no private keys stored under the public key {public_key}.')

        # TODO: Redis - remove key from storage

        return True

    def get_topology(self, observer_address : str):
        pass
    
    def handle_message(self, channel, method, properties, body): 
        print("Received message: {}".format(body.decode()), flush=True)
        msg_str = body.decode()
        msg = Proto.parse(msg_str)

        if msg.header == 'VOUCH':
            self.handle(msg)

    def handle_vouch(self, msg : VouchMessage):
        """Handles vouch messages"""
        print("Verifying vouch message...")

        valid = True

        # TODO: are accounts registered?

        if not msg.verify_general():
            print("\t[!] Failed general verification")
            valid = False

        if not msg.verify_participants(''):
            print("\t[!] Participants does not match")
            valid = False

        if not msg.verify_signature():
            print("\t[!] Signature does not match")
            valid = False

        if not msg.verify_pow(self.POW_LENGTH):
            print("\t[!] Proof of work does not match")
            valid = False

        if valid:
            print('\t[v] Message is valid!')
        else:
            print('\t[x] Message is invalid!')
