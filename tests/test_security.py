"""
tests/test_security.py
----------------------
Verifies every security property claimed in the project description.

Run with:    pytest -v tests/test_security.py
"""

import time
import pytest

from security.crypto_utils import (
    sha256, sign, verify, generate_rsa_keypair,
)
from security.pki import CertificateAuthority, verify_certificate
from security.secure_message import SecureMessage, new_message
from security.emergency_auth import (
    EmergencyToken, EmergencyDispatchAuthority, validate_emergency_token,
)
from security.secure_agent import SecureAgent
from security.attack_simulator import run_all_attacks


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def ca():
    return CertificateAuthority()


@pytest.fixture
def agent_keys():
    priv, pub = generate_rsa_keypair()
    return priv, pub


@pytest.fixture
def eda():
    priv, pub = generate_rsa_keypair()
    return EmergencyDispatchAuthority(priv, pub)


# ---------------------------------------------------------------------
# 1. CRYPTO PRIMITIVES
# ---------------------------------------------------------------------
class TestCryptoPrimitives:
    def test_sha256_is_deterministic(self):
        assert sha256(b"hello") == sha256(b"hello")

    def test_sha256_avalanche(self):
        a = sha256(b"hello")
        b = sha256(b"Hello")
        assert a != b

    def test_sign_and_verify_roundtrip(self, agent_keys):
        priv, pub = agent_keys
        sig = sign(priv, b"control frame")
        assert verify(pub, b"control frame", sig)

    def test_verify_rejects_wrong_key(self, agent_keys):
        priv, _ = agent_keys
        _, wrong_pub = generate_rsa_keypair()
        sig = sign(priv, b"x")
        assert not verify(wrong_pub, b"x", sig)

    def test_verify_rejects_altered_message(self, agent_keys):
        priv, pub = agent_keys
        sig = sign(priv, b"original")
        assert not verify(pub, b"tampered", sig)


# ---------------------------------------------------------------------
# 2. PKI
# ---------------------------------------------------------------------
class TestPKI:
    def test_ca_signed_cert_verifies(self, ca, agent_keys):
        _, pub = agent_keys
        cert = ca.issue_certificate("J1", pub)
        assert verify_certificate(cert, ca.certificate)

    def test_cert_from_other_ca_fails(self, ca, agent_keys):
        _, pub = agent_keys
        other_ca = CertificateAuthority("Rogue-CA")
        cert = other_ca.issue_certificate("J1", pub)
        assert not verify_certificate(cert, ca.certificate)


# ---------------------------------------------------------------------
# 3. SECURE MESSAGE (signing + replay + MITM)
# ---------------------------------------------------------------------
class TestSecureMessage:
    def test_roundtrip_accepts(self, agent_keys):
        priv, pub = agent_keys
        msg = new_message("A", "B", {"phase": 1}, priv)
        ok, _ = msg.verify_with(pub, seen_nonces=set())
        assert ok

    def test_tampering_is_detected(self, agent_keys):
        priv, pub = agent_keys
        msg = new_message("A", "B", {"phase": 1}, priv)
        msg.payload["phase"] = 99
        ok, reason = msg.verify_with(pub, seen_nonces=set())
        assert not ok
        assert "signature" in reason.lower()

    def test_mitm_receiver_change_is_detected(self, agent_keys):
        priv, pub = agent_keys
        msg = new_message("A", "B", {"phase": 1}, priv)
        msg.receiver_id = "C"
        ok, _ = msg.verify_with(pub, seen_nonces=set())
        assert not ok

    def test_replay_is_rejected(self, agent_keys):
        priv, pub = agent_keys
        msg = new_message("A", "B", {"phase": 1}, priv)
        nonces = set()
        ok1, _ = msg.verify_with(pub, nonces)
        ok2, reason = msg.verify_with(pub, nonces)
        assert ok1 and not ok2
        assert "replay" in reason.lower() or "nonce" in reason.lower()

    def test_stale_message_is_rejected(self, agent_keys):
        priv, pub = agent_keys
        msg = new_message("A", "B", {"phase": 1}, priv)
        msg.timestamp = time.time() - 3600
        msg.sign_with(priv)
        ok, reason = msg.verify_with(pub, set())
        assert not ok
        assert "old" in reason.lower() or "replay" in reason.lower()


# ---------------------------------------------------------------------
# 4. EMERGENCY VEHICLE AUTHENTICATION
# ---------------------------------------------------------------------
class TestEmergencyAuth:
    def test_valid_token_passes(self, eda):
        token = eda.issue("ambulance_7", "AMBULANCE")
        ok, _ = validate_emergency_token(token, eda.public_key, "ambulance_7")
        assert ok

    def test_forged_token_is_rejected(self, eda):
        fake_priv, _ = generate_rsa_keypair()
        token = EmergencyToken(
            vehicle_id="attacker_car",
            dispatched_at=time.time(),
            expires_at=time.time() + 300,
            reason_code="AMBULANCE",
        )
        token.sign_with(fake_priv)
        ok, reason = validate_emergency_token(token, eda.public_key, "attacker_car")
        assert not ok
        assert "signature" in reason.lower() or "forged" in reason.lower()

    def test_expired_token_is_rejected(self, eda):
        token = eda.issue("ambulance_7", "AMBULANCE", validity_seconds=1)
        time.sleep(2)
        ok, reason = validate_emergency_token(token, eda.public_key, "ambulance_7")
        assert not ok
        assert "expired" in reason.lower()

    def test_token_reassignment_is_rejected(self, eda):
        """Attacker steals a legitimate token and tries to use it on their car."""
        token = eda.issue("ambulance_7", "AMBULANCE")
        ok, reason = validate_emergency_token(token, eda.public_key, "attacker_car")
        assert not ok
        assert "mismatch" in reason.lower() or "theft" in reason.lower()


# ---------------------------------------------------------------------
# 5. END-TO-END: SecureAgent + attack simulator
# ---------------------------------------------------------------------
class TestSecureAgentE2E:
    def _build_agent(self, ca, eda):
        priv, pub = generate_rsa_keypair()
        cert = ca.issue_certificate("J1", pub)
        return SecureAgent(
            base_agent=None,
            agent_id="J1",
            private_key=priv,
            certificate=cert,
            ca_cert=ca.certificate,
            peer_public_keys={"J1": pub},
            eda_public_key=eda.public_key,
        ), priv, pub

    def test_all_attacks_are_blocked(self, ca, eda):
        agent, priv, pub = self._build_agent(ca, eda)
        agent.peer_public_keys["agent_A"] = pub
        results = run_all_attacks(agent, priv, pub)
        for name, blocked, detail in results:
            assert blocked, f"ATTACK NOT BLOCKED: {name} -- {detail}"