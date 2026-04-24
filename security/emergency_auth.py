"""
emergency_auth.py
-----------------
Prevents emergency-priority abuse.

Problem:
    The base MARL agent gives signal priority whenever ANY vehicle of
    type "emergency" is present on an incoming lane. A malicious actor
    could set their own vehicle's type to "emergency" (via SUMO's API,
    or in a real city via a compromised vehicle firmware) and sail
    through every intersection.

Solution:
    Every legitimate emergency vehicle is issued a signed token at
    dispatch time by the Emergency Dispatch Authority (EDA). The token
    binds:
        - the vehicle's unique ID
        - a validity window (dispatched_at .. expires_at)
        - the dispatch reason code
    The agent only grants priority to emergency vehicles whose token
    validates against the EDA's public key.

In production this token would be broadcast over the V2X radio. In our
simulation we store it in the vehicle's parameters via traci, but the
cryptographic validation logic is identical.
"""

import json
import time
from dataclasses import dataclass, asdict

from .crypto_utils import sign, verify, sha256_hex


@dataclass
class EmergencyToken:
    vehicle_id: str
    dispatched_at: float
    expires_at: float
    reason_code: str        # e.g. "AMBULANCE", "FIRE", "POLICE"
    signature: str = ""     # hex-encoded RSA-PSS signature

    def _canonical_bytes(self) -> bytes:
        body = {
            "vehicle_id": self.vehicle_id,
            "dispatched_at": self.dispatched_at,
            "expires_at": self.expires_at,
            "reason_code": self.reason_code,
        }
        return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign_with(self, eda_private_key) -> "EmergencyToken":
        self.signature = sign(eda_private_key, self._canonical_bytes()).hex()
        return self

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, data: str) -> "EmergencyToken":
        return cls(**json.loads(data))


class EmergencyDispatchAuthority:
    """
    Single trusted authority that issues emergency tokens.
    In a real deployment there would be one EDA per metropolitan area.
    """

    def __init__(self, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key

    def issue(self, vehicle_id: str, reason_code: str, validity_seconds: int = 600) -> EmergencyToken:
        now = time.time()
        token = EmergencyToken(
            vehicle_id=vehicle_id,
            dispatched_at=now,
            expires_at=now + validity_seconds,
            reason_code=reason_code,
        )
        token.sign_with(self.private_key)
        return token


def validate_emergency_token(token: EmergencyToken, eda_public_key, expected_vehicle_id: str) -> tuple[bool, str]:
    """
    Validate an emergency token before granting priority.

    Rejects if:
      - signature doesn't match the EDA's public key
      - token is expired
      - token's vehicle_id differs from who's presenting it (prevents
        an attacker from reusing a legitimate ambulance's token on
        their own car)

    Returns (ok, reason).
    """
    if token.vehicle_id != expected_vehicle_id:
        return False, "token vehicle_id mismatch (possible theft)"

    now = time.time()
    if now > token.expires_at:
        return False, "token expired"
    if now < token.dispatched_at - 2:
        return False, "token not yet valid"

    try:
        sig_bytes = bytes.fromhex(token.signature)
    except ValueError:
        return False, "malformed signature"

    if not verify(eda_public_key, token._canonical_bytes(), sig_bytes):
        return False, "invalid EDA signature (forged token)"

    return True, "ok"