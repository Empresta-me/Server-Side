from cryptography.hazmat.primitives import hashes 
from cryptography.exceptions import InvalidSignature 
from cryptography.hazmat.primitives.asymmetric import ec  

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
        """Generates a new asymmetric key(Object) pair"""
        
        # Generation 
        private_key = ec.generate_private_key(
            ec.SECP384R1()
        )
        
        return ( private_key, private_key.public_key())

    @classmethod
    def sign(cls, private_key: str, data) -> bytes:
        """Returns signature of given data signed with given private key""" 
 
        if(type(data) != bytes):
            data = data.encode()
    
        signature = private_key.sign(
            data,
            ec.ECDSA(hashes.SHA256())
        )

        return signature

    @classmethod
    def verify(cls, public_key, message, signature: bytes) -> bool:
        """Verifies if given message matches with given signature"""
          
        if(type(message) != bytes):
            message = message.encode()

        try:  
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature:
            return False
        except:
            print("Unidentified Error")
            return False

        return True
     
    @classmethod
    def get_public_numbers(cls, public_key):
        """ Gets the x and y points that define the publlic key """ 
        
        (x,y) = (public_key.public_numbers().x, public_key.public_numbers().y)
        
        return  (x,y)
    
    @classmethod
    def numbers_to_public_key(cls, x: int, y: int) -> str:
        """ Generate a public key Object based on the x and y points that defines them """ 
        
        p_k = ec.EllipticCurvePublicNumbers(x,y,ec.SECP384R1()).public_key()

        return p_k

"""

# Generate key pair 
(prv_k, pbl_k) = Crypto.asym_gen()

# Sign with private key
message = b'pls work! I rly need this'
signature = Crypto.sign(prv_k, message)

# get the numbers & Generate public key
(x,y) = Crypto.get_public_numbers(pbl_k)
new_pbl_key = Crypto.numbers_to_public_key(x,y)

# test the signature with the orivate key 
print("Sgnature: " + str(Crypto.verify(new_pbl_key, b'pls work! I rly need this', signature))) 

"""
