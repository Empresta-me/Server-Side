from cryptography.hazmat.primitives import hashes 
from cryptography.exceptions import InvalidSignature 
from cryptography.hazmat.primitives.asymmetric import ec  
from cryptography.hazmat.primitives import serialization
import math
import base58 # for human friendly encoding
import json

ZEROS = 8
BYTES = math.ceil(ZEROS/8)

def gen_key():
    private_key = ec.generate_private_key(
        ec.SECP256K1()
    )
    
    return private_key

def gen_hash(data: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256()) 
    digest.update(data)    
    hash = digest.finalize()#.hex()
    
    return hash 

def get_public_key(public_key):
    serialized_public = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint
    ) 
    return serialized_public

def sign(private_key, data : bytes) -> bytes:
    signature = private_key.sign(
        data,
        ec.ECDSA(hashes.SHA256())
    )

    return signature 

def verify(public_key, message : bytes, signature : bytes) -> bool:
    """Verifies if given message matches with given signature"""

    try:  
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        return False
    except Exception as e:
        raise e
        return False

    return True
     

state = 'FOR'
clock = 0
sender_key = gen_key()
sender = base58.b58encode(get_public_key(sender_key.public_key())).decode('utf-8')
receiver = base58.b58encode(get_public_key(gen_key().public_key())).decode('utf-8')
message = 'Test message'

nonce = 0
hash = None
while hash == None or "0"*ZEROS != "{:08b}".format(int(hash[0:BYTES].hex(),16))[0:ZEROS]:
    nonce += 1
    data = state+str(clock)+sender+receiver+message+str(nonce)

    hash = gen_hash(bytes(data,'utf-8'))

    binary_string = "{:08b}".format(int(hash[0:BYTES].hex(),16))[0:ZEROS]
    print(binary_string)

print('\n\n\n')

signature = sign(sender_key, hash)

# TAMPER WITH HASH TO BREAK POW
"""
hash = b'FF' + hash[1:]
binary_string = "{:08b}".format(int(hash[0:BYTES].hex(),16))[0:ZEROS]
print(binary_string)
"""

msg = {'header':'VOUCH','state':state,'clock':clock,'sender':sender,'receiver':receiver,'message':message,'nonce':nonce,'hash':base58.b58encode(hash).decode('utf-8'),'signature':base58.b58encode(signature).decode('utf-8')}

print(json.dumps(msg))
