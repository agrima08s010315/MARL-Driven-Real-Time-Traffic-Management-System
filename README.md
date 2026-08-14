# 🚦 MARL Traffic Intelligence

### Multi-Agent Reinforcement Learning for Adaptive & Secure Urban Traffic Control

> A simulation-driven intelligent transportation system combining multi-agent traffic-signal control, predictive traffic modelling, SUMO/TraCI, and cryptographically secured agent communication.

---

## Overview

Urban traffic signals are typically controlled using fixed schedules or predefined rules that react poorly to rapidly changing traffic conditions.

**MARL Traffic Intelligence** explores a different approach: model each traffic intersection as an autonomous decision-making agent capable of observing local traffic conditions and adapting its signal phase in response.

The system integrates:

- 🚦 **Multi-Agent Reinforcement Learning** for adaptive signal control
- 📈 **LSTM-based traffic prediction** for dynamic traffic-demand modelling
- 🏙️ **SUMO + TraCI** for microscopic traffic simulation and real-time control
- 🚑 **Emergency vehicle prioritization**
- 🔐 **TLS 1.3, PKI and signed messages** for secure inter-agent communication
- 🧪 **Adversarial security testing** against six attack scenarios

The project combines **AI systems, graph-like multi-agent coordination, simulation, cybersecurity, and intelligent transportation infrastructure** in a reproducible research environment.

---

## 🎯 Problem

Fixed-time traffic signals cannot respond effectively to changing traffic demand.

During congestion, the same predetermined signal plan may remain active despite large differences in queue lengths between approaches. This can result in:

- longer vehicle waiting times;
- growing intersection queues;
- reduced traffic throughput;
- unnecessary fuel consumption;
- poor coordination between neighbouring intersections; and
- delayed emergency vehicle movement.

The goal of this project is to investigate whether **decentralized learning agents can adapt traffic signals dynamically while communicating securely in a simulated smart-city environment.**

---

## 💡 System Design

Each controlled intersection acts as an autonomous traffic-signal agent.

The agent observes the traffic environment, evaluates congestion conditions, selects a signal action, receives a reward from the resulting traffic state, and continuously adapts its policy.

```text
                         ┌──────────────────────┐
                         │   Traffic Dataset    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   LSTM Prediction    │
                         │ Traffic Flow / Demand│
                         └──────────┬───────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────┐
│                       SUMO Environment                        │
│                                                               │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐             │
│   │ Agent J1 │◄───►│ Agent J2 │◄───►│ Agent J3 │             │
│   └────┬─────┘     └────┬─────┘     └────┬─────┘             │
│        │                │                │                    │
│   Queue / Wait     Traffic Density   Emergency State          │
│        │                │                │                    │
│        └────────────────┼────────────────┘                    │
│                         ▼                                     │
│                Adaptive Signal Control                        │
└─────────────────────────┬─────────────────────────────────────┘
                          │
                          ▼
               ┌───────────────────────┐
               │ Performance Metrics   │
               │ Delay • Queue • Flow  │
               └───────────────────────┘
```

TraCI provides the control interface between Python agents and the running SUMO simulation.

---

## 🧠 Multi-Agent Traffic Control

### State Space

Each traffic-signal agent observes features including:

```text
Queue Length
Vehicle Waiting Time
Traffic Density
Emergency Vehicle Presence
```

### Action Space

Agents dynamically select traffic-light phase changes based on the observed intersection state.

Instead of executing a permanently fixed timing plan, signal decisions therefore respond to current traffic conditions.

### Reward

The reward penalizes congestion and accumulated waiting time.

```python
reward = -(queue_length + 0.5 * waiting_time)
```

This encourages agents to discover policies that reduce queues while preventing excessive vehicle delay.

---

## 📈 Traffic Prediction

An LSTM-based forecasting component models changing traffic demand and vehicle arrivals.

```text
Historical Traffic
       │
       ▼
   LSTM Model
       │
       ▼
Predicted Demand
       │
       ▼
Vehicle Generation
       │
       ▼
SUMO Simulation
```

Combining forecasting with adaptive control allows the simulation to represent traffic conditions that change over time rather than relying exclusively on static demand.

---

## 🚑 Emergency Vehicle Priority

Emergency vehicles introduce a second optimization objective: minimizing emergency delay without destabilizing surrounding traffic.

When an authorized emergency vehicle is detected, the system can modify signal behaviour to facilitate clearance through the intersection.

Because blindly trusting an `"emergency": true` message would create a security vulnerability, emergency priority is integrated with the project's authentication layer.

---

# 🔐 Security Engineering

Connected traffic infrastructure introduces a different class of problem.

A traffic-control algorithm may perform correctly while still being unsafe if an attacker can impersonate another intersection, replay an old signal command, modify traffic data, or fraudulently request emergency priority.

The project therefore implements a **defense-in-depth communication layer** around the traffic agents.

## Threat Model

| Threat | Potential impact | Defense |
|---|---|---|
| Man-in-the-Middle | Intercept or alter agent traffic | TLS 1.3 + mutual TLS |
| Agent impersonation | Rogue controller joins network | X.509 certificates |
| Message tampering | Modify signal commands | RSA-PSS signatures |
| Replay attack | Reuse valid historical commands | Nonce + timestamp validation |
| Message misrouting | Redirect legitimate commands | Signed message metadata |
| Emergency spoofing | Fraudulent traffic priority | Cryptographic emergency authorization |

---

## 🛡️ Defense-in-Depth Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│        Authenticated Emergency Vehicle Authorization         │
├──────────────────────────────────────────────────────────────┤
│                      MESSAGE LAYER                           │
│       RSA-PSS • SHA-256 • Nonce • Timestamp Validation       │
├──────────────────────────────────────────────────────────────┤
│                      IDENTITY LAYER                          │
│             X.509 PKI • Per-Agent Certificates               │
├──────────────────────────────────────────────────────────────┤
│                     TRANSPORT LAYER                          │
│                 TLS 1.3 Mutual TLS                           │
└──────────────────────────────────────────────────────────────┘
```

### Security Components

| Module | Responsibility |
|---|---|
| `crypto_utils.py` | RSA-2048, SHA-256 and RSA-PSS cryptographic primitives |
| `pki.py` | Certificate authority and per-agent X.509 certificates |
| `secure_message.py` | Signed, timestamped and nonced message envelopes |
| `secure_channel.py` | TLS 1.3 mutual-authentication channel |
| `emergency_auth.py` | Emergency-vehicle authorization tokens |
| `secure_agent.py` | Security integration with traffic agents |
| `attack_simulator.py` | Adversarial security scenarios |

See [`SECURITY.md`](./SECURITY.md) for the STRIDE threat model and detailed security design.

---

## ⚔️ Adversarial Validation

The security layer is not documented only as an architectural proposal.

The repository contains automated tests and attack simulations that exercise the implemented defenses.

### Security Test Suite

```bash
python -m pytest -v tests/test_security.py
```

**17 security tests** validate properties including authentication, message integrity, replay protection and emergency authorization.

### Attack Simulation

```bash
python demo.py
```

The simulation exercises six adversarial scenarios:

| Attack | Expected result |
|---|---|
| Message tampering | 🛡️ Blocked |
| Agent impersonation | 🛡️ Blocked |
| Replay attack | 🛡️ Blocked |
| MITM redirection | 🛡️ Blocked |
| Emergency spoofing | 🛡️ Blocked |
| Forged authorization token | 🛡️ Blocked |

### TLS Verification

```bash
python tls_smoke_test.py
```

This verifies the live TLS 1.3 mutual-authentication path between simulated traffic-system participants.

---

# 📊 Simulation Results

The simulation study compared adaptive traffic control against the project's rule-based baseline.

| Metric | Baseline | MARL System | Change |
|---|---:|---:|---:|
| Average waiting time | 55 s | 32 s | ↓ 41.8% |
| Queue length | 30 vehicles | 15 vehicles | ↓ 50.0% |
| Fuel consumption | 120 L | 90 L | ↓ 25.0% |
| Traffic throughput | 65% | 82% | ↑ 17 percentage points |

These values are derived from the project's simulation study and should be interpreted as **simulation results rather than real-world deployment measurements**.

The results suggest that adaptive control can substantially improve traffic flow under the evaluated simulation conditions.

---

# 🧪 Reproducing the Project

## Prerequisites

- Python
- SUMO
- TraCI
- NumPy
- Cryptography
- Pytest

Install the Python dependencies:

```bash
pip install numpy traci cryptography pytest
```

SUMO must also be installed and available to the simulation environment.

## Run Traffic Simulation

```bash
python run_marl_agent.py
```

## Run Secure Traffic Simulation

Generate the PKI material once:

```bash
python generate_keys.py --agents J1 J2 J3 J4
```

Then start the security-enabled simulation:

```bash
python run_secure_marl_agent.py
```

## Generate Performance Results

```bash
python csv_gen.py
```

## Validate Security

```bash
python -m pytest -v tests/test_security.py
python demo.py
python tls_smoke_test.py
```

---

# 🛠️ Technology

| Area | Technologies |
|---|---|
| Traffic Simulation | SUMO, TraCI |
| Intelligent Control | Multi-Agent Reinforcement Learning |
| Traffic Forecasting | LSTM, TensorFlow/Keras |
| Core Engineering | Python, NumPy |
| Cryptography | RSA-2048, RSA-PSS, SHA-256 |
| Identity | X.509 PKI |
| Transport Security | TLS 1.3 / mTLS |
| Testing | Pytest |
| Analysis | CSV-based simulation metrics |

---

# 📁 Repository Structure

```text
.
├── marl_agent.py
├── run_marl_agent.py
├── run_secure_marl_agent.py
├── csv_gen.py
├── final2.sumocfg
│
├── fixed_timing_results.csv
├── Marl_timing_results.csv
│
├── generate_keys.py
├── demo.py
├── tls_smoke_test.py
│
├── security/
│   ├── crypto_utils.py
│   ├── pki.py
│   ├── secure_message.py
│   ├── secure_channel.py
│   ├── emergency_auth.py
│   ├── secure_agent.py
│   └── attack_simulator.py
│
├── tests/
│   └── test_security.py
│
├── SECURITY.md
└── README.md
```

---

# 🔬 Engineering Contributions

The project explores several engineering problems within one system:

### Multi-Agent Decision Making
Models intersections as independent agents operating within a shared traffic environment.

### Adaptive Traffic Control
Changes signal behaviour according to measured traffic conditions rather than relying exclusively on fixed schedules.

### Predictive Traffic Modelling
Uses temporal traffic prediction to represent changing demand within the simulation.

### Emergency-Aware Optimization
Introduces priority handling for emergency vehicles alongside general congestion objectives.

### Secure Distributed Agents
Protects inter-agent communication through authenticated identities, encrypted transport and signed messages.

### Adversarial Testing
Validates security assumptions using executable attack scenarios instead of relying exclusively on documentation.

---

# 🚀 Future Work

- Real-world traffic sensor integration
- Camera-based vehicle detection
- Larger multi-intersection MARL experiments
- Federated training across traffic regions
- Edge deployment of intersection agents
- Adaptive route recommendation
- City-scale traffic-network evaluation
- Formal comparison of independent vs. cooperative MARL policies
- Post-quantum cryptographic migration

---

# ⚠️ Scope

This repository is a **research and simulation project**.

Performance measurements were produced in SUMO-based experiments and do not represent results from deployment on a real municipal transportation network.

The cybersecurity components demonstrate defensive mechanisms in the simulated agent environment and are not presented as a certified production ITS security implementation.

---

## 👩‍💻 Author

**Agrima Saxena**  
B.Tech — Computer & Communication Engineering  
Manipal University Jaipur

---

### ⭐ If this project interests you

Explore the implementation, reproduce the simulations, review the security model, or open an issue with an improvement.