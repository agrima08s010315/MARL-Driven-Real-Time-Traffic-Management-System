# 🔐 Security Architecture

## Secure Communication for Multi-Agent Traffic Intelligence

This document describes the cybersecurity architecture protecting the MARL-driven traffic management system.

The system treats every traffic-signal controller as a distributed software agent operating over a potentially untrusted network. The security layer protects agent identity, message integrity, transport confidentiality, replay resistance, and emergency-priority authorization.

The design is implemented in the `security/` package and validated through automated tests and adversarial simulations.

---

## Security Goals

The architecture is designed around five core guarantees:

- **Authenticated agents** — only registered traffic controllers can participate
- **Confidential communication** — inter-agent traffic is encrypted in transit
- **Message integrity** — modified commands are rejected
- **Replay resistance** — stale or reused commands cannot be accepted repeatedly
- **Controlled privilege** — emergency priority requires cryptographic authorization

These controls protect the decision-making layer underneath the traffic optimization system. A correct MARL policy is not sufficient if an attacker can manipulate the observations or actions exchanged between agents.

---

# 🧭 Threat Model

CyberShield-style defense-in-depth principles are applied to the intelligent transportation environment using the **STRIDE threat-modeling framework**.

| STRIDE Category | Attack Scenario | Implemented Mitigation |
|---|---|---|
| **Spoofing** | Malicious node impersonates another intersection | X.509 identity + trusted CA + signature verification |
| **Tampering** | Signal command is modified during transmission | RSA-PSS signature + SHA-256 payload integrity |
| **Repudiation** | Agent denies issuing a control command | Signed messages with persistent sender metadata |
| **Information Disclosure** | Attacker observes traffic-control communication | TLS 1.3 encrypted transport |
| **Denial of Service** | Forged emergency-priority requests flood controllers | Authentication + cryptographically signed emergency tokens |
| **Elevation of Privilege** | Normal vehicle claims emergency priority | Dispatch-authority signed token bound to vehicle identity |

---

# 🏗️ Defense-in-Depth Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                  APPLICATION SECURITY                        │
│     Authenticated Emergency Vehicle Authorization            │
├──────────────────────────────────────────────────────────────┤
│                     MESSAGE SECURITY                         │
│   RSA-PSS • SHA-256 • Nonce • Timestamp • Receiver Binding  │
├──────────────────────────────────────────────────────────────┤
│                     IDENTITY SECURITY                        │
│       X.509 PKI • Per-Agent Certificates • Trusted CA       │
├──────────────────────────────────────────────────────────────┤
│                    TRANSPORT SECURITY                        │
│                    TLS 1.3 + mTLS                            │
├──────────────────────────────────────────────────────────────┤
│                  CRYPTOGRAPHIC PRIMITIVES                    │
│              RSA-2048 • SHA-256 • PSS                        │
└──────────────────────────────────────────────────────────────┘
```

Each layer protects a different failure mode.

For example, TLS protects confidentiality in transit, while RSA-PSS message signatures still provide application-level integrity if message handling occurs beyond the encrypted transport boundary.

---

# 🧩 Security Components

| Module | Responsibility |
|---|---|
| `crypto_utils.py` | RSA-2048 key generation, SHA-256 hashing, RSA-PSS signing and verification |
| `pki.py` | Self-managed certificate authority and per-agent X.509 certificates |
| `secure_message.py` | Signed message envelope with timestamp, nonce, sender and receiver binding |
| `secure_channel.py` | TLS 1.3 mutual-authentication channel |
| `emergency_auth.py` | Signed emergency-vehicle authorization tokens |
| `secure_agent.py` | Security wrapper around traffic-control agents |
| `attack_simulator.py` | Executable adversarial scenarios |

---

# ✉️ Secure Message Protocol

Every inter-agent message is wrapped in a signed envelope.

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

The receiver validates the message in a deterministic sequence:

1. verify that `receiver_id` matches the local agent;
2. confirm that `sender_id` belongs to a trusted peer;
3. reject messages outside the allowed freshness window;
4. reject previously observed nonces;
5. verify the RSA-PSS signature using the sender public key;
6. recompute and compare the SHA-256 payload digest.

A message is accepted only if all checks succeed.

```text
Incoming Message
       │
       ▼
Receiver Validation
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
Payload Hash Valid?
   ├── No ──► Reject
   └── Yes ─► Accept
```

---

# 🚑 Emergency Vehicle Authentication

Emergency priority is treated as a privileged operation rather than ordinary traffic metadata.

A priority request must include a signed token issued by the simulated Emergency Dispatch Authority.

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

Validation requires:

- token `vehicle_id` matches the requesting vehicle;
- current time falls inside the authorization window;
- signature verifies against the trusted dispatch public key;
- expired or modified tokens are rejected.

This prevents a normal vehicle from obtaining traffic-signal priority by simply setting an emergency flag.

---

# 🪪 PKI and Identity

Each traffic agent receives its own X.509 identity.

```text
Traffic Authority CA
        │
        ├──► Certificate: J1
        ├──► Certificate: J2
        ├──► Certificate: J3
        └──► Certificate: J4
```

The certificate authority acts as the trust anchor for the simulated traffic network.

Agents authenticate peers using certificates before accepting protected communication.

---

# 🔑 Key Management

| Key / Credential | Owner | Intended Lifetime | Simulation Storage |
|---|---|---:|---|
| CA private key | Traffic authority | 10 years | `keys/ca_key.pem` |
| Agent private key | Individual intersection | 1 year | Local controller only |
| Agent certificate | Traffic agent | 1 year | Shareable CA-signed certificate |
| Emergency authority private key | Dispatch authority | 1 year | Dispatch environment |
| Emergency authority public key | All agents | 1 year | Provisioned at bootstrap |

Private key material under `keys/` is excluded from version control.

> Production deployment would require hardware-backed key storage or managed key infrastructure rather than filesystem-based simulation keys.

---

# ⚔️ Adversarial Validation

The security layer is validated through executable tests rather than architecture claims alone.

## Attack Coverage

| Attack | Defense | Validation |
|---|---|---|
| Payload tampering | RSA-PSS signature | `test_tampering_is_detected` |
| Agent impersonation | Trusted certificate + signature | `test_impersonation` |
| Untrusted certificate | CA validation | `test_cert_from_other_ca_fails` |
| Replay attack | Nonce cache | `test_replay_is_rejected` |
| Stale message | Timestamp window | `test_stale_message_is_rejected` |
| MITM redirection | Signed receiver identity | `test_mitm_receiver_change_is_detected` |
| Emergency spoofing | Signed authorization token | `attempt_emergency_spoofing` |
| Forged token | Dispatch-authority signature | `test_forged_token_is_rejected` |
| Token theft | Vehicle-ID binding | `test_token_reassignment_is_rejected` |
| Expired token | Validity window | `test_expired_token_is_rejected` |

---

## Automated Security Tests

Run:

```bash
python -m pytest -v tests/test_security.py
```

The test suite contains **17 security-focused tests** covering:

- identity validation;
- message integrity;
- replay prevention;
- certificate trust;
- authorization-token verification; and
- adversarial message handling.

---

## Attack Simulation

Run:

```bash
python demo.py
```

The simulation exercises six adversarial attack classes:

```text
Tampering
Impersonation
Replay
MITM Redirection
Emergency Spoofing
Forged Authorization Token
```

Each scenario is expected to be rejected by the relevant defensive layer.

---

# 🔒 TLS Verification

Transport security can be validated independently using:

```bash
python tls_smoke_test.py
```

The smoke test exercises mutual authentication between simulated traffic agents using the configured TLS stack.

This provides a separate validation path from the application-level signed-message tests.

---

# 🧠 Security + AI Interaction

The security layer is intentionally separated from the MARL decision policy.

```text
Traffic Observation
       │
       ▼
Security Validation
       │
       ▼
Trusted Input
       │
       ▼
MARL Agent
       │
       ▼
Signal Decision
       │
       ▼
Signed + Authenticated Command
```

This separation prevents the learning agent from consuming unvalidated external messages as trusted state.

From an AI-systems perspective, the security layer therefore protects both:

- **model inputs**, by validating observations and peer messages;
- **model actions**, by authenticating and signing outbound control messages.

This is especially important for distributed AI systems where model quality alone does not guarantee system integrity.

---

# 📊 Performance Considerations

Cryptographic operations add processing overhead to every protected message.

The current implementation uses RSA-2048 with RSA-PSS signatures.

For low-frequency traffic-control messaging, this overhead is small compared with the traffic-control update interval.

Rather than treating cryptographic cost as zero, the design isolates signing and verification primitives inside `crypto_utils.py` so the algorithm can be replaced independently if future deployment requires lower-latency primitives.

Potential alternatives include:

- Ed25519 for lower signature overhead;
- hardware-backed key operations;
- asynchronous verification;
- session-level authenticated messaging.

Any specific latency claim should be benchmarked on the target hardware before production use.

---

# 🧪 Security Design Principles

The implementation follows several software and security engineering principles:

### Least Trust

Messages are not trusted simply because they originate from another traffic controller.

### Defense in Depth

Transport encryption, identity validation, application signatures and authorization checks provide separate protection layers.

### Explicit Authorization

Emergency privileges require signed credentials rather than boolean metadata.

### Replay Resistance

Nonces and timestamp validation prevent reuse of previously accepted commands.

### Separation of Concerns

Cryptographic logic is isolated from traffic-control and MARL decision code.

### Testable Security Properties

Each major threat maps to an executable test or adversarial scenario.

---

# ⚠️ Security Boundaries

This project is a research and simulation artifact, not a certified production ITS security platform.

The current architecture does not attempt to solve every possible attack class.

### Compromised Controllers

If an attacker gains control of an intersection controller and its private key, the attacker can authenticate as that legitimate controller.

Mitigations such as hardware attestation and secure enclaves are outside the current scope.

### Denial-of-Service at Scale

Authentication rejects unauthorized messages, but large-scale volumetric network attacks require network-level mitigation beyond the application layer.

### Side-Channel Attacks

Hardware timing, power-analysis and electromagnetic side-channel protections are not modeled.

### Certificate Revocation

The simulation uses certificate trust but does not implement a full production certificate-revocation infrastructure.

### Post-Quantum Security

RSA-2048 is not post-quantum secure.

Future work could evaluate post-quantum signatures and key-establishment mechanisms once appropriate deployment constraints are known.

---

# 🚀 Future Security Work

- Certificate revocation and rotation
- Hardware-backed private keys
- Agent attestation
- Rate limiting and distributed DoS protection
- Security-event telemetry
- Intrusion detection across traffic agents
- Secure federated learning
- Model-poisoning detection
- Byzantine-agent detection
- Post-quantum cryptographic migration

---

# 📚 Security Summary

The traffic-management system combines adaptive multi-agent decision making with a separately enforced security boundary.

The implemented security layer provides:

- encrypted inter-agent transport;
- authenticated X.509 identities;
- signed traffic-control messages;
- replay detection;
- emergency-vehicle authorization;
- adversarial attack simulations; and
- automated security validation.

The goal is not merely to demonstrate an adaptive traffic controller, but to explore how **distributed AI agents can make decisions over data and communication channels that are explicitly authenticated and validated before being trusted**.