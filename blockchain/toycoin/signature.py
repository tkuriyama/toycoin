# RSA keys and signatures.


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


################################################################################


Signature = bytes


################################################################################
# RSA Keys


def gen_priv_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """Generate RSA key with modulus of given size in bits."""
    return rsa.generate_private_key(public_exponent=65537, key_size=key_size)


def get_pub_key(priv_key: rsa.RSAPrivateKey) -> rsa.RSAPublicKey:
    """Get RSA pubic key from private key."""
    return priv_key.public_key()


def get_pub_key_bytes(priv_key: rsa.RSAPrivateKey) -> bytes:
    """Get Public Key in PEM format."""
    k = priv_key.public_key()
    return k.public_bytes(encoding=serialization.Encoding.PEM,
                          format=serialization.PublicFormat.SubjectPublicKeyInfo)


def load_pub_key_bytes(bs: bytes) -> rsa.RSAPublicKey:
    """LOad PEM-encoded Public Key."""
    return serialization.load_pem_public_key(bs)


b'hello world hash'################################################################################
# Signing


HASH = hashes.SHA512()

PADDING = padding.PSS(mgf=padding.MGF1(HASH),
                      salt_length=padding.PSS.MAX_LENGTH)


def sign(priv_key: rsa.RSAPrivateKey, msg: bytes) -> Signature:
    """Sign msg with RSA private key."""
    return priv_key.sign(msg, PADDING, HASH)


def verify(signature: Signature, pub_key: rsa.RSAPublicKey, msg: bytes) -> bool:
    """Verify msg signature with RSA public key."""
    try:
        pub_key.verify(signature, msg, PADDING, HASH)
    except:
        return False
    return True
