# Security Architecture

This document describes the cybersecurity layer that protects the
MARL-driven traffic management system against network-layer and
application-layer attacks. It is written to serve as both implementation
reference and patent/report supporting documentation.

## 1. Threat Model (STRIDE)

The system operates in an open environment where traffic controllers
communicate over potentially untrusted networks. We apply the STRIDE
taxonomy to enumerate threats.

| STRIDE category | Scenario | Mitigation in this system |
|---|---|---|
| **S**poofing identity | Attacker claims to be Intersection-B and sends false congestion data | X.509 certificates signed by the TrafficNet CA; receiver verifies sender cert |
| **T**ampering with data | Attacker flips bits in a signal-phase command mid-flight | RSA-PSS signature over the full message + SHA-256 payload digest |
| **R**epudiation | Agent denies having sent a command after an incident | All messages are signed; log persists sender_id + signature |
| **I**nformation disclosure | Attacker eavesdrops congestion patterns to plan attacks | TLS 1.3 encryption of the transport channel (AES-256-GCM) |
| **D**enial of service | Flood of forged emergency-priority requests | Cryptographic emergency tokens; unauthenticated requests are dropped |
| **E**levation of privilege | Regular vehicle gains emergency priority | EDA-signed tokens bound to specific `vehicle_id` + validity window |

## 2. Defense-in-Depth Layers

```
+------------------------------------------------------------------+
|  Layer 4: Application-level signing  (secure_message.py)          |
|           RSA-PSS + SHA-256 + nonce + timestamp                  |
+------------------------------------------------------------------+
|  Layer 3: Peer authentication         (pki.py)                    |
|           X.509 mutual certificates issued by a trust anchor     |
+------------------------------------------------------------------+
|  Layer 2: Transport security          (secure_channel.py)         |
|           TLS 1.3 with AES-256-GCM and ephemeral key exchange    |
+------------------------------------------------------------------+
|  Layer 1: Cryptographic primitives    (crypto_utils.py)           |
|           OpenSSL-backed RSA-2048, SHA-256, PSS padding          |
+------------------------------------------------------------------+
```

Each layer is independent — compromise of any single layer still
leaves the others enforcing security properties.

## 3. Message Format

Every inter-agent message is a JSON envelope:

```
{
  "sender_id":   "J1",
  "receiver_id": "J2",
  "payload":     {"phase": 2, "green_duration": 30, ...},
  "timestamp":   1735947200.123,
  "nonce":       "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "sender_hash": "3a7bd...c12f",      // SHA-256 of payload
  "signature":   "4c8ef...91a2"       // RSA-PSS over the envelope
}
```

Verification steps performed by the receiver, in order:

1. `receiver_id` matches the local agent ID (drops misrouted / MITM-redirected messages)
2. `sender_id` is in the peer public-key registry (drops unknown senders)
3. `now - timestamp < FRESHNESS_WINDOW_SECONDS` (drops stale messages)
4. `nonce` not seen before (drops replays)
5. `signature` validates against `sender`'s public key over the canonical byte form
6. `sender_hash` equals SHA-256 of the payload (cross-check)

Any failure → message dropped, event logged, counter incremented.

## 4. Emergency Vehicle Authentication

Emergency priority is a high-value privilege and a common abuse target.
We require a signed token issued by the Emergency Dispatch Authority
(EDA) before granting priority:

```
EmergencyToken {
  vehicle_id:     "ambulance_7",
  dispatched_at:  1735947000,
  expires_at:     1735947600,
  reason_code:    "AMBULANCE",
  signature:      <EDA RSA-PSS signature>
}
```

Validation rules:

* `vehicle_id` on the token must match the vehicle presenting it
  (prevents token theft / replay on a different vehicle)
* current time must fall between `dispatched_at` and `expires_at`
* signature must verify under the EDA's public key baked into every
  agent at bootstrap

## 5. Key Management

| Key | Owner | Lifetime | Storage |
|---|---|---|---|
| CA root private key | Traffic authority | 10 years | Offline (HSM in production; `keys/ca_key.pem` with 0600 in sim) |
| Agent private key | Individual intersection | 1 year | On the intersection controller only |
| Agent certificate | — | 1 year | Freely shared, CA-signed |
| EDA private key | Emergency dispatch | 1 year | Dispatch center only |
| EDA public key | Every agent | 1 year | Baked in at bootstrap |

Nothing under `keys/` is committed to git — see `.gitignore`.

## 6. Attack Coverage Matrix

Maps each claimed defense to the test that validates it.

| Attack | Primary defense | Test |
|---|---|---|
| Payload tampering | RSA-PSS signature | `test_tampering_is_detected` |
| Agent impersonation | Cert + signature verification | `test_impersonation`, `test_cert_from_other_ca_fails` |
| Replay attack | Nonce log + timestamp window | `test_replay_is_rejected`, `test_stale_message_is_rejected` |
| MITM eavesdropping | TLS 1.3 encryption | TLS smoke test (cipher = AES-256-GCM) |
| MITM redirection | `receiver_id` inside signature | `test_mitm_receiver_change_is_detected` |
| Emergency spoofing | Token required | `attempt_emergency_spoofing` |
| Forged emergency token | EDA signature check | `test_forged_token_is_rejected` |
| Token theft | `vehicle_id` binding | `test_token_reassignment_is_rejected` |
| Expired token | Timestamp check | `test_expired_token_is_rejected` |

## 7. Performance

RSA-2048-PSS sign on a 200-byte message: ~1 ms on modern hardware.
Verify: ~0.1 ms. Traffic control updates at 1 Hz, so cryptographic
overhead is three orders of magnitude under budget.

If future deployment scales to millisecond-level control, the design
supports swapping RSA for Ed25519 (drop-in replacement in
`crypto_utils.py`).

## 8. What This Design Does NOT Cover

Being explicit about limits is important for an honest research
artifact:

* **Compromised endpoints**. If an attacker gains root on a
  controller, they possess its private key and become indistinguishable
  from the legitimate agent. Hardware attestation is out of scope.
* **Side channels**. Timing / power analysis of the RSA implementation
  on an embedded controller would require constant-time hardware.
* **Long-term quantum resilience**. RSA-2048 is not post-quantum.
  Migration to Dilithium / Kyber is tracked as future work.