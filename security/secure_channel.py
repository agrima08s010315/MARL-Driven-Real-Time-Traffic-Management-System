"""
secure_channel.py
-----------------
TLS 1.3 mutual-authentication (mTLS) socket wrapper.

While `secure_message` gives us application-layer signing, `secure_channel`
adds transport-layer security: the TCP stream itself is encrypted and
both endpoints authenticate each other with X.509 certificates.

Defense-in-depth rationale:
    - Signing alone protects individual messages but an attacker can
      still see them in cleartext, correlate traffic patterns, and
      learn which intersection is congested.
    - TLS alone secures the channel but once an attacker compromises
      one endpoint, they can inject bogus signed messages.
    - Combining both means an attacker needs (a) to break TLS 1.3 AND
      (b) to steal an agent's private key to do real damage.

TLS 1.3 was chosen because:
    - It's the current IETF standard (RFC 8446)
    - Removes all legacy weak ciphers (RC4, CBC, SHA-1, etc.)
    - Mandatory forward secrecy (ephemeral Diffie-Hellman)
    - 1-RTT handshake -- ~50% faster than TLS 1.2
"""

import socket
import ssl
import tempfile
import os

from cryptography.hazmat.primitives import serialization
from cryptography import x509

from .crypto_utils import serialize_private_key


class SecureChannel:
    """
    Thin wrapper over an SSL-wrapped socket with TLS 1.3 enforced
    and mutual certificate verification required.
    """

    def __init__(
        self,
        identity_cert: x509.Certificate,
        identity_private_key,
        ca_cert: x509.Certificate,
        is_server: bool,
    ):
        self.is_server = is_server
        # SSLContext needs certs as files on disk. We write them to a
        # tempdir that we clean up later.
        self._tmpdir = tempfile.mkdtemp(prefix="trafficnet_tls_")
        self._cert_path, self._key_path, self._ca_path = self._write_pem_files(
            identity_cert, identity_private_key, ca_cert
        )
        self.context = self._build_context()

    def _write_pem_files(self, cert, private_key, ca_cert):
        cert_path = os.path.join(self._tmpdir, "cert.pem")
        key_path = os.path.join(self._tmpdir, "key.pem")
        ca_path = os.path.join(self._tmpdir, "ca.pem")

        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(key_path, "wb") as f:
            f.write(serialize_private_key(private_key))
        with open(ca_path, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        # 0o600 on key file -- OpenSSL will refuse keys that are
        # world-readable on some platforms.
        os.chmod(key_path, 0o600)
        return cert_path, key_path, ca_path

    def _build_context(self) -> ssl.SSLContext:
        """Build an SSLContext with TLS 1.3 and mTLS enforced."""
        purpose = ssl.Purpose.CLIENT_AUTH if self.is_server else ssl.Purpose.SERVER_AUTH
        ctx = ssl.create_default_context(purpose=purpose, cafile=self._ca_path)

        # Lock to TLS 1.3 on both sides. Anything lower -> hard fail.
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.maximum_version = ssl.TLSVersion.TLSv1_3

        # Load our own identity
        ctx.load_cert_chain(certfile=self._cert_path, keyfile=self._key_path)

        # Mutual auth -- server demands client cert; client already verifies
        # server cert via create_default_context.
        if self.is_server:
            ctx.verify_mode = ssl.CERT_REQUIRED

        return ctx

    def wrap_server(self, sock: socket.socket) -> ssl.SSLSocket:
        """Wrap an accept()-ready server socket."""
        return self.context.wrap_socket(sock, server_side=True)

    def wrap_client(self, sock: socket.socket, server_hostname: str) -> ssl.SSLSocket:
        """Wrap a connect()-ready client socket."""
        return self.context.wrap_socket(sock, server_hostname=server_hostname)

    def cleanup(self):
        """Wipe temp PEM files."""
        for p in (self._cert_path, self._key_path, self._ca_path):
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(self._tmpdir)
        except OSError:
            pass