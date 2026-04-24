"""
secure_agent.py
---------------
Integration layer -- wraps the existing TrafficSignalAgent with the
security primitives defined in this package.

Design principle: minimal surface change.
    The original agent code in marl_agent.py is untouched. SecureAgent
    COMPOSES a TrafficSignalAgent and adds:
        - cryptographic identity (private key + CA-signed cert)
        - signed message exchange with peer agents
        - emergency token validation before granting priority
        - an in-memory replay-nonce log

This keeps the MARL research code clean and the security layer
inspectable in one place.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .secure_message import SecureMessage, new_message
from .emergency_auth import validate_emergency_token, EmergencyToken

if TYPE_CHECKING:
    # Only imported for type hints -- keeps the security package
    # independently importable even when traci is not installed
    # (useful during testing).
    pass


class SecureAgent:
    """
    Wraps a TrafficSignalAgent with authenticated communication and
    emergency-priority validation.

    Usage:
        base = TrafficSignalAgent("J1")
        sec  = SecureAgent(base, agent_id="J1",
                           private_key=my_key, certificate=my_cert,
                           ca_cert=ca_cert, peer_keys=peer_pub_keys,
                           eda_public_key=eda_pub)
        sec.step()   # safe replacement for the original loop body
    """

    def __init__(
        self,
        base_agent,
        agent_id: str,
        private_key,
        certificate,
        ca_cert,
        peer_public_keys: dict[str, object],
        eda_public_key,
    ):
        self.base = base_agent
        self.agent_id = agent_id
        self.private_key = private_key
        self.certificate = certificate
        self.ca_cert = ca_cert
        # Map of peer agent_id -> their public key. Populated at
        # startup by the PKI bootstrap.
        self.peer_public_keys = peer_public_keys
        self.eda_public_key = eda_public_key

        # Nonces we've already accepted. In a real system this would
        # be bounded (LRU) to avoid unbounded growth; for simulation
        # a plain set is fine.
        self._seen_nonces: set[str] = set()

        # Trusted emergency tokens observed this tick. Populated by
        # register_emergency_token() before step() is called.
        self._valid_emergency_tokens: dict[str, EmergencyToken] = {}

    # ------------------------------------------------------------------
    # Secure peer messaging
    # ------------------------------------------------------------------
    def send_to(self, peer_id: str, payload: dict) -> SecureMessage:
        """
        Build a signed message addressed to `peer_id`.
        The transport (socket / in-memory queue) is the caller's job --
        this method just produces the envelope.
        """
        return new_message(
            sender_id=self.agent_id,
            receiver_id=peer_id,
            payload=payload,
            private_key=self.private_key,
        )

    def receive(self, msg: SecureMessage) -> tuple[bool, str, dict | None]:
        """
        Validate an incoming signed message. Returns (accepted, reason, payload).

        Drops the message silently (accepted=False) if:
          - sender is unknown (no public key on file)
          - receiver_id doesn't match us (misdirected or MITM rerouting)
          - signature invalid, stale, or nonce reused
        """
        if msg.receiver_id != self.agent_id:
            return False, f"not addressed to us (for {msg.receiver_id})", None

        sender_key = self.peer_public_keys.get(msg.sender_id)
        if sender_key is None:
            return False, f"unknown sender {msg.sender_id}", None

        ok, reason = msg.verify_with(sender_key, self._seen_nonces)
        if not ok:
            return False, reason, None
        return True, "ok", msg.payload

    # ------------------------------------------------------------------
    # Emergency vehicle authentication
    # ------------------------------------------------------------------
    def register_emergency_token(self, token: EmergencyToken) -> tuple[bool, str]:
        """
        Called when a vehicle approaches claiming emergency status.
        Only tokens that validate are stored; the simulation step
        method consults this store when deciding whether to grant
        priority.
        """
        ok, reason = validate_emergency_token(
            token, self.eda_public_key, expected_vehicle_id=token.vehicle_id
        )
        if ok:
            self._valid_emergency_tokens[token.vehicle_id] = token
        return ok, reason

    def clear_emergency_tokens(self):
        """Call at the start of each simulation tick."""
        self._valid_emergency_tokens.clear()

    def authenticated_emergency_present(self, vehicle_ids: list[str]) -> bool:
        """
        Replacement for the base agent's `emergency_present` check.
        Only returns True when at least one of the present vehicles
        has a currently-valid emergency token.
        """
        return any(vid in self._valid_emergency_tokens for vid in vehicle_ids)