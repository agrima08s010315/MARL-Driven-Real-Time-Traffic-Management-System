"""
attack_simulator.py
-------------------
Simulates adversarial behavior to demonstrate that the security layer
actually blocks the attacks claimed in the project.

This is the module reviewers and patent examiners will look at first
to verify the security claims are not just architectural hand-waving.

Attacks implemented:
    1. TAMPERING            -- flip bits in a signed message mid-flight
    2. IMPERSONATION        -- attacker signs with their own key and
                               claims to be a legitimate agent
    3. REPLAY               -- resend a captured valid message
    4. MITM REDIRECTION     -- change receiver_id of a valid message
    5. EMERGENCY SPOOFING   -- claim emergency status without a token
    6. FORGED TOKEN         -- present a fake EDA-signed token

Each scenario is expressed as a self-contained function that returns
True iff the attack was correctly BLOCKED by the defenses.
"""

from __future__ import annotations

from .crypto_utils import generate_rsa_keypair, sign
from .secure_message import SecureMessage, new_message
from .emergency_auth import EmergencyToken


# ---------------------------------------------------------------------
# Attack 1: Payload tampering (bit flip in transit)
# ---------------------------------------------------------------------
def attempt_tampering(honest_private_key, honest_public_key) -> tuple[bool, str]:
    msg = new_message("agent_A", "agent_B", {"phase": 2, "ttl": 30}, honest_private_key)

    # Attacker intercepts and alters the payload without re-signing
    msg.payload["phase"] = 99  # malicious phase change

    ok, reason = msg.verify_with(honest_public_key, seen_nonces=set())
    blocked = not ok
    return blocked, f"tampering: blocked={blocked} (reason={reason})"


# ---------------------------------------------------------------------
# Attack 2: Impersonation (attacker uses their own key)
# ---------------------------------------------------------------------
def attempt_impersonation(honest_public_key) -> tuple[bool, str]:
    # Attacker generates their own keypair and signs a message
    # claiming to be agent_A
    attacker_private, _ = generate_rsa_keypair()
    forged = new_message("agent_A", "agent_B", {"phase": 0}, attacker_private)

    # Receiver checks signature against the REAL agent_A public key
    ok, reason = forged.verify_with(honest_public_key, seen_nonces=set())
    blocked = not ok
    return blocked, f"impersonation: blocked={blocked} (reason={reason})"


# ---------------------------------------------------------------------
# Attack 3: Replay (capture + resend)
# ---------------------------------------------------------------------
def attempt_replay(honest_private_key, honest_public_key) -> tuple[bool, str]:
    msg = new_message("agent_A", "agent_B", {"phase": 1}, honest_private_key)

    nonce_log: set[str] = set()

    # First delivery is legitimate
    ok1, _ = msg.verify_with(honest_public_key, nonce_log)

    # Attacker captures and resends the EXACT same bytes
    ok2, reason = msg.verify_with(honest_public_key, nonce_log)

    blocked = ok1 and (not ok2)
    return blocked, f"replay: first={ok1}, second_blocked={not ok2} (reason={reason})"


# ---------------------------------------------------------------------
# Attack 4: MITM redirection (change receiver)
# ---------------------------------------------------------------------
def attempt_mitm_redirection(honest_private_key, honest_public_key) -> tuple[bool, str]:
    msg = new_message("agent_A", "agent_B", {"phase": 1}, honest_private_key)

    # Attacker in the middle wants to deliver the signed command to
    # agent_C instead. They modify receiver_id.
    msg.receiver_id = "agent_C"

    ok, reason = msg.verify_with(honest_public_key, seen_nonces=set())
    blocked = not ok
    return blocked, f"mitm_redirect: blocked={blocked} (reason={reason})"


# ---------------------------------------------------------------------
# Attack 5: Emergency spoofing (no token at all)
# ---------------------------------------------------------------------
def attempt_emergency_spoofing(secure_agent) -> tuple[bool, str]:
    """
    A malicious vehicle sets its SUMO type to "emergency" but has no
    EDA-signed token. The secure agent should report no authenticated
    emergency present.
    """
    vehicle_ids_on_lane = ["attacker_car_42"]
    granted = secure_agent.authenticated_emergency_present(vehicle_ids_on_lane)
    blocked = not granted
    return blocked, f"emergency_spoofing: blocked={blocked}"


# ---------------------------------------------------------------------
# Attack 6: Forged emergency token (self-signed)
# ---------------------------------------------------------------------
def attempt_forged_token(secure_agent) -> tuple[bool, str]:
    """
    Attacker generates their own keypair and signs their own token.
    Validation fails because the signature doesn't match the real
    EDA public key the agent trusts.
    """
    fake_priv, _ = generate_rsa_keypair()
    forged = EmergencyToken(
        vehicle_id="attacker_car_42",
        dispatched_at=0.0,
        expires_at=9e9,
        reason_code="AMBULANCE",
    )
    forged.sign_with(fake_priv)

    ok, reason = secure_agent.register_emergency_token(forged)
    blocked = not ok
    return blocked, f"forged_token: blocked={blocked} (reason={reason})"


# ---------------------------------------------------------------------
# Full demo runner
# ---------------------------------------------------------------------
def run_all_attacks(secure_agent, honest_private_key, honest_public_key):
    """
    Run every attack and return a summary list.

    Each entry is (attack_name, blocked_bool, detail_str).
    """
    results = []

    blocked, detail = attempt_tampering(honest_private_key, honest_public_key)
    results.append(("Tampering", blocked, detail))

    blocked, detail = attempt_impersonation(honest_public_key)
    results.append(("Impersonation", blocked, detail))

    blocked, detail = attempt_replay(honest_private_key, honest_public_key)
    results.append(("Replay", blocked, detail))

    blocked, detail = attempt_mitm_redirection(honest_private_key, honest_public_key)
    results.append(("MITM redirection", blocked, detail))

    blocked, detail = attempt_emergency_spoofing(secure_agent)
    results.append(("Emergency spoofing", blocked, detail))

    blocked, detail = attempt_forged_token(secure_agent)
    results.append(("Forged emergency token", blocked, detail))

    return results