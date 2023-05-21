import json # for serialization

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
        self.none = nonce
        self.hash = hash
        self.signature = signature

    def verify_participants(self, participant : str) -> bool:
        return self.sender == participant or self.receiver == participant

    def hash() -> str:
        pass

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
