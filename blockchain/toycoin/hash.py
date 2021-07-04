""" Hashing."""


from cryptography.hazmat.primitives import hashes # type: ignore


################################################################################

Hash = bytes


def hash(msg: bytes, algo = hashes.SHA512()) -> Hash:
    """Hash given msg."""
    digest = hashes.Hash(algo)
    digest.update(msg)
    return digest.finalize()
