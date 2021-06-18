
# Hashing.


from cryptography.hazmat.primitives import hashes # typing: ignore


################################################################################


Digest = bytes


def hash(msg: bytes, algo = hashes.SHA512()) -> Digest:
    """Hash given msg32."""
    digest = hashes.Hash(algo)
    digest.update(msg)
    return digest.finalize()
