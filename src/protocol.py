import json # for serialization
from src.crypto import Crypto # cryptographic functions
import math
import base58

class Message:
    """Generic message"""
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False)

    def __str__(self):
        return self.to_json()

    def verify_general(self) -> bool:
        return True
    
    def verify_participants(self, participant : str) -> bool:
        return True

    def verify_signature(self) -> bool:
        return True

    def verify_pow(self, zeros : int) -> bool:
        return True

class VouchMessage(Message):
    """Vouch"""
    def __init__(self, state : str, clock : int, sender : str, receiver : str, message : str, nonce : int, hash : str, signature : str):
        self.header = 'VOUCH'
        self.state = state
        self.clock = clock
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.nonce = nonce
        self.hash = hash
        self.signature = signature

    def verify_general(self) -> bool:
        return type(self.clock) is int

    def verify_participants(self, participant : str) -> bool:
        return self.sender == participant or self.receiver == participant

    def verify_signature(self) -> bool:
            key = Crypto.load_key(base58.b58decode(self.sender))

            sig = base58.b58decode(bytes(self.signature,'utf-8'))

            return Crypto.verify(key, self.gen_hash(), sig)

    def verify_pow(self, zeros : int) -> bool:
        b = math.ceil(zeros/8)

        b_hash = base58.b58decode(bytes(self.hash,'utf-8'))

        return "0"*zeros == "{:08b}".format(int(b_hash[0:b].hex(),16))[0:zeros]

    def gen_hash(self) -> str:
        data = self.state+str(self.clock)+self.sender+self.receiver+self.message+str(self.nonce)
        return Crypto.hash(bytes(data,'utf-8'))

    @classmethod
    def parse(cls, j : str):
        return VouchMessage(j['state'],j['clock'],j['sender'],j['receiver'], j['message'], j['nonce'], j['hash'], j['signature'])

class Proto:
    @classmethod
    def parse(self, msg_str: str):
        if not msg_str:
            return None

        j = json.loads(msg_str)

        if j['header'] == 'VOUCH':
            return VouchMessage.parse(j)
        else:
            raise ProtoBadFormat(msg_str)

class ProtoBadFormat(Exception):
    """Exception when source message is not Proto."""

    def __init__(self, original_msg: str=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
