"""
security
--------
Cybersecurity layer for the MARL-driven traffic management system.

Public API:
    - Crypto primitives:  sha256, sign, verify, generate_rsa_keypair
    - PKI:                CertificateAuthority, verify_certificate
    - Messaging:          SecureMessage, new_message
    - Transport:          SecureChannel (TLS 1.3 mTLS wrapper)
    - Emergency auth:     EmergencyDispatchAuthority, EmergencyToken,
                          validate_emergency_token
    - Agent wrapper:      SecureAgent
    - Attack demos:       run_all_attacks, attempt_tampering, ...
"""

from .crypto_utils import (
    sha256, sha256_hex, sign, verify, generate_rsa_keypair,
    serialize_private_key, serialize_public_key,
    load_private_key, load_public_key,
)
from .pki import CertificateAuthority, verify_certificate
from .secure_message import SecureMessage, new_message, FRESHNESS_WINDOW_SECONDS
from .secure_channel import SecureChannel
from .emergency_auth import (
    EmergencyToken, EmergencyDispatchAuthority, validate_emergency_token,
)
from .secure_agent import SecureAgent
from . import attack_simulator

__all__ = [
    "sha256", "sha256_hex", "sign", "verify", "generate_rsa_keypair",
    "serialize_private_key", "serialize_public_key",
    "load_private_key", "load_public_key",
    "CertificateAuthority", "verify_certificate",
    "SecureMessage", "new_message", "FRESHNESS_WINDOW_SECONDS",
    "SecureChannel",
    "EmergencyToken", "EmergencyDispatchAuthority", "validate_emergency_token",
    "SecureAgent",
    "attack_simulator",
]