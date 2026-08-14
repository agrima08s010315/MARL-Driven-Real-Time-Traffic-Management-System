# 🚦 MARL Traffic Intelligence

### Multi-Agent Learning for Adaptive and Secure Urban Traffic Control

A simulation-based traffic management system combining **multi-agent adaptive signal control, LSTM traffic-demand prediction, SUMO/TraCI, emergency-vehicle prioritization, and cryptographically secured agent communication**.

The project explores two connected engineering problems:

1. Can decentralized traffic-signal agents reduce congestion compared with rule-based control?
2. How can communication between those agents be protected against spoofing, replay, tampering, and impersonation?

---

## 📊 Results at a Glance

Evaluated against the project's rule-based traffic-control baseline in simulation:

| Metric | Baseline | Adaptive System | Improvement |
|---|---:|---:|---:|
| Average waiting time | 55 s | 32 s | **↓ 41.8%** |
| Queue length | 30 vehicles | 15 vehicles | **↓ 50.0%** |
| Fuel consumption | 120 L | 90 L | **↓ 25.0%** |
| Traffic throughput | 65% | 82% | **↑ 17 pp** |

Security validation:

- **17 automated security tests**
- **6 simulated attack classes blocked**
- **TLS 1.3 mutual authentication**
- **X.509 agent identities**
- **RSA-PSS signed messages**
- **Nonce + timestamp replay protection**

> Results above are from SUMO-based simulation experiments and are not real-world municipal deployment measurements.

---

## 🎯 Problem

Fixed-time traffic signals cannot respond effectively to rapidly changing traffic demand.

A predetermined signal schedule may continue operating even when one approach is heavily congested and another is nearly empty, contributing to:

- longer vehicle waiting times;
- growing intersection queues;
- reduced throughput;
- unnecessary fuel consumption;
- delayed emergency vehicles; and
- poor coordination between neighbouring intersections.

This project models traffic intersections as autonomous agents that adapt signal decisions from observed traffic conditions while operating inside a simulated urban network.

---

## 🏗️ System Architecture

```text
                     Historical Traffic Data
                               │
                               ▼
                      ┌─────────────────┐
                      │ LSTM Prediction │
                      └────────┬────────┘
                               │
                        Predicted Demand
                               │
                               ▼
┌──────────────────────────────────────────────────────────┐
│                    SUMO Environment                       │
│                                                          │
│     ┌──────────┐       ┌──────────┐       ┌──────────┐   │
│     │ Agent J1 │ ◄───► │ Agent J2 │ ◄───► │ Agent J3 │   │
│     └────┬─────┘       └────┬─────┘       └────┬─────┘   │
│          │                  │                   │          │
│     Queue Length       Traffic Density     Emergency      │
│     Waiting Time                           Vehicle State   │
│          └──────────────────┬────────────────┘            │
│                             ▼                             │
│                   Adaptive Signal Control                 │
└─────────────────────────────┬────────────────────────────┘
                              │
                              ▼
                  Waiting • Queue • Throughput
```

**SUMO** provides the microscopic traffic simulation, while **TraCI** gives the Python agents programmatic access to vehicle states and traffic-light controls.

---

## 🧠 Multi-Agent Traffic Control

Each controlled intersection acts as an independent traffic-signal agent interacting with the shared SUMO environment.

### State

Agents observe traffic features including:

```text
Queue Length
Waiting Time
Traffic Density
Emergency Vehicle Presence
```

### Actions

An agent selects traffic-light phase changes according to its current observed state rather than executing a permanently fixed timing schedule.

### Reward

Congestion and accumulated waiting time are penalized:

```python
reward = -(queue_length + 0.5 * waiting_time)
```

This gives agents an optimization signal favouring lower queues and reduced vehicle delay.

---

## 📈 Traffic-Demand Prediction

The forecasting component uses an **LSTM** to model changing traffic demand.

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
SUMO Environment
       │
       ▼
Adaptive Agents
```

Predicted demand can therefore influence simulated vehicle arrivals instead of restricting experiments to a single static traffic pattern.

---

## 🚑 Emergency Vehicle Priority

Emergency vehicles introduce a second objective alongside general congestion reduction.

When an authorized emergency vehicle is detected, traffic-signal behaviour can be adapted to facilitate its movement through an intersection.

However, accepting an unauthenticated message such as:

```json
{
  "emergency": true
}
```

would allow a malicious participant to abuse signal priority.

Emergency requests are therefore integrated with the project's cryptographic authentication mechanisms rather than being trusted solely from message content.

---

# 🔐 Security Engineering

Traffic-control agents form a distributed system. Protecting the control algorithm alone is insufficient if another participant can forge messages, impersonate an intersection, replay old commands, or fraudulently request emergency priority.

The project therefore implements multiple defensive layers around inter-agent communication.

## Threat Model

| Threat | Risk | Implemented Defense |
|---|---|---|
| MITM interception | Read or alter agent traffic | TLS 1.3 + mTLS |
| Agent impersonation | Rogue controller joins network | X.509 certificates |
| Message tampering | Modify legitimate commands | RSA-PSS signatures |
| Replay attack | Reuse previously valid messages | Nonce + timestamp |
| Message redirection | Misroute legitimate commands | Signed metadata |
| Emergency spoofing | Fraudulent priority request | Cryptographic authorization |

---

## 🛡️ Defense in Depth

```text
┌─────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                   │
│       Emergency Vehicle Authorization               │
├─────────────────────────────────────────────────────┤
│                    MESSAGE LAYER                    │
│      RSA-PSS • SHA-256 • Nonce • Timestamp          │
├─────────────────────────────────────────────────────┤
│                    IDENTITY LAYER                   │
│          X.509 PKI • Agent Certificates             │
├─────────────────────────────────────────────────────┤
│                   TRANSPORT LAYER                   │
│                TLS 1.3 Mutual TLS                   │
└─────────────────────────────────────────────────────┘
```

### Security Modules

| Module | Responsibility |
|---|---|
| `crypto_utils.py` | RSA-2048, SHA-256 and RSA-PSS primitives |
| `pki.py` | Certificate authority and per-agent X.509 certificates |
| `secure_message.py` | Signed, timestamped and nonced message envelopes |
| `secure_channel.py` | TLS 1.3 mutual-authentication channel |
| `emergency_auth.py` | Emergency-vehicle authorization |
| `secure_agent.py` | Security integration with traffic agents |
| `attack_simulator.py` | Executable adversarial scenarios |

For the detailed threat model and security architecture, see [`SECURITY.md`](./SECURITY.md).

---

## ⚔️ Adversarial Validation

The security architecture is backed by executable tests rather than documentation alone.

### Automated Security Tests

```bash
python -m pytest -v tests/test_security.py
```

**17 tests** exercise authentication, integrity validation, replay protection, certificate handling, and emergency authorization.

### Attack Simulation

```bash
python demo.py
```

Six adversarial scenarios are exercised:

| Attack | Result |
|---|:---:|
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

The smoke test validates the TLS 1.3 mutual-authentication path between simulated traffic-system participants.

---

# 📊 Simulation Evaluation

The adaptive system was compared with the project's rule-based traffic-control baseline.

| Metric | Rule-Based | Adaptive System | Change |
|---|---:|---:|---:|
| Average waiting time | 55 s | 32 s | **↓ 41.8%** |
| Queue length | 30 vehicles | 15 vehicles | **↓ 50.0%** |
| Fuel consumption | 120 L | 90 L | **↓ 25.0%** |
| Traffic throughput | 65% | 82% | **↑ 17 percentage points** |

The measurements were obtained from the project's simulation study.

They demonstrate the behaviour of the system under the evaluated SUMO configuration and should not be interpreted as expected performance on a real road network.

---

# 🛠️ Technology Stack

| Area | Technologies |
|---|---|
| Traffic Simulation | SUMO, TraCI |
| Adaptive Control | Multi-Agent Learning |
| Traffic Forecasting | LSTM, TensorFlow/Keras |
| Core Development | Python, NumPy |
| Cryptography | RSA-2048, RSA-PSS, SHA-256 |
| Identity | X.509 PKI |
| Transport Security | TLS 1.3, mTLS |
| Testing | Pytest |
| Evaluation | CSV-based simulation metrics |

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

# 🚀 Running the Project

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

### Run Traffic Simulation

```bash
python run_marl_agent.py
```

### Run the Security-Enabled Simulation

Generate agent PKI material:

```bash
python generate_keys.py --agents J1 J2 J3 J4
```

Then run:

```bash
python run_secure_marl_agent.py
```

### Generate Evaluation Data

```bash
python csv_gen.py
```

### Validate the Security Layer

```bash
python -m pytest -v tests/test_security.py
python demo.py
python tls_smoke_test.py
```

---

# 🔬 Engineering Focus

### Multi-Agent Decision Making

Models intersections as independent decision-making agents operating within a shared traffic environment.

### Adaptive Signal Control

Adjusts traffic-light behaviour from observed traffic conditions rather than relying exclusively on fixed schedules.

### Temporal Traffic Modelling

Uses LSTM-based forecasting to represent changing traffic demand in simulation.

### Emergency-Aware Control

Incorporates emergency-vehicle priority alongside general congestion objectives.

### Secure Agent Communication

Combines authenticated identities, encrypted transport, signed messages, and replay protection for inter-agent communication.

### Adversarial Testing

Exercises security assumptions through executable attack scenarios covering tampering, replay, impersonation, MITM behaviour, and emergency-priority abuse.

---

# 🚀 Future Work

- Evaluate larger multi-intersection networks
- Compare independent and cooperative MARL policies
- Integrate real-world traffic sensor data
- Add camera-based vehicle detection
- Explore federated training across traffic regions
- Deploy intersection agents to edge devices
- Investigate adaptive vehicle routing
- Evaluate city-scale traffic networks
- Explore post-quantum authentication mechanisms

---

# ⚠️ Project Scope

This repository is a **research and simulation project**.

Traffic-performance measurements were obtained from SUMO experiments and do not represent deployment results from a real municipal transportation network.

The security components demonstrate defensive mechanisms within the simulated multi-agent environment and are not presented as a certified production ITS security implementation.

---

## 👩‍💻 Author

**Agrima Saxena**  
B.Tech — Computer & Communication Engineering  
Manipal University Jaipur

---

### ⭐ Interested in the project?

Explore the implementation, reproduce the simulation experiments, review the security model, or open an issue with an improvement.