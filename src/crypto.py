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
    
    #NOTE: Cuurently Unneened 
    @classmethod
    def public_key_to_PEM(cls, public_key) :
        """ Generate a PEM file given a public key object """ 
        
        serialized_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized_public
    
   #NOTE: Cuurently unecessary
    @classmethod
    def PEM_to_public_key(cls, PEM_content : bytes) :
        """ Returns a public key object given a PEM content """ 
        
        loaded_public_key = serialization.load_pem_public_key(
            PEM_content,
        )
        return loaded_public_key

    @classmethod
    def private_key_to_PEM(cls, private_key : bytes) :
        """ Generate a PEM file given a private key object """ 
        
        serialized_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(bytes('testpassword','utf-8'))
        )

        return serialized_private
     
    @classmethod
    def PEM_to_private_key(cls, PEM_content : bytes, password : bytes) :
        """ Returns a private key object given a PEM content """ 
        
        loaded_private_key = serialization.load_pem_private_key(
            PEM_content, 
            password=password,
        )
        return loaded_private_key

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

 


private_key, public_key = Crypto.asym_gen()

f = open("private.PEM", "wb")
f.write(Crypto.privateKey_to_PEM(private_key))
f.close()

f = open("public.PEM", "wb")
f.write(Crypto.publicKey_to_PEM(public_key))    
f.close()
"""
