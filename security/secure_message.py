"""
secure_message.py
-----------------
Defines the message envelope exchanged between traffic agents.

Every inter-agent message carries:
    - sender_id      : who claims to be sending it
    - receiver_id    : intended recipient (binds message to a route)
    - timestamp      : UTC epoch seconds -- freshness window
    - nonce          : 16 random bytes -- uniqueness per message
    - payload        : actual control data (JSON-serializable)
    - signature      : RSA-PSS signature over everything above
    - sender_hash    : SHA-256 of payload (redundant with signature but
                       explicit per project requirement + useful for logs)

Attacks prevented:

  TAMPERING       - any bit flipped in transit invalidates the signature
  IMPERSONATION   - attacker without sender's private key cannot sign
  REPLAY          - nonces are tracked; old timestamps are rejected
  MITM (payload)  - signature covers sender + receiver + payload, so
                    a middle-man cannot redirect a valid message
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any

from .crypto_utils import sign, verify, sha256_hex


# Messages older than this are rejected as stale. Traffic control
# updates at 1 Hz, so 10 s is generous but safe against clock drift.
FRESHNESS_WINDOW_SECONDS = 10


@dataclass
class SecureMessage:
    sender_id: str
    receiver_id: str
    payload: dict
    timestamp: float = field(default_factory=lambda: time.time())
    nonce: str = field(default_factory=lambda: os.urandom(16).hex())
    signature: str = ""       # hex-encoded
    sender_hash: str = ""     # hex-encoded SHA-256 of payload

    # -------- signing path --------
    def _canonical_bytes(self) -> bytes:
        """
        Produce the exact byte-string that gets signed.

        CRITICAL: both sender and receiver must compute this identically.
        We use JSON with sorted keys to eliminate dict-ordering ambiguity.
        The signature field itself is obviously excluded.
        """
        body = {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "sender_hash": self.sender_hash,
        }
        return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign_with(self, private_key) -> "SecureMessage":
        """Populate sender_hash and signature using `private_key`."""
        self.sender_hash = sha256_hex(
            json.dumps(self.payload, sort_keys=True).encode("utf-8")
        )
        self.signature = sign(private_key, self._canonical_bytes()).hex()
        return self

    # -------- verification path --------
    def verify_with(self, sender_public_key, seen_nonces: set | None = None) -> tuple[bool, str]:
        """
        Validate signature, freshness, and nonce uniqueness.

        Returns (ok, reason). `reason` is a short string for logging
        when ok=False. `seen_nonces` is a mutable set that callers
        should keep across messages -- it holds nonces already
        accepted so we can reject replays.
        """
        # Reject future-dated messages (skew tolerance: 2 s)
        now = time.time()
        if self.timestamp > now + 2:
            return False, "timestamp in the future"
        if now - self.timestamp > FRESHNESS_WINDOW_SECONDS:
            return False, "message too old (replay candidate)"

        # Reject nonce reuse
        if seen_nonces is not None:
            if self.nonce in seen_nonces:
                return False, "nonce reuse (replay attack)"

        # Verify signature -- this covers tampering and impersonation
        try:
            sig_bytes = bytes.fromhex(self.signature)
        except ValueError:
            return False, "malformed signature"

        if not verify(sender_public_key, self._canonical_bytes(), sig_bytes):
            return False, "signature invalid (tampering or wrong sender)"

        # Recompute payload hash and compare
        expected = sha256_hex(
            json.dumps(self.payload, sort_keys=True).encode("utf-8")
        )
        if expected != self.sender_hash:
            return False, "payload hash mismatch"

        # All checks passed -- record nonce so it can't be reused
        if seen_nonces is not None:
            seen_nonces.add(self.nonce)
        return True, "ok"

    # -------- wire format --------
    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, data: str) -> "SecureMessage":
        return cls(**json.loads(data))


# ---------------------------------------------------------------------
# Convenience helper used by tests and the attack simulator
# ---------------------------------------------------------------------
def new_message(sender_id: str, receiver_id: str, payload: dict, private_key) -> SecureMessage:
    """Build + sign in one call."""
    msg = SecureMessage(sender_id=sender_id, receiver_id=receiver_id, payload=payload)
    msg.sign_with(private_key)
    return msg