from src.crypto import Crypto # cryptographic functions
from src.pub_sub import pub_sub
from src.redis_interface import RedisInterface
import base58 # for human friendly encoding
import os # TODO explain
import configparser # TODO explain
from src.protocol import *
from src.authentication import *
from src.network import Network
import json
import hashlib

class Community:

    CHALLENGE_LENGTH = 16
    ASSOCIATION_TOKEN_LENGTH = 16
    POW_LENGTH = 8

    ASSOCIATION_KEY = "ASSOCIATION"
    CHALLENGE_KEY = "CHALLENGE"
    ACCOUNT_KEY = "ACCOUNT"
    ACCINFO_KEY = "ACCINFO"

    ALIASES = ['Anonymous Fox','Anonymous Rat','Anonymous Bat','Anonymous Cat', 'Anonymous Dog', 'Anonymous Bunny', 'Anonymous Bird', 'Anonymous Penguin', 'Anonymous Hamster', 'Anonymous Shark', 'Anonymous Wombat', 'Anonymous Bear']

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

        self.challenges = RedisInterface()

        # set of association tokens issued. removed as soon as they are used
        # NOTE: as the existing association tokens are stored in memory, server reboots will clean it. have to keep in mind when doing the frontend that "lost" tokens can exist
        self.association_tokens = RedisInterface(db=1) # set is called "association_tokens"

        self.accounts = RedisInterface(db=2)

        self.acc_info = RedisInterface(db=3)

        # NOTE: authentication is direct approx. by default
        self.auth = DirectApproximation(config['SECURITY']['password'], self.ASSOCIATION_TOKEN_LENGTH)
        #self.auth = IDP(config['SECURITY']['password'], self.ASSOCIATION_TOKEN_LENGTH)

        self.network = Network()

        # TODO: Remove later
        #pub_sub.start_listening(user_pub_key="ndShu87QAz6cxEhFN2arSuKRmY9A848mMqwKnQYVuMwj", on_message=self.handle_message)


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
        while (not token) or (self.association_tokens.sismember(self.ASSOCIATION_KEY, token)):
            token = self.auth.authenticate(data)

        # save token
        if token:
            self.association_tokens.sadd(self.ASSOCIATION_KEY, token)

        # returns either a token or none
        return token


    def issue_authentication_challenge(self, token : str, public_key : str) -> str:
        """Verifies the key and issues a registration challenge"""

        # TODO: Redis - must not be alerady registered
        
        # token must be valid
        if self.association_tokens.sismember(self.ASSOCIATION_KEY, token) == False:
            return None

        # discard token
        self.association_tokens.srem(self.ASSOCIATION_KEY, token)

        # verifies if the public key is valid
        if len(base58.b58decode(public_key)) == 33:

            # overrides the previous challenge if there's already one
            # NOTE: chould this allow a DoS attack? spamming for new challenges so that someone cant respond to the challenge

            # generate challenges and store it (tied to the public key)
            challenge = os.urandom(self.CHALLENGE_LENGTH)
            self.challenges.hset(self.CHALLENGE_KEY, public_key, challenge)

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
        if not self.challenges.hexists(self.CHALLENGE_KEY, public_key):
            return False

        # gets challenge and removes it
        challenge = self.challenges.hget(self.CHALLENGE_KEY, public_key)
        self.challenges.hdel(self.CHALLENGE_KEY, public_key)

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))

        print(str(challenge) + ' = '+str(type(challenge)))
        if not Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8'))):
            return False

        # store new account in db
        self.accounts.hset(self.ACCOUNT_KEY, public_key, str(account)) 

        # subscribe to the users exchange (queue) 
        #pub_sub.start_listening(user_pub_key=public_key, on_message=self.handle_message)

        return True

    def login(self, public_key : str, response : str) -> bool:
        """Verifies that an account is registered and that the challenge response is valid"""

        # TODO: Redis - public key must be registered

        # there must be a valid challenge pending for this account
        if not self.challenges.hexists(self.CHALLENGE_KEY, public_key):
            return False

        # gets challenge and removes it
        challenge = self.challenges.hget(self.CHALLENGE_KEY, public_key)
        self.challenges.hdel(self.CHALLENGE_KEY, public_key)

        # challenge, key and response should match
        # if the challenge is valid, then the login is successful
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))
        return Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8')))

    def store_key(self, public_key : str, private_key : str, response : str) -> bool:
        """Stores a (encrypted) version of an user's private key on their behalf if the user is registerd and the response matches the challange and public key"""

        # TODO: validate size
        # TODO: Redis - public key must be registered

        # there must be a valid challenge pending for this account
        if not self.challenges.get(public_key):
            return False

        # gets challenge and removes it
        challenge = self.challenges.hdel(self.CHALLENGE_KEY, public_key)

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
        if not self.challenges.hexists(self.CHALLENGE_KEY, public_key):
            return False

        # gets challenge and removes it
        challenge = self.challenges.hdel(self.CHALLENGE_KEY, public_key)

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(public_key,'utf-8')))
        if not Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8'))):
            return False

        # TODO: Redis - if the private key is not in storage...
        if False:
            raise ResourceWarning(f'There were no private keys stored under the public key {public_key}.')

        # TODO: Redis - remove key from storage

        return True

    def get_topology(self, observer_address : str, use_aliases : bool = False):
        diagram = self.network.gen_diagram(observer_address)

        res = str(diagram) 

        return res
    
    def get_topology_diagram(self, observer_address : str, use_aliases : bool = True):
        diagram = self.network.gen_diagram(observer_address)

        res = str(diagram)

        def get_alias(key):
            h = hashlib.md5(key.encode('UTF-8'))
            int_val = int.from_bytes(h.digest(), "big")
            index = int_val % len(self.ALIASES)
            return self.ALIASES[index]

        if use_aliases and diagram and diagram['nodes']:
            nodes = [i['name'] for i in diagram['nodes']]

            for node in nodes:

                if node == '(You)':
                    res = res.replace(observer_address,'(You)')
                    continue

                info = self.get_account_info(observer_address, node)
                if info:
                    info = info.replace("'",'"') # kill me please
                    name = json.loads(info)['alias']
                    res = res.replace(node,name)
                else:
                    name = get_alias(node)
                    res = res.replace(node,name)
        
        return res

    def request_info(self, host_key : str, guest_key : str):
        # there must be a valid challenge pending for this account
        """
        if self.challenges.get(host_key) == None:
            return False
        """

        # gets challenge and removes it
        challenge = self.challenges.hdel(self.CHALLENGE_KEY, host_key)

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(host_key,'utf-8')))
        # if not valid, deny request
        """
        if not Crypto.verify(k, challenge, base58.b58decode(bytes(response,'utf-8'))):
            return False
        """

        return self.get_account_info(host_key, guest_key)


    def get_account_info(self, host_key : str, guest_key : str) -> str:
        permit_list = self.acc_info.hget(self.ACCINFO_KEY, guest_key)

        if not permit_list:
            permit_list = set([])
        else:
            # turn the string into a set
            permit_list = set(permit_list.decode('utf-8').split(','))

        if host_key in permit_list:
            return self.accounts.hget(self.ACCOUNT_KEY, guest_key).decode('utf-8')
        else:
            return None


    def permit_info(self, host_key : str, guest_key : str):
        # there must be a valid challenge pending for this account

        # gets challenge and removes it
        challenge = self.challenges.hdel(self.CHALLENGE_KEY, host_key)

        # challenge, key and response should match
        k = Crypto.load_key(base58.b58decode(bytes(host_key,'utf-8')))
        # if not valid, deny request

        permit_list = self.acc_info.hget(self.ACCINFO_KEY, host_key)

        if not permit_list:
            permit_list = set([])
        else:
            # turn the string into a set
            permit_list = set(permit_list.decode('utf-8').split(','))

        permit_list.add(guest_key)

        self.acc_info.hset(self.ACCINFO_KEY, host_key, ','.join(permit_list))

        return True

    def handle_message(self, channel, method, properties, body): 
        print("Received message: {}".format(body.decode()), flush=True)
        msg_str = body.decode()
        msg = Proto.parse(msg_str)

        if msg.header == 'VOUCH':
            self.handle_vouch(msg)
        print("Delivery tag:", method.delivery_tag)
        #channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True) 

    def handle_vouch(self, msg : VouchMessage):
        """Handles vouch messages"""
        print("Verifying vouch message...")

        valid = True
        '''
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

        # TODO: remove this
        valid = True
        '''
        if valid:
            print('\t[v] Message is valid!')
            self.network.new_vouch(msg)
        else:
            print('\t[x] Message is invalid!')
