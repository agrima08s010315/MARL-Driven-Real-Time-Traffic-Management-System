"""
pki.py
------
Mini Public Key Infrastructure (PKI) for the traffic network.

Why a PKI?
    Digital signatures prove a message came from someone who holds a
    specific private key -- but how do you know that private key
    belongs to "the traffic agent at Intersection A" and not an
    attacker? You bind the key to an identity using an X.509 certificate
    signed by a trusted Certificate Authority (CA).

    In the real world, governments run V2X CAs (e.g. the US SCMS).
    For our simulation we run a self-signed in-memory CA that issues
    certs for each intersection agent and each emergency vehicle.

Threat this stops:
    AGENT IMPERSONATION -- an attacker generates their own RSA keypair
    and claims to be "Intersection B". Without a CA-signed cert, other
    agents refuse to trust the keypair.
"""

import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

from .crypto_utils import generate_rsa_keypair


class CertificateAuthority:
    """
    Self-signed root CA for the traffic network.

    In production this would be an offline HSM-backed CA. Here we keep
    it in-memory for reproducibility -- the important property is that
    there's ONE CA and every agent cert chains back to it.
    """

    def __init__(self, name: str = "TrafficNet-RootCA"):
        self.name = name
        # CA's own keypair -- used to sign subordinate certs
        self.private_key, self.public_key = generate_rsa_keypair()
        self.certificate = self._build_self_signed_cert()
        # Running serial number -- every cert must have a unique one
        self._next_serial = 1000

    def _build_self_signed_cert(self) -> x509.Certificate:
        """Create the CA's own self-signed certificate."""
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, self.name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Smart Traffic Research"),
        ])
        now = datetime.datetime.now(datetime.timezone.utc)
        return (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self.public_key)
            .serial_number(1)
            .not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=3650))
            # CA-specific extension: marks this cert as allowed to sign others
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(self.private_key, hashes.SHA256())
        )

    def issue_certificate(self, common_name: str, subject_public_key) -> x509.Certificate:
        """
        Issue a leaf certificate for an agent / emergency vehicle.

        The returned cert is signed by the CA's private key, so anyone
        with the CA's public cert can verify it authentically binds
        `common_name` to `subject_public_key`.
        """
        self._next_serial += 1
        now = datetime.datetime.now(datetime.timezone.utc)

        cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ]))
            .issuer_name(self.certificate.subject)
            .public_key(subject_public_key)
            .serial_number(self._next_serial)
            .not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=365))
            # Leaf cert -- explicitly NOT a CA
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .sign(self.private_key, hashes.SHA256())
        )
        return cert


def verify_certificate(cert: x509.Certificate, ca_cert: x509.Certificate) -> bool:
    """
    Verify that `cert` was validly issued by `ca_cert`.

    Checks:
      1. Signature is valid under ca_cert's public key
      2. cert is within its validity window
      3. cert's issuer matches ca_cert's subject

    Any failure -> False.
    """
    try:
        # 1. Signature check
        ca_cert.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            asym_padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
    except Exception:
        return False

    # 2. Validity window
    now = datetime.datetime.now(datetime.timezone.utc)
    if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
        return False

    # 3. Issuer match
    if cert.issuer != ca_cert.subject:
        return False

    return True