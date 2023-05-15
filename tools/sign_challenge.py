#!/usr/bin/python3
from cryptography.hazmat.primitives import hashes 
from cryptography.exceptions import InvalidSignature 
from cryptography.hazmat.primitives.asymmetric import ec  
from cryptography.hazmat.primitives import serialization
import sys
import base58

def PEM_to_private_key(PEM_content : bytes, password : bytes) :
    """ Returns a private key object given a PEM content """ 
    
    loaded_private_key = serialization.load_pem_private_key(
        PEM_content, 
        password=password,
    )
    return loaded_private_key

def serialize(public_key) -> bytes:
    """ Generate a public key Object based on the x and y points that defines them """ 
    
    serialized_public = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint
    ) 

    return serialized_public

with open("key.pem", "rb") as key_file: 
    private_key = PEM_to_private_key(key_file.read(), bytes('testpassword','utf-8'))
    public_key =  private_key.public_key()
address = base58.b58encode(serialize(public_key)).decode('utf-8')

print('Public key: ' + address)

if len(sys.argv) >= 2:
    print('Challenge: ' + sys.argv[1])
    signature = private_key.sign(
        bytes(sys.argv[1],'utf-8'),
        ec.ECDSA(hashes.SHA256())
    )

    print('Signature: ' + base58.b58encode(signature).decode('utf-8'))
