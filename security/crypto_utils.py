"""
crypto_utils.py
----------------
Low-level cryptographic primitives used across the security layer.
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature


# -------------------------------------------------------------------
# 1. HASHING
# -------------------------------------------------------------------
def sha256(data: bytes) -> bytes:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    return digest.finalize()


def sha256_hex(data: bytes) -> str:
    return sha256(data).hex()


# -------------------------------------------------------------------
# 2. KEY GENERATION
# -------------------------------------------------------------------
def generate_rsa_keypair(key_size: int = 2048):
    """Generate a fresh RSA keypair. Returns (private_key, public_key)."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()
    return private_key, public_key


# -------------------------------------------------------------------
# 3. KEY SERIALIZATION (PEM)
# -------------------------------------------------------------------
def serialize_private_key(private_key, password: bytes | None = None) -> bytes:
    encryption = (
        serialization.BestAvailableEncryption(password)
        if password else serialization.NoEncryption()
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )


def serialize_public_key(public_key) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_private_key(pem_data: bytes, password: bytes | None = None):
    return serialization.load_pem_private_key(pem_data, password=password)


def load_public_key(pem_data: bytes):
    return serialization.load_pem_public_key(pem_data)


# -------------------------------------------------------------------
# 4. DIGITAL SIGNATURES (RSA-PSS + SHA-256)
# -------------------------------------------------------------------
def sign(private_key, message: bytes) -> bytes:
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verify(public_key, message: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False