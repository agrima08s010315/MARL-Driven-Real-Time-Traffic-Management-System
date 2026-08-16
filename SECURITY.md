<div align="center">

# 🔐 Security Architecture

### Secure communication for the traffic-control agents

**TLS 1.3 · mTLS · X.509 · RSA-PSS · SHA-256 · Replay Protection**

</div>

## Purpose

This document explains the security layer used by the traffic-management project.

The traffic controllers are treated as distributed software agents.

Even if the traffic-control algorithm behaves correctly, the overall system can still fail if another process can impersonate an intersection, alter a command, replay an old message or request emergency priority without authorization.

The security implementation is mainly located in the [`security/`](./security/) directory.

The current design focuses on:

* agent identity
* communication confidentiality
* message integrity
* message authenticity
* replay resistance
* receiver validation
* emergency vehicle authorization

## Security Model

Incoming network messages are not treated as trusted automatically.

Before a network-sourced message can influence a traffic controller, it passes through a sequence of checks.

```text
Network message
     |
     v
Transport authentication
     |
     v
Sender and receiver validation
     |
     v
Timestamp and nonce checks
     |
     v
Signature verification
     |
     v
Payload integrity check
     |
     v
Trusted message
     |
     v
Traffic-control logic
```

This keeps the security decision separate from the traffic-control decision.

## Security Goals

| Goal                    | Implementation                                   |
| ----------------------- | ------------------------------------------------ |
| Agent authentication    | X.509 certificates and trusted CA                |
| Confidentiality         | TLS 1.3                                          |
| Mutual authentication   | mTLS                                             |
| Message authenticity    | RSA-PSS signatures                               |
| Message integrity       | SHA-256 and signature verification               |
| Replay resistance       | timestamps and nonce tracking                    |
| Emergency authorization | signed authorization token                       |
| Receiver binding        | receiver identity included in protected metadata |

## Threat Model

STRIDE is used to organize the main threats considered by the project.

| STRIDE Area            | Example                                      | Mitigation                              |
| ---------------------- | -------------------------------------------- | --------------------------------------- |
| Spoofing               | Attacker claims to be intersection J2        | X.509 identity and signature validation |
| Tampering              | Signal command is changed                    | RSA-PSS and SHA-256                     |
| Repudiation            | Sender disputes issuing a message            | signed sender metadata                  |
| Information disclosure | Network traffic is observed                  | TLS 1.3                                 |
| Denial of service      | Fake priority requests are sent repeatedly   | authentication and authorization checks |
| Elevation of privilege | Normal vehicle requests emergency privileges | signed emergency authorization          |

The DoS protection here is limited to rejecting unauthorized traffic. Large volumetric network attacks are outside the scope of this simulation.

## Security Layers

The project uses several controls because each one protects a different part of the communication path.

```text
Application
Emergency authorization

Message
RSA-PSS
SHA-256
Timestamp
Nonce
Sender / receiver binding

Identity
X.509 certificates
Trusted certificate authority

Transport
TLS 1.3
Mutual TLS
```

### Transport

TLS 1.3 encrypts traffic between participating agents.

Mutual TLS requires both endpoints to authenticate.

### Identity

Each traffic agent receives an X.509 certificate issued by the simulated traffic authority.

### Message protection

Messages include metadata that allows the receiver to check the sender, intended receiver, freshness and integrity.

### Application authorization

Emergency priority is treated as a privileged operation instead of a normal boolean field.

## Security Files

| File                           | Responsibility                                    |
| ------------------------------ | ------------------------------------------------- |
| `security/crypto_utils.py`     | key generation, hashing, signing and verification |
| `security/pki.py`              | certificate authority and agent certificates      |
| `security/secure_message.py`   | protected message format                          |
| `security/secure_channel.py`   | TLS communication                                 |
| `security/emergency_auth.py`   | emergency authorization                           |
| `security/secure_agent.py`     | traffic-agent security integration                |
| `security/attack_simulator.py` | attack demonstrations                             |

## Protected Message Format

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

The implementation can be inspected in [`security/secure_message.py`](./security/secure_message.py).

## Message Validation

The receiving agent performs the checks in a defined sequence.

### 1. Receiver validation

The message must be addressed to the local agent.

### 2. Sender trust

The sender must correspond to a trusted participant.

### 3. Timestamp validation

Messages outside the accepted freshness window are rejected.

### 4. Nonce validation

A nonce that has already been accepted cannot be reused.

### 5. Signature verification

The RSA-PSS signature is verified using the sender public key.

### 6. Payload integrity

The payload digest is recomputed and compared with the protected value.

```text
Incoming message
      |
      v
Correct receiver?
  no -> reject
  yes
      |
      v
Trusted sender?
  no -> reject
  yes
      |
      v
Fresh timestamp?
  no -> reject
  yes
      |
      v
Nonce already used?
  yes -> reject
  no
      |
      v
Signature valid?
  no -> reject
  yes
      |
      v
Payload valid?
  no -> reject
  yes -> accept
```

## Emergency Vehicle Authorization

Emergency priority is treated separately from ordinary traffic information.

A request is not trusted simply because it claims emergency status.

The authorization token contains information such as:

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

A traffic controller checks:

* whether the vehicle ID matches the requester
* whether the token is still valid
* whether the token has expired
* whether the dispatch signature is valid
* whether the token was modified

This prevents a message such as:

```json
{
  "emergency": true
}
```

from being treated as sufficient proof of emergency status.

## PKI

The project uses a small public-key infrastructure for the simulation.

```text
Traffic Authority CA
       |
       +---- J1 certificate
       |
       +---- J2 certificate
       |
       +---- J3 certificate
       |
       +---- J4 certificate
```

The traffic authority acts as the trust anchor.

A certificate signed by an unrelated CA should not be accepted as a valid traffic-controller identity.

## Key Material

| Credential                      | Used By                      | Simulation Storage         |
| ------------------------------- | ---------------------------- | -------------------------- |
| CA private key                  | traffic authority            | `keys/ca_key.pem`          |
| Agent private key               | individual controller        | local agent files          |
| Agent certificate               | traffic agents               | CA-signed certificate      |
| Emergency authority private key | simulated dispatch authority | dispatch-side storage      |
| Emergency public key            | traffic agents               | provisioned trust material |

Private keys should not be committed to the repository.

A production implementation would require stronger key protection, for example HSMs, TPM-backed storage or another managed key system.

## Security Tests

Run:

```bash
python -m pytest -v tests/test_security.py
```

The current suite contains **17 security-focused tests**.

Examples include:

| Scenario                       | Security Control                 |
| ------------------------------ | -------------------------------- |
| Modified payload               | RSA-PSS validation               |
| Impersonated sender            | certificate and signature checks |
| Certificate from another CA    | trust validation                 |
| Replayed message               | nonce tracking                   |
| Old message                    | timestamp freshness              |
| Receiver changed               | protected receiver identity      |
| Fake emergency request         | emergency authorization          |
| Forged token                   | dispatch signature validation    |
| Token used for another vehicle | vehicle-ID binding               |
| Expired token                  | validity window                  |

The exact implementation can be reviewed in [`tests/test_security.py`](./tests/test_security.py).

## Attack Simulation

Run:

```bash
python demo.py
```

The demo covers six attack categories:

```text
message tampering
agent impersonation
replay
MITM redirection
emergency spoofing
forged authorization token
```

The expected result is that each attempt is rejected by the corresponding control.

## TLS Test

The TLS path can be tested separately with:

```bash
python tls_smoke_test.py
```

This verifies mutual authentication without requiring the entire traffic simulation to run.

## Why Use Both TLS and Signatures?

TLS protects a connection between two endpoints.

Application-level signatures protect individual messages.

Using both means the implementation does not depend on one mechanism for every property.

A signed message still carries verifiable sender and integrity information after it reaches the application layer.

## Interaction With the Traffic Controller

Security validation happens before network-sourced data is treated as trusted input.

```text
Incoming data
     |
     v
Security checks
     |
     v
Validated input
     |
     v
Traffic controller
     |
     v
Signal decision
     |
     v
Protected outgoing message
```

The traffic controller decides what action to take.

The security layer decides whether external information is trustworthy enough to be used.

## Cryptographic Performance

Cryptographic operations add some overhead.

The implementation currently uses RSA-2048 with RSA-PSS signatures.

For this project, cryptographic functions are isolated in their own utilities so they can be replaced without rewriting the traffic-control logic.

Possible alternatives for future experiments include:

* Ed25519
* hardware-backed signing
* asynchronous verification
* session-level message authentication

The project does not claim a specific cryptographic latency because that depends on the target hardware and deployment environment.

## Limitations

This is a research and simulation project, not a production ITS security system.

### Compromised controller

If an attacker obtains the private key of a legitimate controller, normal certificate authentication cannot distinguish the attacker from that controller.

Possible future mitigations include:

* hardware-backed keys
* remote attestation
* behavioural monitoring

### Large-scale DoS

The application can reject unauthorized messages, but it cannot stop a large network flood before those messages reach the application.

### Certificate revocation

The simulation uses CA-based trust but does not implement a complete production revocation service.

### Endpoint security

Secure boot, firmware protection, operating-system hardening and physical controller security are outside the current scope.

### Side-channel attacks

Timing attacks, power analysis and other hardware side channels are not modelled.

### Post-quantum cryptography

RSA-2048 is not post-quantum secure.

No post-quantum security claim is made by this project.

## Future Work

Possible improvements include:

* certificate rotation
* certificate revocation
* hardware-backed private keys
* controller attestation
* security event logging
* rate limiting
* network-level DoS mitigation
* Byzantine-agent detection
* anomaly detection
* secure federated learning
* model-poisoning detection
* SIEM integration
* post-quantum signature experiments

## Security Files

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

## Summary

The security layer answers a practical question:

**Before one traffic controller trusts another controller's message, what should it verify?**

In this project, that verification includes:

* transport security
* sender identity
* intended receiver
* message integrity
* timestamp freshness
* nonce reuse
* emergency authorization

The main implemented controls are:

* TLS 1.3
* mutual authentication
* X.509 certificates
* RSA-PSS signatures
* SHA-256 validation
* nonce-based replay prevention
* timestamp checks
* emergency authorization tokens
* automated security tests
* adversarial simulations

<div align="center">

### Related

[Main README](./README.md) ·
[Security Tests](./tests/test_security.py) ·
[Repository](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System) ·
[Patent](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)

</div>
