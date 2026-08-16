<div align="center">

# 🚦 MARL-Driven Real-Time Traffic Management System

### Adaptive traffic control, demand forecasting and secure inter-agent communication

A SUMO-based traffic management project combining **multi-agent adaptive signal control, LSTM traffic forecasting, emergency vehicle prioritization and secure communication between traffic agents**.

<br>

[![Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square\&logo=github\&logoColor=white)](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System)
[![Patent](https://img.shields.io/badge/Patent-202511108091%20A-2563EB?style=flat-square\&logo=googledrive\&logoColor=white)](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square\&logo=python\&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-222222?style=flat-square)

</div>

## Overview

This project explores whether traffic signals can respond to changing road conditions instead of following only a fixed timing plan.

Intersections are modelled as traffic-control agents inside **SUMO**. Python communicates with SUMO through **TraCI**, allowing each controller to observe traffic conditions and adapt signal behaviour during the simulation.

The project also includes:

* LSTM-based traffic demand prediction
* emergency vehicle prioritization
* comparison against a rule-based baseline
* TLS 1.3 mutual authentication
* X.509 certificates for traffic-agent identity
* RSA-PSS signed messages
* SHA-256 integrity checks
* timestamp and nonce-based replay protection
* automated security tests
* executable attack simulations

The traffic-control code and the security code are kept separate so that incoming network messages are validated before they influence a traffic decision.

## 📜 Patent

### Indian Patent Application No. 202511108091 A

A patent application has been filed for the traffic-management approach developed through this project.

[![View Patent](https://img.shields.io/badge/View%20Patent-Google%20Drive-4285F4?style=flat-square\&logo=googledrive\&logoColor=white)](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing)

## 📊 Results

The adaptive controller was compared with the project's rule-based traffic-control baseline in SUMO.

| Metric               | Rule-Based Baseline | Adaptive System |                          Change |
| -------------------- | ------------------: | --------------: | ------------------------------: |
| Average waiting time |                55 s |            32 s |                 **41.8% lower** |
| Queue length         |         30 vehicles |     15 vehicles |                   **50% lower** |
| Fuel consumption     |               120 L |            90 L |                   **25% lower** |
| Throughput           |                 65% |             82% | **17 percentage points higher** |

These values come from the simulation setup used in this repository. They are not measurements from a deployed city traffic network.

### Security validation

* **17 security-focused automated tests**
* **6 simulated attack classes**
* TLS 1.3 mutual authentication
* X.509 agent identities
* RSA-PSS signatures
* SHA-256 integrity validation
* timestamp and nonce-based replay protection
* emergency authorization checks

## 🎯 Problem

Fixed-time traffic signals cannot react well when traffic demand changes significantly.

A static timing plan may continue assigning green time to one approach while another road develops a long queue. This can increase:

* waiting time
* queue length
* fuel consumption
* emergency response delay
* congestion at neighbouring intersections

The project therefore focuses on three related problems:

1. **Adaptive traffic control**
   Signals react to observed traffic conditions.

2. **Traffic demand forecasting**
   An LSTM model is used to represent changing traffic demand.

3. **Secure agent communication**
   Messages between traffic controllers are authenticated before being trusted.

## 🏗️ Architecture

```text
                    Historical Traffic Data
                              |
                              v
                     +------------------+
                     |  LSTM Forecast   |
                     +--------+---------+
                              |
                       Predicted Demand
                              |
                              v
                +---------------------------+
                |      SUMO Simulation      |
                |                           |
                |  J1 <-> J2 <-> J3 <-> J4 |
                |                           |
                +-------------+-------------+
                              |
                    Traffic observations
                              |
            +-----------------+-----------------+
            |                                   |
            v                                   v
   Adaptive Signal Logic              Emergency Priority
            |                                   |
            +-----------------+-----------------+
                              |
                              v
                     Signal Decisions
                              |
                              v
              Waiting Time / Queue / Throughput
```

**SUMO** provides the traffic simulation.

**TraCI** gives the Python controllers access to vehicle states and traffic lights during execution.

## 🧠 Adaptive Traffic Control

Each controlled intersection acts as an independent traffic-signal agent.

### Observed state

The controller can use information such as:

```text
queue length
waiting time
traffic density
emergency vehicle presence
```

### Actions

An agent can change the active traffic-light phase or associated timing according to its current state.

### Reward

The implementation penalizes congestion and waiting time.

```python
reward = -(queue_length + 0.5 * waiting_time)
```

Lower queue lengths and lower waiting time therefore produce a better reward.

## 📈 LSTM Traffic Forecasting

Traffic demand changes over time, so the project includes an LSTM-based forecasting component.

```text
Historical traffic
       |
       v
   LSTM model
       |
       v
Predicted demand
       |
       v
Vehicle generation
       |
       v
SUMO simulation
       |
       v
Adaptive control
```

The forecasting component allows experiments to use changing traffic demand rather than only one static traffic pattern.

## 🚑 Emergency Vehicle Priority

Emergency traffic is treated as a privileged case.

The system does not trust a message only because it contains:

```json
{
  "emergency": true
}
```

A malicious sender could otherwise request priority without authorization.

Emergency requests therefore pass through the same authentication and authorization layer used for protected agent communication.

## 🔐 Security Design

The traffic agents form a small distributed system.

The project therefore protects the communication path separately from the traffic-control algorithm.

| Threat                | Example                              | Protection                           |
| --------------------- | ------------------------------------ | ------------------------------------ |
| Agent impersonation   | Rogue process claims to be J2        | X.509 identity and certificate trust |
| Message tampering     | Signal command is modified           | RSA-PSS signature and SHA-256        |
| Replay                | Old command is sent again            | Nonce and timestamp checks           |
| MITM                  | Traffic is intercepted or redirected | TLS 1.3 mTLS and protected metadata  |
| Emergency spoofing    | Normal vehicle requests priority     | Signed authorization token           |
| Untrusted participant | Certificate is from another CA       | CA validation                        |

The project uses several layers rather than relying only on TLS.

```text
Application
Emergency authorization

Message
RSA-PSS
SHA-256
Nonce
Timestamp
Sender / receiver binding

Identity
X.509 certificates
Trusted CA

Transport
TLS 1.3
Mutual TLS
```

For the full security design, see [`SECURITY.md`](./SECURITY.md).

## 🔧 Security Modules

| File                           | Purpose                                      |
| ------------------------------ | -------------------------------------------- |
| `security/crypto_utils.py`     | RSA, SHA-256, signing and verification       |
| `security/pki.py`              | certificate authority and X.509 certificates |
| `security/secure_message.py`   | signed message envelopes                     |
| `security/secure_channel.py`   | TLS 1.3 communication                        |
| `security/emergency_auth.py`   | emergency authorization                      |
| `security/secure_agent.py`     | integration with traffic agents              |
| `security/attack_simulator.py` | attack demonstrations                        |

## 🧪 Security Testing

Run:

```bash
python -m pytest -v tests/test_security.py
```

The current suite contains **17 security-focused tests**.

The tests cover:

* message tampering
* replayed messages
* stale timestamps
* sender impersonation
* certificate trust
* receiver modification
* emergency authorization
* expired tokens
* token reassignment

### Attack simulation

Run:

```bash
python demo.py
```

Six scenarios are exercised:

| Scenario                   | Expected Result |
| -------------------------- | --------------- |
| Message tampering          | Blocked         |
| Agent impersonation        | Blocked         |
| Replay                     | Blocked         |
| MITM redirection           | Blocked         |
| Emergency spoofing         | Blocked         |
| Forged authorization token | Blocked         |

### TLS smoke test

Run:

```bash
python tls_smoke_test.py
```

This validates the mutual TLS path separately from the signed-message tests.

## 🛠️ Technology Stack

| Area                | Technology                        |
| ------------------- | --------------------------------- |
| Language            | Python                            |
| Traffic simulation  | SUMO                              |
| Simulation control  | TraCI                             |
| Adaptive control    | Multi-agent traffic-control logic |
| Forecasting         | LSTM                              |
| Numerical computing | NumPy                             |
| Cryptography        | RSA-2048, RSA-PSS, SHA-256        |
| Identity            | X.509 PKI                         |
| Transport security  | TLS 1.3, mTLS                     |
| Testing             | pytest                            |
| Evaluation          | CSV-based simulation metrics      |

## 📁 Repository Structure

```text
MARL-Driven-Real-Time-Traffic-Management-System/
|
├── marl_agent.py
├── run_marl_agent.py
├── run_secure_marl_agent.py
├── csv_gen.py
├── final2.sumocfg
|
├── fixed_timing_results.csv
├── Marl_timing_results.csv
|
├── generate_keys.py
├── demo.py
├── tls_smoke_test.py
|
├── security/
│   ├── crypto_utils.py
│   ├── pki.py
│   ├── secure_message.py
│   ├── secure_channel.py
│   ├── emergency_auth.py
│   ├── secure_agent.py
│   └── attack_simulator.py
|
├── tests/
│   └── test_security.py
|
├── SECURITY.md
├── LICENSE
└── README.md
```

## 🚀 Running the Project

### Requirements

You need:

* Python 3.10+
* SUMO
* TraCI
* NumPy
* `cryptography`
* `pytest`

Install the Python packages:

```bash
pip install numpy traci cryptography pytest
```

SUMO must also be installed and available in the environment.

### Run the traffic simulation

```bash
python run_marl_agent.py
```

### Generate agent keys and certificates

```bash
python generate_keys.py --agents J1 J2 J3 J4
```

### Run the secure simulation

```bash
python run_secure_marl_agent.py
```

### Generate evaluation output

```bash
python csv_gen.py
```

### Run security tests

```bash
python -m pytest -v tests/test_security.py
```

### Run attack scenarios

```bash
python demo.py
```

### Test mutual TLS

```bash
python tls_smoke_test.py
```

## 🔬 What I Focused On

### Traffic control

The project experiments with changing signal behaviour according to local traffic conditions instead of relying only on fixed timing plans.

### Forecasting

LSTM-based forecasting is used to represent changing traffic demand.

### Emergency handling

Emergency priority is supported, but requests still have to pass authorization checks.

### Secure distributed communication

Traffic-agent messages are authenticated and validated before they affect another controller.

### Testing

Traffic behaviour and security behaviour are validated separately so the security architecture is not only documented but also exercised through code.

## ⚠️ Limitations

This repository is a **simulation and research project**.

The traffic results come from SUMO and do not represent a deployed municipal traffic system.

The security implementation is also a prototype. It is not a certified Intelligent Transportation System security platform.

Current limitations include:

* simulation-scale road networks
* no live municipal sensor feed
* no production certificate revocation service
* no hardware-backed key storage
* no large-scale DoS mitigation
* no compromised-controller recovery
* no post-quantum cryptography

## 🔭 Possible Next Steps

* larger SUMO road networks
* cooperative traffic-agent policies
* additional baseline comparisons
* real traffic sensor datasets
* camera-based vehicle detection
* edge deployment
* certificate revocation and rotation
* controller attestation
* Byzantine-agent detection
* security telemetry
* post-quantum authentication experiments

## 📚 Project Resources

| Resource               | Link                                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------------------- |
| Repository             | [GitHub](https://github.com/agrima08s010315/MARL-Driven-Real-Time-Traffic-Management-System)        |
| Patent                 | [View document](https://drive.google.com/file/d/1QSSDN_fmPc41MEugw1atImfDk9ymtrHb/view?usp=sharing) |
| Security documentation | [`SECURITY.md`](./SECURITY.md)                                                                      |
| Security tests         | [`tests/test_security.py`](./tests/test_security.py)                                                |

<div align="center">

## Author

### Agrima Saxena

**Software Engineering · Applied AI · Secure Systems**

<table align="center">
<tr>

<td align="center" width="70">
<a href="https://www.linkedin.com/in/agrima-saxena-142960426/">
<img src="https://img.icons8.com/color/48/linkedin.png" width="32" height="32" alt="LinkedIn"/>
</a>
</td>

<td align="center" width="70">
<a href="mailto:agrimalc@gmail.com">
<img src="https://img.icons8.com/color/48/gmail-new.png" width="32" height="32" alt="Email"/>
</a>
</td>

<td align="center" width="70">
<a href="https://github.com/agrima08s010315">
<img src="https://img.icons8.com/ios-glyphs/48/ffffff/github.png" width="32" height="32" alt="GitHub"/>
</a>
</td>

</tr>
</table>

<br>

If you want to understand the security side first, start with [`SECURITY.md`](./SECURITY.md).

</div>
