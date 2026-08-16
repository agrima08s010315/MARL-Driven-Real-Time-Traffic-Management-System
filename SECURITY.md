<div align="center">

# 🔐 Security Architecture

### Secure Communication for Multi-Agent Traffic Intelligence

**TLS 1.3 · mTLS · X.509 PKI · RSA-PSS · SHA-256 · Replay Protection · Emergency Authorization**

</div>

---

## Overview

This document describes the security architecture protecting the **MARL-Driven Real-Time Traffic Management System**.

The system models traffic intersections as distributed software agents that may exchange control or coordination messages over an untrusted network.

The security layer is designed to protect:

* **agent identity**
* **transport confidentiality**
* **message integrity**
* **message authenticity**
* **replay resistance**
* **receiver binding**
* **emergency-priority authorization**

The implementation lives primarily inside the [`security/`](./security/) package and is validated through automated tests and adversarial simulations.

> A correct traffic-control policy is not sufficient if an attacker can manipulate the inputs, messages, or commands exchanged between agents.

---

## 🛡️ Security Goals

The architecture is built around six core guarantees.

| Goal                           | Security Property                                                |
| ------------------------------ | ---------------------------------------------------------------- |
| **Authenticated agents**       | Only identities trusted by the traffic authority can participate |
| **Confidential communication** | Inter-agent traffic is encrypted while in transit                |
| **Message integrity**          | Modified commands are rejected                                   |
| **Message authenticity**       | Messages can be verified against the sender identity             |
| **Replay resistance**          | Previously valid messages cannot be reused indefinitely          |
| **Controlled privilege**       | Emergency priority requires separate cryptographic authorization |

---

# 🧭 Threat Model

The project uses the **STRIDE** framework to reason about likely threats in a distributed intelligent-transportation environment.

| STRIDE Category            | Example Attack                                               | Implemented Mitigation                             |
| -------------------------- | ------------------------------------------------------------ | -------------------------------------------------- |
| **Spoofing**               | Malicious node impersonates intersection `J2`                | X.509 identity, trusted CA, signature verification |
| **Tampering**              | Attacker modifies a signal-phase command                     | RSA-PSS signature + SHA-256 integrity validation   |
| **Repudiation**            | Agent disputes issuing a message                             | Signed message envelope containing sender metadata |
| **Information Disclosure** | Network observer captures controller communication           | TLS 1.3 encrypted transport                        |
| **Denial of Service**      | Forged emergency requests attempt to abuse priority handling | Authentication + authorization validation          |
| **Elevation of Privilege** | Normal vehicle claims emergency status                       | Dispatch-authority signed emergency token          |

### Important Boundary

Authentication can reject unauthorized messages, but it does **not** by itself prevent large-scale volumetric denial-of-service attacks. Network-level DoS mitigation is outside the scope of this simulation.

---

# 🏗️ Defense-in-Depth Design

```text
┌──────────────────────────────────────────────────────────────┐
│                    APPLICATION SECURITY                      │
│             Emergency Vehicle Authorization                  │
├──────────────────────────────────────────────────────────────┤
│                      MESSAGE SECURITY                        │
│      RSA-PSS • SHA-256 • Nonce • Timestamp • Receiver       │
├──────────────────────────────────────────────────────────────┤
│                      IDENTITY SECURITY                       │
│          X.509 PKI • Per-Agent Certificates • CA            │
├──────────────────────────────────────────────────────────────┤
│                     TRANSPORT SECURITY                       │
│                       TLS 1.3 + mTLS                         │
├──────────────────────────────────────────────────────────────┤
│                  CRYPTOGRAPHIC PRIMITIVES                    │
│                 RSA-2048 • SHA-256 • PSS                    │
└──────────────────────────────────────────────────────────────┘
```

Each layer protects a different part of the communication path.

For example:

* **TLS 1.3** protects data while it travels between peers.
* **mTLS** authenticates both communicating endpoints.
* **X.509 certificates** establish agent identity.
* **RSA-PSS signatures** provide application-level message authenticity and integrity.
* **nonces and timestamps** reduce replay risk.
* **receiver binding** helps detect message redirection.
* **emergency tokens** separate privileged priority requests from ordinary traffic metadata.

---

# 🧩 Security Components

| Module                | Responsibility                                                                 |
| --------------------- | ------------------------------------------------------------------------------ |
| `crypto_utils.py`     | RSA-2048 keys, SHA-256 hashing, RSA-PSS signing and verification               |
| `pki.py`              | Certificate authority and per-agent X.509 certificates                         |
| `secure_message.py`   | Signed envelopes with sender, receiver, timestamp, nonce, and payload metadata |
| `secure_channel.py`   | TLS 1.3 mutual-authentication transport                                        |
| `emergency_auth.py`   | Emergency-vehicle authorization tokens                                         |
| `secure_agent.py`     | Integration layer between security controls and traffic agents                 |
| `attack_simulator.py` | Executable adversarial scenarios                                               |

---

# ✉️ Secure Message Protocol

Each protected inter-agent message is wrapped in a signed envelope.

Example:

```json
{
  "sender_id": "J1",
  "receiver_id": "J2",
  "payload": {
    "phase": 2,
    "green_duration": 30
  },
  "timestamp": 1735947200.123,
  "nonce": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "sender_hash": "3a7bd...c12f",
  "signature": "4c8ef...91a2"
}
```

## Validation Sequence

The receiving agent performs a deterministic validation sequence:

1. confirm that `receiver_id` matches the local agent;
2. verify that `sender_id` belongs to a trusted peer;
3. validate message freshness using the timestamp;
4. reject previously observed nonces;
5. verify the RSA-PSS signature using the sender public key;
6. recompute the SHA-256 payload digest;
7. accept the message only if all checks succeed.

```text
Incoming Message
       │
       ▼
Receiver Match?
   ├── No ──► Reject
   └── Yes
       │
       ▼
Trusted Sender?
   ├── No ──► Reject
   └── Yes
       │
       ▼
Fresh Timestamp?
   ├── No ──► Reject
   └── Yes
       │
       ▼
Nonce Reused?
   ├── Yes ─► Reject
   └── No
       │
       ▼
Signature Valid?
   ├── No ──► Reject
   └── Yes
       │
       ▼
Payload Integrity Valid?
   ├── No ──► Reject
   └── Yes ─► Accept
```

---

# 🚑 Emergency Vehicle Authorization

Emergency priority is treated as a **privileged operation**, not ordinary message metadata.

A requesting vehicle must present a signed authorization token issued by the simulated Emergency Dispatch Authority.

```text
EmergencyToken
├── vehicle_id
├── dispatched_at
├── expires_at
├── reason_code
└── signature
```

Example:

```json
{
  "vehicle_id": "ambulance_7",
  "dispatched_at": 1735947000,
  "expires_at": 1735947600,
  "reason_code": "AMBULANCE",
  "signature": "<EDA RSA-PSS signature>"
}
```

The receiving controller validates that:

* the token `vehicle_id` matches the requesting vehicle;
* the token is currently within its allowed validity period;
* the signature verifies against the trusted dispatch-authority public key;
* the token has not been modified;
* expired or invalid authorization is rejected.

This prevents a standard vehicle from obtaining signal priority merely by setting:

```json
{
  "emergency": true
}
```

---

# 🪪 PKI & Agent Identity

Each traffic-control agent receives a unique X.509 identity.

```text
                 Traffic Authority CA
                        │
             ┌──────────┼──────────┐
             │          │          │
             ▼          ▼          ▼
           J1 Cert    J2 Cert    J3 Cert
                                     │
                                     ▼
                                   J4 Cert
```

The traffic authority certificate acts as the **trust anchor** for the simulated controller network.

Agents validate peer certificates before accepting protected communication.

---

# 🔑 Key Management

| Credential                      | Owner              | Simulation Lifetime | Storage                         |
| ------------------------------- | ------------------ | ------------------: | ------------------------------- |
| CA private key                  | Traffic authority  |            10 years | `keys/ca_key.pem`               |
| Agent private key               | Intersection agent |              1 year | Local controller storage        |
| Agent certificate               | Traffic agent      |              1 year | Shareable CA-signed certificate |
| Emergency authority private key | Dispatch authority |              1 year | Dispatch environment            |
| Emergency authority public key  | Traffic agents     |              1 year | Provisioned during bootstrap    |

Private-key material under `keys/` should remain excluded from version control.

> **Production note:** A real deployment should use managed secrets, hardware security modules, TPM-backed storage, secure enclaves, or another hardware-backed key-management approach rather than filesystem-based private keys.

---

# ⚔️ Adversarial Validation

The security architecture is validated through executable tests rather than documentation claims alone.

## Attack Coverage

| Attack                        | Defensive Control               | Validation                              |
| ----------------------------- | ------------------------------- | --------------------------------------- |
| Payload tampering             | RSA-PSS signature               | `test_tampering_is_detected`            |
| Agent impersonation           | Trusted certificate + signature | `test_impersonation`                    |
| Certificate from untrusted CA | CA trust validation             | `test_cert_from_other_ca_fails`         |
| Replay attack                 | Nonce cache                     | `test_replay_is_rejected`               |
| Stale message                 | Timestamp freshness window      | `test_stale_message_is_rejected`        |
| MITM receiver redirection     | Signed receiver identity        | `test_mitm_receiver_change_is_detected` |
| Emergency spoofing            | Signed authorization token      | `attempt_emergency_spoofing`            |
| Forged token                  | Dispatch-authority signature    | `test_forged_token_is_rejected`         |
| Token reassignment            | Vehicle-ID binding              | `test_token_reassignment_is_rejected`   |
| Expired token                 | Authorization validity window   | `test_expired_token_is_rejected`        |

---

## 🧪 Automated Security Tests

Run:

```bash
python -m pytest -v tests/test_security.py
```

The current suite contains **17 security-focused tests** covering areas including:

* identity validation
* message-integrity checks
* signature validation
* replay prevention
* certificate trust
* emergency authorization
* stale-message handling
* receiver binding
* adversarial message processing

---

## ⚔️ Attack Simulation

Run:

```bash
python demo.py
```

The adversarial simulation exercises six attack classes:

```text
1. Message Tampering
2. Agent Impersonation
3. Replay
4. MITM Redirection
5. Emergency Spoofing
6. Forged Authorization Token
```

Each scenario is expected to be rejected by the appropriate defensive layer.

---

# 🔒 TLS Verification

Transport security can be tested independently with:

```bash
python tls_smoke_test.py
```

This smoke test exercises mutual authentication between simulated traffic-system participants using the configured TLS stack.

It provides a separate validation path from the application-level signed-message tests.

---

# 🧠 Security Boundary Around the AI Layer

The security architecture is intentionally separated from the adaptive traffic-control policy.

```text
External Observation / Peer Message
                │
                ▼
        Security Validation
                │
                ▼
           Trusted Input
                │
                ▼
     Adaptive / MARL Controller
                │
                ▼
          Signal Decision
                │
                ▼
   Sign + Authenticate Command
                │
                ▼
        Protected Transmission
```

This separation helps prevent the decision layer from treating unvalidated external messages as trusted state.

From an AI-systems perspective, the security layer protects both:

**Model inputs**
Incoming observations and peer messages are validated before use.

**Model outputs**
Outbound control commands are signed and authenticated before transmission.

This distinction is important because **model quality does not guarantee system integrity** in a distributed environment.

---

# 📊 Cryptographic Performance Considerations

Security operations introduce computational overhead.

The current implementation uses **RSA-2048 with RSA-PSS signatures**.

For the simulated traffic-control update frequency, this cost is acceptable for demonstration purposes. However, production performance should be measured on the target controller hardware rather than assumed.

Cryptographic primitives are isolated within `crypto_utils.py`, allowing them to be replaced without rewriting the traffic-control logic.

Potential future alternatives include:

* Ed25519 signatures
* hardware-backed signing
* asynchronous verification
* session-level message authentication
* dedicated cryptographic accelerators

> Any latency or throughput claim for cryptographic operations should be benchmarked on representative deployment hardware.

---

# 🧪 Security Engineering Principles

## Zero Implicit Trust

Messages are not considered trusted simply because they appear to originate from another traffic controller.

## Defense in Depth

Transport encryption, peer authentication, signed messages, replay checks, and privileged authorization operate as separate controls.

## Explicit Authorization

Emergency priority requires cryptographic authorization rather than boolean metadata.

## Replay Resistance

Nonces and timestamp validation reduce the risk of reusing previously accepted commands.

## Separation of Concerns

Security primitives remain separate from traffic-control and adaptive-decision logic.

## Testable Security Properties

Major defensive claims are mapped to automated tests or executable adversarial scenarios.

## Fail Closed

A protected message that fails validation should be rejected rather than accepted with reduced confidence.

---

# ⚠️ Security Boundaries & Limitations

This project is a **research and simulation artifact**, not a certified production Intelligent Transportation System security implementation.

The architecture intentionally does not claim to solve every attack class.

### Compromised Legitimate Controller

If an attacker compromises an authorized intersection and gains access to its private key, the attacker may be able to authenticate as that legitimate controller.

Possible future mitigations include:

* hardware-backed keys
* remote attestation
* secure enclaves
* behavioural anomaly detection

### Volumetric Denial of Service

Application authentication can reject malicious requests but cannot stop an attacker from consuming network capacity before the application receives them.

Network-level DDoS mitigation is outside the current scope.

### Side-Channel Attacks

Hardware timing, power analysis, electromagnetic leakage, and other side-channel attacks are not modelled.

### Certificate Revocation

The simulation uses CA-backed certificate trust but does not implement a complete production revocation infrastructure such as CRLs or OCSP.

### Endpoint Hardening

Operating-system hardening, secure boot, firmware integrity, patch management, and physical controller security are outside the current implementation.

### Post-Quantum Security

RSA-2048 is not post-quantum secure.

Future deployment could evaluate post-quantum signature and key-establishment mechanisms when practical requirements are better defined.

---

# 🚀 Future Security Work

Potential extensions include:

* certificate rotation and revocation
* hardware-backed private keys
* controller attestation
* rate limiting
* distributed DoS mitigation
* structured security-event telemetry
* traffic-agent intrusion detection
* Byzantine-agent detection
* secure federated learning
* model-poisoning detection
* anomaly detection for controller behaviour
* SIEM integration
* certificate transparency for traffic agents
* post-quantum cryptographic migration

---

# 📁 Security-Relevant Files

```text
security/
├── crypto_utils.py
├── pki.py
├── secure_message.py
├── secure_channel.py
├── emergency_auth.py
├── secure_agent.py
└── attack_simulator.py

tests/
└── test_security.py

generate_keys.py
demo.py
tls_smoke_test.py
SECURITY.md
```

---

# ✅ Security Summary

The traffic-management system combines adaptive multi-agent decision making with a separately enforced security boundary.

The implemented security layer provides:

* 🔒 encrypted inter-agent transport
* 🪪 X.509-based agent identities
* ✍️ cryptographically signed traffic-control messages
* 🔐 message-integrity verification
* ⏱️ timestamp and nonce-based replay protection
* 🚑 authenticated emergency-vehicle authorization
* ⚔️ executable adversarial attack simulations
* 🧪 automated security validation

The broader goal is not simply to demonstrate an adaptive traffic controller.

It is to explore how **distributed intelligent agents can exchange observations and actions through communication channels that are authenticated, validated, and explicitly trusted before influencing system behaviour**.

---

<div align="center">

### 🔗 Related Documentation

[![Main README](https://img.shields.io/badge/Project-Main%20README-181717?style=flat-square\&logo=github\&logoColor=white)](./README.md)
[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square\&logo=github\&logoColor=white)](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System)
[![Patent](https://img.shields.io/badge/View-Patent%20Document-4285F4?style=flat-square\&logo=googledrive\&logoColor=white)](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)

</div>
