# MARL Driven Real-Time Traffic Management System

An intelligent traffic optimization system that uses **Multi-Agent Reinforcement Learning (MARL)**, **LSTM traffic prediction**, and **SUMO simulation** to dynamically control urban traffic signals, reduce congestion, and improve traffic throughput.  
Developed as a research-driven project focused on scalable smart city traffic control.

---

## Problem Statement

Traditional fixed-time traffic signals cannot adapt to real-time congestion, causing:

- Long vehicle waiting times  
- Increased queue lengths  
- Fuel wastage and emissions  
- Poor intersection coordination  
- Delayed emergency vehicle movement  

This project solves this by enabling **traffic lights to act as intelligent learning agents** that adapt signal timings in real time.

---

# Proposed Solution

This system combines:

### 1. Traffic Flow Prediction (LSTM)
- Predicts dynamic vehicle arrivals
- Simulates realistic traffic demand
- Supports proactive signal control

### 2. Multi-Agent Reinforcement Learning (MARL)
Each intersection acts as an autonomous RL agent that learns optimal signaling based on:

- Queue Length
- Waiting Time
- Traffic Density
- Emergency Vehicle Presence

Agents coordinate to optimize city-wide flow.

### 3. SUMO Simulation + TraCI
- Realistic urban traffic simulation
- Real-time traffic light control
- Agent-environment interaction

### 4. Emergency Vehicle Prioritization
- Dynamic signal adaptation for emergency clearance
- Priority routing logic

---

# Cybersecurity Layer (Novel Contribution)

Beyond traffic optimization, the project incorporates a working cybersecurity layer that secures intelligent transportation infrastructure from malicious attacks. The security claims below are backed by a test suite that actively demonstrates each defense.

## Threats Addressed

Modern smart traffic systems are vulnerable to:

- Man-in-the-Middle (MITM) attacks on signal communication  
- Signal spoofing / false traffic data injection  
- Replay attacks on signal phase commands  
- Agent impersonation across the network  
- Emergency vehicle priority abuse  
- Forged emergency dispatch tokens  

## Security Architecture

The defense is layered (defense-in-depth):

| Layer | Component | Protects Against |
|---|---|---|
| Transport | TLS 1.3 mTLS (AES-256-GCM) | Eavesdropping, MITM interception |
| Identity | X.509 PKI (self-signed CA + per-agent certs) | Agent impersonation |
| Message | RSA-PSS signatures + SHA-256 + nonce + timestamp | Tampering, replay, misrouting |
| Application | EDA-signed emergency tokens | Priority abuse, token theft |

## Implementation

Full source in the `security/` package:

- `crypto_utils.py` — RSA-2048, SHA-256, RSA-PSS signing primitives  
- `pki.py` — Self-signed CA issuing per-agent X.509 certificates  
- `secure_message.py` — Signed + timestamped + nonced message envelope  
- `secure_channel.py` — TLS 1.3 mTLS socket wrapper  
- `emergency_auth.py` — Cryptographic emergency-vehicle tokens  
- `secure_agent.py` — Integrates the above with `TrafficSignalAgent`  
- `attack_simulator.py` — Six adversarial scenarios demonstrating blocked attacks  

See [`SECURITY.md`](./SECURITY.md) for the full STRIDE threat model and defense-in-depth architecture.

## Verify Defenses

```bash
pip install cryptography pytest

# Run 17 unit tests covering every security property
python -m pytest -v tests/test_security.py

# Run 6 adversarial attack scenarios
python demo.py

# Verify live TLS 1.3 mTLS handshake
python tls_smoke_test.py
```

All six attack scenarios (tampering, impersonation, replay, MITM redirection, emergency spoofing, forged token) are blocked by the security layer.

---

# System Architecture

```text
Traffic Data
   ↓
LSTM Prediction
   ↓
Dynamic Vehicle Insertion in SUMO
   ↓
MARL Agents at Intersections
   ↓
Adaptive Signal Optimization
   ↓
Reduced Congestion + Higher Throughput
```

---

# Tech Stack

- Python
- SUMO
- TraCI
- Multi-Agent Reinforcement Learning
- PPO / DQN concepts
- TensorFlow / Keras (LSTM)
- NumPy
- Cryptography (RSA, SHA-256, X.509, TLS 1.3)
- XML + CSV Analysis

---

# Project Structure

```bash
├── marl_agent.py                 # Traffic signal MARL agent
├── run_marl_agent.py             # Simulation runner (baseline)
├── run_secure_marl_agent.py      # Simulation runner with security layer
├── csv_gen.py                    # Extract performance metrics
├── final2.sumocfg                # SUMO simulation config
├── fixed_timing_results.csv      # Baseline traffic results
├── Marl_timing_results.csv       # MARL performance results
├── generate_keys.py              # PKI bootstrap (CA + agent certs)
├── demo.py                       # Attack-blocking demonstration
├── tls_smoke_test.py             # Live TLS 1.3 mTLS handshake test
├── security/                     # Cybersecurity layer package
│   ├── crypto_utils.py
│   ├── pki.py
│   ├── secure_message.py
│   ├── secure_channel.py
│   ├── emergency_auth.py
│   ├── secure_agent.py
│   └── attack_simulator.py
├── tests/
│   └── test_security.py          # 17 unit tests for security properties
├── SECURITY.md                   # STRIDE threat model + architecture
└── README.md
```

---

# Reinforcement Learning Formulation

## State Space
Each agent observes:

- Queue length
- Vehicle waiting time
- Traffic density
- Emergency vehicle presence

## Actions
Agent selects signal phase changes dynamically.

## Reward Function
Optimizes:

- Lower congestion
- Reduced waiting time
- Higher throughput
- Emergency prioritization

Example reward logic implemented in code:

```python
reward = -(queue_length + 0.5 * waiting_time)
```

---

# Results

Compared with rule-based traffic control:

| Metric | Traditional | MARL System |
|--------|-------------|-------------|
| Average Waiting Time | 55 sec | 32 sec |
| Queue Length | 30 vehicles | 15 vehicles |
| Fuel Consumption | 120 L | 90 L |
| Traffic Throughput | 65% | 82% |

### Improvements
✅ Reduced congestion  
✅ Lower delay  
✅ Improved throughput  
✅ Better emergency handling  

Results derived from simulation study in report.

---

# Running the Project

## Install dependencies

```bash
pip install numpy traci cryptography pytest
```

Install SUMO: https://www.eclipse.org/sumo/

---

## Run Baseline Simulation

```bash
python run_marl_agent.py
```

## Run Simulation with Security Layer

```bash
# One-time setup: generate PKI keys for your traffic lights
python generate_keys.py --agents J1 J2 J3 J4

# Run secure simulation
python run_secure_marl_agent.py
```

## Generate Performance CSV

```bash
python csv_gen.py
```

---

# Research Contributions

This project addresses challenging problems in:

- Multi-agent coordination
- Real-time adaptive control
- Multi-objective optimization
- Intelligent transportation systems
- AI for Smart Cities

## Key Contributions

- Hybrid LSTM + MARL traffic optimization
- Multi-agent adaptive signal coordination
- Emergency vehicle prioritization with cryptographic authentication
- Cybersecure inter-agent communication using TLS 1.3 + RSA-PSS + SHA-256
- Protection against tampering, replay, impersonation, MITM, and emergency-priority abuse
- Test-verified security layer: 17 unit tests + 6 attack-blocking scenarios

---

# Future Work

- Real-world sensor integration
- Computer vision traffic detection
- Federated multi-city training
- Edge deployment
- Smart route recommendation
- Large-scale city traffic optimization
- Post-quantum signature migration (Dilithium / Kyber)

---

# Author

Agrima  
B.Tech Computer & Communication Engineering  
Manipal University Jaipur

---

## If you found this interesting
Star the repository and feel free to contribute.