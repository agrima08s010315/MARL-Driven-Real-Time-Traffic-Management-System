# 🔐 Security Architecture

### Secure communication for distributed traffic-control agents

The MARL traffic-management project treats each intersection controller as a distributed software agent.

That means traffic decisions are not the only concern. A secure system also needs to verify **who sent a message, whether it was changed, whether it is fresh, and whether the sender is authorized to request a privileged action**.

The security layer uses:

`TLS 1.3` `mTLS` `X.509` `RSA-PSS` `SHA-256` `Nonce Validation` `Timestamp Validation`

## 🎯 Security Goals

The design focuses on the following properties:

| Goal | Implementation |
|---|---|
| Agent authentication | X.509 certificates issued by a trusted CA |
| Confidentiality | TLS 1.3 |
| Mutual authentication | mTLS |
| Message authenticity | RSA-PSS signatures |
| Message integrity | SHA-256 + signature verification |
| Replay resistance | timestamps + nonce tracking |
| Receiver validation | receiver identity included in protected metadata |
| Emergency authorization | signed authorization token |

The goal is simple:

> A traffic controller should not trust a network message until the sender, receiver, freshness, integrity, and authorization have been checked.

## 🧩 Security Model

Incoming network data is treated as untrusted.

Before a network message can influence the traffic controller, it passes through a validation pipeline.

```text
Incoming Network Message
          |
          v
Transport Authentication
          |
          v
Sender / Receiver Validation
          |
          v
Timestamp Check
          |
          v
Nonce Check
          |
          v
Signature Verification
          |
          v
Payload Integrity Check
          |
          v
Validated Message
          |
          v
Traffic-Control Logic
```

This keeps the security decision separate from the traffic-control decision.

## 🛡️ Threat Model

The project uses STRIDE to organize the main threats considered.

| Threat | Example | Mitigation |
|---|---|---|
| Spoofing | Attacker pretends to be intersection J2 | X.509 identity + signature validation |
| Tampering | Signal command is changed | RSA-PSS + SHA-256 |
| Repudiation | Sender disputes issuing a message | signed sender metadata |
| Information disclosure | Network traffic is observed | TLS 1.3 |
| Denial of service | Repeated fake priority requests | authentication + authorization checks |
| Elevation of privilege | Normal vehicle claims emergency status | signed emergency authorization token |

The application can reject unauthorized requests, but it does not claim to prevent large volumetric network attacks.

## 🏗️ Security Layers

The design uses several controls because no single mechanism solves every problem.

```text
Application Layer
Emergency Authorization

Message Layer
RSA-PSS
SHA-256
Timestamp
Nonce
Sender / Receiver Binding

Identity Layer
X.509 Certificates
Trusted Certificate Authority

Transport Layer
TLS 1.3
Mutual TLS
```

### Transport Security

TLS 1.3 encrypts communication between participating traffic agents.

Mutual TLS requires both endpoints to authenticate.

### Agent Identity

Each traffic agent receives an X.509 certificate issued by the simulated traffic authority.

### Message Protection

Protected messages include the sender, receiver, timestamp, nonce, payload digest, and signature.

### Application Authorization

Emergency priority is treated as a privileged operation and requires separate authorization.

## 📂 Security Components

| File | Responsibility |
|---|---|
| `security/crypto_utils.py` | key generation, hashing, signing and verification |
| `security/pki.py` | certificate authority and X.509 agent certificates |
| `security/secure_message.py` | protected message format |
| `security/secure_channel.py` | TLS communication |
| `security/emergency_auth.py` | emergency authorization |
| `security/secure_agent.py` | security integration with traffic agents |
| `security/attack_simulator.py` | adversarial scenarios |

## ✉️ Protected Message Format

A protected message contains information about the sender, receiver, payload and freshness.

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

The implementation can be reviewed in:

[`security/secure_message.py`](./security/secure_message.py)

## ✅ Message Validation

The receiving agent performs the checks in a defined order.

### 1. Receiver Validation

The message must be intended for the local agent.

### 2. Sender Trust

The sender must correspond to a recognized participant.

### 3. Timestamp Validation

Messages outside the accepted freshness window are rejected.

### 4. Nonce Validation

A nonce that has already been accepted cannot be reused.

### 5. Signature Verification

The RSA-PSS signature is verified using the sender's public key.

### 6. Payload Integrity

The payload digest is recomputed and checked against the protected value.

```text
Incoming Message
      |
      v
Correct Receiver?
   no -> Reject
   yes
      |
      v
Trusted Sender?
   no -> Reject
   yes
      |
      v
Fresh Timestamp?
   no -> Reject
   yes
      |
      v
Nonce Already Used?
   yes -> Reject
   no
      |
      v
Signature Valid?
   no -> Reject
   yes
      |
      v
Payload Valid?
   no -> Reject
   yes
      |
      v
Accept Message
```

## 🚑 Emergency Vehicle Authorization

Emergency priority is handled separately from ordinary traffic information.

A controller does not trust a request simply because it contains:

```json
{
  "emergency": true
}
```

That would make emergency priority trivial to spoof.

Instead, the simulated authorization token contains information such as:

```text
vehicle_id
dispatched_at
expires_at
reason_code
signature
```

Example:

```json
{
  "vehicle_id": "ambulance_7",
  "dispatched_at": 1735947000,
  "expires_at": 1735947600,
  "reason_code": "AMBULANCE",
  "signature": "<dispatch authority signature>"
}
```

The controller checks:

- whether the vehicle ID matches the requester
- whether the token is within its validity period
- whether the token has expired
- whether the dispatch-authority signature is valid
- whether the token has been modified

Only after these checks can the request be treated as authorized emergency traffic.

## 🪪 PKI and Agent Identity

The simulation uses a small certificate hierarchy.

```text
Traffic Authority CA
       |
       +---- J1 Certificate
       |
       +---- J2 Certificate
       |
       +---- J3 Certificate
       |
       +---- J4 Certificate
```

The traffic authority acts as the trust anchor.

A certificate issued by an unrelated CA should not be accepted as a trusted controller identity.

## 🔑 Key Material

| Credential | Used By | Simulation Storage |
|---|---|---|
| CA private key | traffic authority | `keys/ca_key.pem` |
| Agent private key | individual controller | local agent files |
| Agent certificate | traffic agent | CA-signed certificate |
| Emergency authority private key | simulated dispatch authority | dispatch-side storage |
| Emergency authority public key | traffic agents | provisioned trust material |

Private keys should not be committed to the repository.

A production deployment would require stronger key protection such as:

- HSMs
- TPM-backed keys
- secure enclaves
- managed secret systems

## 🧪 Security Tests

Run:

```bash
python -m pytest -v tests/test_security.py
```

The current suite contains **17 security-focused tests**.

Coverage includes:

| Scenario | Security Control |
|---|---|
| Modified payload | RSA-PSS validation |
| Impersonated sender | certificate + signature checks |
| Certificate from another CA | trust validation |
| Replayed message | nonce tracking |
| Old message | timestamp freshness |
| Receiver changed | protected receiver identity |
| Fake emergency request | emergency authorization |
| Forged token | dispatch signature validation |
| Token used by another vehicle | vehicle-ID binding |
| Expired token | token validity window |

The exact tests can be reviewed in:

[`tests/test_security.py`](./tests/test_security.py)

## ⚔️ Attack Simulation

Run:

```bash
python demo.py
```

The demo exercises six attack categories:

```text
message tampering
agent impersonation
replay
MITM redirection
emergency spoofing
forged authorization token
```

The expected result is that each attempt is rejected by the relevant control.

## 🔒 TLS Test

The TLS path can be tested separately.

```bash
python tls_smoke_test.py
```

This verifies mutual authentication without requiring the complete traffic simulation.

## 🔍 Why Use Both TLS and Signatures?

TLS protects the communication channel between two endpoints.

Application-level signatures protect individual messages.

Using both provides two different guarantees:

- TLS protects data in transit
- signatures preserve message-level authenticity and integrity

A signed message still carries verifiable sender and integrity information after it reaches the application layer.

## 🧠 Interaction With the Traffic Controller

Security checks happen before external network data is treated as trusted input.

```text
Incoming Data
     |
     v
Security Validation
     |
     v
Trusted Input
     |
     v
Traffic Controller
     |
     v
Signal Decision
     |
     v
Protected Outgoing Message
```

The traffic controller decides **what action should be taken**.

The security layer decides **whether external information should be trusted**.

Keeping those responsibilities separate makes the system easier to reason about and test.

## ⚡ Cryptographic Performance

Cryptographic operations introduce computational overhead.

The current implementation uses:

- RSA-2048
- RSA-PSS
- SHA-256

The cryptographic code is isolated in utility modules so the implementation can be changed without rewriting the traffic-control logic.

Possible future alternatives include:

- Ed25519
- hardware-backed signing
- asynchronous verification
- session-level authenticated messaging

No fixed cryptographic latency is claimed because actual performance depends on hardware and deployment conditions.

## ⚠️ Limitations

This is a research and simulation project, not a production ITS security system.

### Compromised Controller

If an attacker steals the private key of a legitimate controller, certificate authentication alone cannot distinguish the attacker from the compromised controller.

Possible mitigations include:

- hardware-backed keys
- secure enclaves
- remote attestation
- behavioural monitoring

### Large-Scale DoS

The application can reject unauthorized messages, but it cannot prevent a large network flood before those messages reach the application.

### Certificate Revocation

The simulation uses CA-based trust but does not implement a full production certificate-revocation system.

### Endpoint Security

The project does not currently model:

- secure boot
- firmware integrity
- operating-system hardening
- physical controller security

### Side-Channel Attacks

Timing attacks, power analysis and other hardware side channels are outside the scope of the simulation.

### Post-Quantum Security

RSA-2048 is not post-quantum secure.

The repository does not claim post-quantum protection.

## 🔭 Future Work

Possible security extensions include:

- certificate rotation
- certificate revocation
- hardware-backed private keys
- controller attestation
- security event telemetry
- rate limiting
- network-level DoS mitigation
- Byzantine-agent detection
- anomaly detection
- secure federated learning
- model-poisoning detection
- SIEM integration
- post-quantum signature experiments

## 📁 Security Files

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
```

## 📌 What This Security Layer Demonstrates

The security implementation focuses on a practical distributed-systems question:

> Before one traffic controller trusts another controller's message, what should it verify?

In this project, that verification includes:

- transport security
- sender identity
- intended receiver
- message authenticity
- message integrity
- timestamp freshness
- nonce reuse
- emergency authorization

The main implemented controls are:

- TLS 1.3
- mutual authentication
- X.509 certificates
- RSA-PSS signatures
- SHA-256 integrity validation
- timestamp validation
- nonce-based replay protection
- emergency authorization tokens
- automated security tests
- adversarial attack simulations

## 📚 Related Resources

| Resource | Link |
|---|---|
| Main Project README | [`README.md`](./README.md) |
| Security Tests | [`tests/test_security.py`](./tests/test_security.py) |
| Repository | [GitHub](https://github.com/agcodes0315/MARL-Driven-Real-Time-Traffic-Management-System) |
| Patent | [View Patent](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing) |