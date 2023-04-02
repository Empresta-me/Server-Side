from cryptography.hazmat.primitives import hashes 
from cryptography.exceptions import InvalidSignature 
from cryptography.hazmat.primitives.asymmetric import ec  
from cryptography.hazmat.primitives import serialization

class Crypto:
    """Cryptographic utilities""" 

    @classmethod
    def hash(cls, data: bytes) -> bytes:
        """Returns an SHA256 hash of a given data"""
        
        digest = hashes.Hash(hashes.SHA256()) 
        digest.update(data)    
        hash = digest.finalize().hex()
        
        return hash 

    @classmethod
    def asym_gen(cls) -> tuple:
        """Generates a new EC asymmetric key pair object"""
        
        # Generation 
        private_key = ec.generate_private_key(
            ec.SECP256K1()
        )
        
        return ( private_key, private_key.public_key())

    @classmethod
    def sign(cls, private_key, data : bytes) -> bytes:
        """Returns signature of given data signed with given private key""" 
    
        signature = private_key.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )

        return signature 

    @classmethod
    def verify(cls, public_key, message : bytes, signature : bytes) -> bool:
        """Verifies if given message matches with given signature"""

        try:  
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature:
            return False
        except Exception as e:
            raise e
            return False

        return True
     
    @classmethod
    def get_public_numbers(cls, public_key) -> tuple:
        """ Gets the x and y points that define the publlic key """ 
        
        (x,y) = (public_key.public_numbers().x, public_key.public_numbers().y)
        
        return (x,y)
    
    @classmethod
    def numbers_to_public_key(cls, x: int, y: int) -> str:
        """ Generate a public key Object based on the x and y points that defines them """ 
        
        p_k = ec.EllipticCurvePublicNumbers(x,y,ec.SECP256K1()).public_key()

        return p_k

    @classmethod
    def serialize(cls, public_key) -> bytes:
        """ Generate a public key Object based on the x and y points that defines them """ 
        
        serialized_public = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        ) 

        return serialized_public
    
    @classmethod
    def load_key(cls, serialized_public : bytes) :
        """ Generate a public key Object based on the x and y points that defines them """ 
        loaded_public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), serialized_public)
        return loaded_public_key

""" 

# Generate key pair 
(prv_k, pbl_k) = Crypto.asym_gen()

# Sign with private key
message = b'pls work! I rly need this'
signature = Crypto.sign(prv_k, message)

# get the numbers & Generate public key
(x,y) = Crypto.get_public_numbers(pbl_k)
new_pbl_key = Crypto.numbers_to_public_key(x,y) 

ser = Crypto.serialize(new_pbl_key)
 
print(ser)
new_new_P = Crypto.load_key(ser)

# test the signature with the orivate key 
print("Sgnature: " + str(Crypto.verify(new_new_P, b'pls work! I rly need this', signature))) 

 
"""
